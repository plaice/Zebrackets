#!/usr/bin/python3

# Copyright (c) John Plaice, 2005
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This filter is run on a region of text.
# Its arguments dictate translation of parentheses in the region.

import copy, glob, io, math, os, re, shutil, subprocess, sys

class FontParameters:
    def __init__(self, kind, style, denominator, ptSize, typeFamily, mag, texmfHome):
        if len(kind) == 0 or 'bp'.find(kind[0]) == -1:
            # Invalid kind
            return false
        self.kind = kind[0]

        if len(style) == 0 or 'bfh'.find(style[0]) == -1:
            # Invalid style
            return false
        self.style = style[0]

        if denominator < 0 or denominator > 7:
            # Invalid number of stripes
            return false
        self.stripes = denominator
        self.stripesAsLetter = chr(ord('a') + self.stripes)

        self.ptSize = ptSize
        self.typeFamily = typeFamily
        self.mag = mag
        self.texmfHome = texmfHome

    def callAndLog(self, args, log):
        try:
            proc = subprocess.Popen(args,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
            output = proc.stdout.read()
            if output != '':
                log.append(output)
        except subprocess.CalledProcessError:
            sys.exit('System died when calling {0}'.format(*args))
    
    def createMFcontent(self, sourceFont):
        styledict = { 'b' : '0', 'f' : '1',  'h' : '2' }
        text = '''% Copied from rtest on p.311 of the MetaFont book.
if unknown cmbase: input cmbase fi
mode_setup;
def generate suffix t = enddef;
input {0}; font_setup;
let iff = always_iff;
           
stripes:={1};
foreground:={2};
input zeroman{3};'''.format(sourceFont,
                            self.stripes,
                            styledict[self.style],
                            self.kind)
        return text
    
    def createMFfiles(self):
        sourceFont = '{0}{1}'.format(self.typeFamily, int(self.ptSize))
        destMFdir = '{0}/fonts/source/public/zetex'.format(self.texmfHome)
        destMF = 'z{0}{1}{2}{3}'.format(self.kind,
                                        self.style,
                                        self.stripesAsLetter,
                                        sourceFont)
        destMFpath = '{0}/{1}.mf'.format(destMFdir, destMF)
        textMFfile = self.createMFcontent(sourceFont)
    
        try:
            subprocess.check_output(['kpsewhich', '{0}.mf'.format(sourceFont)])
        except subprocess.CalledProcessError:
            sys.exit('File "{0}.mf" does not exist'.format(destMF))
    
        try:
            os.makedirs(destMFdir)
        except FileExistsError:
            pass
    
        try:
            subprocess.check_output(['kpsewhich', destMFpath])
        except subprocess.CalledProcessError:
            with open(destMFpath, 'w') as fileMF:
                fileMF.write(textMFfile)
    
        zetexFontsLog = []
        try:
            subprocess.check_output(['kpsewhich', '{0}.tfm'.format(destMF)])
        except subprocess.CalledProcessError:
            self.callAndLog(['mktextfm', destMF], zetexFontsLog)
            self.callAndLog(['mktexlsr', self.texmfHome], zetexFontsLog)
    
        if self.mag != 1.0:
            dpi = int(self.mag * self.mag * float(600) + .5)
            try:
                subprocess.check_output(['kpsewhich',
                                         '{0}.{1}pk'.format(destMF, dpi)])
            except subprocess.CalledProcessError:
                try:
                    proc = subprocess.Popen(['kpsewhich',
                                             '{0}.600pk'.format(destMF)],
                                            stdout=subprocess.PIPE,
                                            universal_newlines=True)
                except subprocess.CalledProcessError:
                    sys.exit('Could not find file {0}.600pk'.format(destMF))
                dpidir = re.sub('/[^/]*$', '', proc.stdout.read())
                self.callAndLog(['mf-nowin',
                                 '-progname=mf',
                                 '\\mode:=ljfour; mag:={0}; nonstopmode; input {1}'.
                                     format(self.mag, destMF)],
                           zetexFontsLog)
                self.callAndLog(['gftopk',
                                 '{0}.{1}gf'.format(destMF, dpi),
                                 '{0}.{1}pk'.format(destMF, dpi)],
                                 zetexFontsLog)
                shutil.move('{0}.{1}pk'.format(destMF, dpi), dpidir)
                self.callAndLog(['mktexlsr', self.texmfHome], zetexFontsLog)
                for file in glob.glob('{0}.*'.format(destMF)):
                    os.unlink(file)
    
        with open('zetexfonts.log', 'a') as zetexLogFile:
            for string in zetexFontsLog:
                zetexLogFile.write(string)
    
# TODO: Document
def generateFont(kind, style, denominator, ptSize, typeFamily, mag):
    fontParams = FontParameters(kind, style, denominator, ptSize, typeFamily, mag, texmfHome)
    fontParams.createMFfiles()

# TODO: Document
class Params:
    def __init__(self):
        self.style = ''
        self.numerator = ''
        self.denominator = ''
        self.encoding = ''
        self.ptSize = ''
        self.typeFamily = ''
        self.kind = ''
        self.stripes = ''
        self.index = ''
        self.mag = ''
        self.filterMode = False

    def checkParams(self):
        if len(self.style) == 0 or 'bfh'.find(self.style[0]) == -1:
            #sys.exit('Invalid style')
            return False

        self.numerator = int(self.numerator)
        self.denominator = int(self.denominator)
        if self.numerator < 0:
            if self.numerator < -3:
                #sys.exit('Invalid numerator')
                return False
        elif self.denominator < 0:
            #sys.exit('Invalid denominator')
            return False

        valueToFunctions = {
            'b' : (lambda value : value % 256),
            'u' : (lambda value : pow(2, (value % 8)) - 1),
            'd' : (lambda value : pow(2, value % 7)) }
        valueFromFunctions = {
            'b' : (lambda value : int(math.ceil(math.log(value, 2)))),
            'u' : (lambda value : value - 1),
            'd' : (lambda value : value) }
        if len(self.encoding) == 0 or 'bud'.find(self.encoding[0]) == -1:
            #sys.exit('Invalid encoding')
            return False
        self.valueToEncoding = valueToFunctions[self.encoding[0]]
        self.valueFromEncoding = valueFromFunctions[self.encoding[0]]

        self.ptSize = float(self.ptSize)
        if self.ptSize < 0:
            #sys.exit('Invalid point size')
            return False

        return True

# TODO: Document
class Delimiter:
    def __init__(self, _kind, _left, _right):
        self.kind = _kind
        self.left = _left
        self.right = _right
        self.count = 0
        self.index = 0
        self.depth = 0;
        self.used = False
        self.denominator = -1
        self.highestCount = 0
        self.deepestDepth = 0
        self.broadestBreadth = 0
        self.stack = [0 for level in range(64)]

class DelimiterDictionary:
    def __init__(self, _dictionary):
        self.dictionary = _dictionary

    # TODO: Document
    def countDelimiters(self, params, buf):
        # Go through the buffer and count the (opening) delimiters
        # in case the automatic stripe denominator is requested.
        for c in buf:
            for k, w in self.dictionary.items():
                if c == w.left:
                    w.used = True
                    w.count += 1
                    if w.highestCount < w.count:
                        w.highestCount = w.count
                    w.depth += 1
                    if w.depth > 63:
                        sys.exit('Depth is too greath (> 63)')
                    w.stack[w.depth] += 1
                    if w.deepestDepth < w.depth:
                        w.deepestDepth = w.depth
                    if w.broadestBreadth < w.stack[w.depth]:
                        w.broadestBreadth = w.stack[w.depth]
                elif c == w.right:
                    w.depth -= 1
    
        # Calculate all the denominators based upon the above tally.
        for k, w in self.dictionary.items():
            if w.used:
                if params.numerator == -1:   # automatic (default) mode
                   w.denominator = w.highestCount
                elif params.numerator == -2: # depth
                   w.denominator = w.deepestDepth
                elif params.numerator == -3: # breadth
                   w.denominator = w.broadestBreadth
                else:                        # manual numerator
                   w.denominator = params.denominator
                w.denominator = params.valueFromEncoding(w.denominator)
                if w.denominator > 7:
                    w.denominator = 7
    
    # TODO: Document
    def printDeclarations(self, params):
        for k, w in self.dictionary.items():
            if params.denominator != -1:
                w.denominator = params.denominator
            if w.used:
                fontName = 'z{0}{1}{2}{3}'.format(w.kind,
                                                  params.style,
                                                  chr(ord('a') + w.denominator),
                                                  params.typeFamily)
                params.buf.write('\\ifundefined{{{0}{1}}}\\newfont{{\\{0}{1}}}{{{0}{2}}}\\fi\n'.
                                 format(fontName,
                                        chr(ord('A') - 1 + int(params.ptSize)),
                                        int(params.ptSize)))
    
    # TODO: Document
    def printAndReplaceSymbols(self, params, inputBuffer):
        for k, w in self.dictionary.items():
           w.count = -1
           w.depth = 0
           for level in range(64):
               w.stack[level] = 0
    
        for c in inputBuffer:
            replace = False
            for k, w in self.dictionary.items():
                if c == w.left:
                    endIsLeft = True
                    w.stack[w.depth] = w.count
                    w.depth += 1
                    w.index = 1
                    w.count += 1
                elif c == w.right:
                    endIsLeft = False
                    w.index -= 1
                    w.depth -= 1
                else:
                    continue
                replace = True
                wsaved = w
                break
    
            if replace:
                if params.numerator == -1:       # automatic (default) mode
                    if endIsLeft:
                        numerator = wsaved.count
                    else:
                        numerator = wsaved.stack[wsaved.depth] + 1
                elif params.numerator == -2:     # depth
                    if endIsLeft:
                        numerator = wsaved.depth -1
                    else:
                        numerator = wsaved.depth
                elif params.numerator == -3:     # breadth
                    numerator = wsaved.index
                else:                            # manual numerator
                    numerator = params.numerator
                numerator = params.valueToEncoding(numerator)
                if not endIsLeft:
                    numerator += pow(2, wsaved.denominator)
    
                params.buf.write('{{\\z{0}{1}{2}{3}{4} \\symbol{{{5}}}}}'.
                                 format(wsaved.kind,
                                        params.style,
                                        chr(ord('a') + wsaved.denominator),
                                        params.typeFamily,
                                        chr(ord('A') - 1 + int(params.ptSize)),
                                        numerator))
            else:
                params.buf.write(c)
             
    # TODO: Document
    def generateFiles(self, params):
        for k, w in self.dictionary.items():
            if w.used:
                generateFont(w.kind,
                             params.style,
                             w.denominator,
                             params.ptSize,
                             params.typeFamily,
                             1.0)

# TODO: Document
def zebracketsFilter(params, inputToFilter):
    if not params.checkParams():
       params.buf.write(inputToFilter)
       return
    delims = DelimiterDictionary(dict(bracket = Delimiter('b', '[', ']'),
                                      parenthesis = Delimiter('p', '(', ')')))
    delims.countDelimiters(params, inputToFilter)
    delims.printDeclarations(params)
    delims.printAndReplaceSymbols(params, inputToFilter)
    delims.generateFiles(params)

# TODO: Document
def setDefaults(defaults, params, args):
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
    if m:
        defaults.style = m.group(1)
    m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
    if m:
        defaults.numerator = m.group(1)
    m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
    if m:
        defaults.denominator = m.group(1)
    m = re.search(r'enc\w*=(\w+)[,\]]', args)
    if m:
        defaults.encoding = m.group(1)
    m = re.search(r'siz\w*=(\d+)[,\]]', args)
    if m:
        defaults.ptSize = m.group(1)
    m = re.search(r'fam\w*=(\w+)[,\]]', args)
    if m:
        defaults.typeFamily = m.group(1)
    m = re.search(r'str\w*=(\d+)[,\]]', args)
    if m:
        defaults.stripes = m.group(1)
    m = re.search(r'typ\w*=([bp])\w+[,\]]', args)
    if m:
        defaults.kind = m.group(1)
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
    if m:
        defaults.mag = m.group(1)
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
    if m:
        defaults.index = m.group(1)
        if (defaults.index == 'b'):
            defaults.index = -3
        elif (defaults.index == 'd'):
            defaults.index = -2
        else:
            defaults.index = -1

# TODO: Document
def declareFont(defaults, params, args):
     m = re.search(r'typ\w*=([bp])\w*[,\]]', args)
     if m:
         kind = m.group(1)
     else:
         kind = defaults.kind
     m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
     if m:
         style = m.group(1)
     else:
         style = defaults.style
     m = re.search(r'str\w*=(\d+)[,\]]', args)
     if m:
         stripes = m.group(1)
     else:
         stripes = defaults.stripes
     m = re.search(r'siz\w*=(\d+)[,\]]', args)
     if m:
         size = m.group(1)
     else:
         size = defaults.ptSize
     m = re.search(r'fam\w*=(\w+)[,\]]', args)
     if m:
         typeFamily = m.group(1)
     else:
         typeFamily = defaults.typeFamily
     m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
     if m:
         mag = math.sqrt(float(m.group(1)))
     elif (defaults.mag != ''):
         mag = math.sqrt(float(defaults.mag))
     else:
         mag = 1.0
     generateFont(kind, style, int(stripes), float(size), typeFamily, float(mag))

# TODO: Document
def beginZebrackets(defaults, params, args):
     m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
     if m:
         params.style = m.group(1)
     else:
         params.style = defaults.style
     m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
     if m:
         params.index = m.group(1)
         if params.index == 'b':
             params.index = -3
         elif params.index == 'd':
             params.index = -2
         else:
             params.index = -1
     else:
         params.index = defaults.index
     m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
     if m:
         params.numerator = m.group(1)
     else:
         params.numerator = defaults.numerator
     m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
     if m:
         params.denominator = m.group(1)
     else:
         params.denominator = defaults.denominator
     m = re.search(r'enc\w*=(\w+)[,\]]', args)
     if m:
         params.encoding = m.group(1)
     else:
         params.encoding = defaults.encoding
     m = re.search(r'siz\w*=(\d+)[,\]]', args)
     if m:
         params.ptSize = m.group(1)
     else:
         params.ptSize = defaults.ptSize
     m = re.search(r'fam\w*=(\w+)[,\]]', args)
     if m:
         params.typeFamily = m.group(1)
     else:
         params.typeFamily = defaults.typeFamily
     m = re.search(r'mag\w*=(\w+)[,\]]', args)
     if m:
         params.mag = m.group(1)
     elif defaults.mag == '':
         params.mag = 1.0
     else:
         params.mag = defaults.mag
     if params.numerator == '':
         params.numerator = params.index
     if params.denominator == '':
         params.denominator = -1
     params.filterMode = True
     params.buf = io.StringIO()

# TODO: Document
def endZebrackets(defaults, params):
     inputToFilter = params.buf.getvalue()
     params.buf.close()
     params.buf = io.StringIO()
     zebracketsFilter(params, inputToFilter)
     defaults.buf.write(params.buf.getvalue())
     params.buf.close()
     params.filterMode = False

# TODO: Document
def filterText(defaults, params):
    defaults.buf = io.StringIO()
    params.filterMode = False
    for line in sys.stdin:
        if not params.filterMode:
            m = re.search(r'^\\zebracketsdefaults(\[.*\])', line)
            if m:
                setDefaults(defaults, params, m.group(1))
                continue
            m = re.search(r'^\\zebracketsfont(\[.*\])', line)
            if m:
                declareFont(defaults, params, m.group(1))
                continue
            m = re.search(r'^\\begin{zebrackets}(\[.*])', line)
            if m:
                beginZebrackets(defaults, params, m.group(1))
                continue
            # Process a normal line
            defaults.buf.write(line)
        else:
            m = re.search(r'^\\end{zebrackets}', line)
            if m:
                endZebrackets(defaults, params)
                continue
            # Process a normal line
            params.buf.write(line)
    print(defaults.buf.getvalue(), end='')
    defaults.buf.close()

if __name__ == '__main__':
    if 'TEXMFHOME' not in os.environ:
       sys.exit('TEXMFHOME environment variable is not set')
    texmfHome = os.environ['TEXMFHOME']
    scriptHome = texmfHome + '/scripts/zetex/python'

    defaults = Params()   
    params = copy.copy(defaults)
    filterText(defaults, params)
