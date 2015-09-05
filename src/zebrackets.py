#!/usr/bin/python3

# Copyright (c) John Plaice, 2015
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

import copy
import fileinput
import glob
import io
import math
import os
import re
import shutil
import subprocess
import sys

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
                string = "echo tex line = " + str(w.denominator) + " >> zetex.log"
                os.system(string)
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
                        string = "echo wsaved.count = " + str(wsaved.count) + " >> zetex.log"
                        numerator = wsaved.count
                    else:
                        string = "echo wsaved.stack[wsaved.depth]+1 = " + str(wsaved.stack[wsaved.depth]+1) + " >> zetex.log"
                        numerator = wsaved.stack[wsaved.depth] + 1
                elif params.numerator == -2:     # depth
                    if endIsLeft:
                        string = "echo wsaved.depth+1 = " + str(wsaved.depth+1) + " >> zetex.log"
                        numerator = wsaved.depth -1
                    else:
                        string = "echo wsaved.depth = " + str(wsaved.depth) + " >> zetex.log"
                        numerator = wsaved.depth
                elif params.numerator == -3:     # breadth
                    string = "echo wsaved.index = " + str(wsaved.index) + " >> zetex.log"
                    numerator = wsaved.index
                else:                            # manual numerator
                    string = "echo params.numerator = " + str(params.numerator) + " >> zetex.log"
                    numerator = params.numerator
                os.system(string)
                string = "echo numerator = " + str(numerator) + " >> zetex.log"
                os.system(string)
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
                font = copy.copy(params)
                font.kind = w.kind
                font.denominator = w.denominator
                font.stripes = font.denominator
                font.stripesAsLetter = chr(ord('a') + font.stripes)
                font.mag = 1.0
                font.generateFont()

# FontParameters is now almost obsolete.
#class FontParameters:
#    def __init__(self, kind, style, denominator, ptSize, typeFamily, mag, texmfHome):
#        if len(kind) == 0 or 'bp'.find(kind[0]) == -1:
#            # Invalid kind
#            return false
#        self.kind = kind[0]
#
#        if len(style) == 0 or 'bfh'.find(style[0]) == -1:
#            # Invalid style
#            return false
#        self.style = style[0]
#
#        if denominator < 0 or denominator > 7:
#            # Invalid number of stripes
#            return false
#        self.stripes = denominator
#        self.stripesAsLetter = chr(ord('a') + self.stripes)
#
#        self.ptSize = ptSize
#        self.typeFamily = typeFamily
#        self.mag = mag
#        self.texmfHome = texmfHome


# TODO: Document
class Params:
    def __init__(self, texmfHome):
        self.valueToFunctions = {
            'b' : (lambda value : value % 256),
            'u' : (lambda value : pow(2, (value % 8)) - 1),
            'd' : (lambda value : pow(2, value % 7))
        }
        self.valueFromFunctions = {
            'b' : (lambda value : int(math.ceil(math.log(value, 2)))),
            'u' : (lambda value : value - 1),
            'd' : (lambda value : value)
        }
        # TODO: Explain kind, encoding, index, style
        self.kind = 'p'
        self.encoding = 'b'
        self.index = -1 # 'd'
        self.style = 'b'
        self.valueToEncoding = self.valueToFunctions[self.encoding]
        self.valueFromEncoding = self.valueFromFunctions[self.encoding]
        # TODO: Explain numerator, denominator, stripes
        self.kind = 'p'
        self.numerator = ''
        self.denominator = ''
        #self.stripes = ''
        #self.stripesAsLetter = chr(ord('a') + self.stripes)
        # TODO: Explain ptSize, mag, typeFamily
        self.ptSize = 10.0
        self.mag = 1.0
        self.typeFamily = 'cmr'
        self.filterMode = False
        self.texmfHome = texmfHome

    def setStyle(self, args):
        m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
        if m:
            style = m.group(1)
            if len(style) == 0 or 'bfh'.find(style[0]) == -1:
                # TODO: Replace with exception
                sys.exit('Invalid style')
            self.style = style[0]

    def setNumerator(self, args):
        m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
        if m:
            numerator = m.group(1)
            # An exception might be raised here
            self.numerator = int(numerator)

    def setDenominator(self, args):
        m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
        if m:
            denominator = m.group(1)
            # An exception might be raised here
            self.denominator = int(denominator)

    def checkNumeratorDenominator(self):
        if self.numerator == '':
            self.numerator = self.index
        if self.denominator == '':
            self.denominator = -1
        if self.numerator < 0:
            if self.numerator < -3:
                # TODO: Replace with exception
                sys.exit('Invalid numerator')
        #elif self.denominator < 0 or self.denominator > 7:
        #    # TODO: Replace with exception
        #    sys.exit('Invalid denominator: (' + str(self.denominator) + ')')

    def setEncoding(self, args):
        m = re.search(r'enc\w*=(\w+)[,\]]', args)
        if m:
            encoding = m.group(1)
            if len(encoding) == 0 or 'bud'.find(encoding[0]) == -1:
                # TODO: Replace with exception
                sys.exit('Invalid encoding')
            self.encoding = encoding[0]
            self.valueToEncoding = self.valueToFunctions[self.encoding]
            self.valueFromEncoding = self.valueFromFunctions[self.encoding]

    def setPointSize(self, args):
        m = re.search(r'siz\w*=(\d+)[,\]]', args)
        if m:
            ptSize = m.group(1)
            ptSize = float(ptSize)
            if ptSize <= 0:
                # TODO: Replace with exception
                sys.exit('Invalid point size')
            self.ptSize = ptSize

    def setTypeFamily(self, args):
        m = re.search(r'fam\w*=(\w+)[,\]]', args)
        if m:
            self.typeFamily = m.group(1)

    def setStripes(self, args):
        m = re.search(r'str\w*=(\d+)[,\]]', args)
        if m:
            self.stripes = int(m.group(1))
            self.stripesAsLetter = chr(ord('a') + self.stripes)
        # default ?

    def setKind(self, args):
        m = re.search(r'typ\w*=([bp])\w+[,\]]', args)
        if m:
            kind = m.group(1)
            if len(kind) == 0 or 'bp'.find(kind[0]) == -1:
                # TODO: Replace with exception
                sys.exit('Invalid type')
            self.kind = kind[0]

    def setMagnification(self, args):
        m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
        if m:
            mag = m.group(1)
            self.mag = math.sqrt(float(mag))

    def setIndex(self, args):
        m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
        if m:
            index = m.group(1)
            if (index == 'b'):
                self.index = -3
            elif (index == 'd'):
                self.index = -2
            else:
                self.index = -1
        string = "echo setIndex = " + str(self.index) + " >> zetex.log"
        os.system(string)

    def setDefaults(self, args):
        self.setStyle(args)
        self.setNumerator(args)
        self.setDenominator(args)
        self.checkNumeratorDenominator()
        self.setEncoding(args)
        self.setPointSize(args)
        self.setTypeFamily(args)
        self.setStripes(args)
        self.setKind(args)
        self.setMagnification(args)
        self.setIndex(args)

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
        except OSError:
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
    def generateFont(self):
        #self.stripes = self.denominator
        #self.stripesAsLetter = chr(ord('a') + self.stripes)
        string = "echo denominator = " + str(self.denominator) + " >> zetex.log"
        os.system(string)
        string = "echo denominator = " + str(self.stripes) + " >> zetex.log"
        os.system(string)
        string = "echo stripesAsLetter = " + self.stripesAsLetter + " >> zetex.log"
        os.system(string)
        #fontParams = FontParameters(kind, style, denominator,
        #                            ptSize, typeFamily, mag, texmfHome)
        self.createMFfiles()

    # TODO: Document
    def zebracketsFilter(self, inputToFilter):
        #if not self.checkParams():
        #   self.buf.write(inputToFilter)
        #   return
        delims = DelimiterDictionary(dict(bracket = Delimiter('b', '[', ']'),
                                          parenthesis = Delimiter('p', '(', ')')))
        delims.countDelimiters(self, inputToFilter)
        delims.printDeclarations(self)
        string = "echo zebracketsFilter numerator = " + str(self.numerator) + " >> zetex.log"
        os.system(string)
        delims.printAndReplaceSymbols(self, inputToFilter)
        delims.generateFiles(self)

    # TODO: Document
    def declareFont(self, args):
        font = copy.copy(self)
        font.setKind(args)
        font.setStyle(args)
        # TODO: Stripes are still not properly initialized.
        font.setStripes(args)
        font.setPointSize(args)
        font.setTypeFamily(args)
        font.setMagnification(args)
        font.generateFont()
        #generateFont(kind, style, int(stripes), float(size), typeFamily, float(mag))

    # TODO: Document
    def beginZebrackets(self, args):
        string = "echo entering beginZebrackets >> zetex.log"
        os.system(string)
        self = copy.copy(self)
        self.setStyle(args)
        self.setIndex(args)
        self.setNumerator(args)
        self.setDenominator(args)
        # TODO: This is probably no longer necessary
        if self.numerator == '':
            self.numerator = self.index
        if self.denominator == '':
            self.denominator = -1
        self.checkNumeratorDenominator()
        self.setEncoding(args)
        self.setPointSize(args)
        self.setTypeFamily(args)
        self.setMagnification(args)
        self.filterMode = True
        self.buf = io.BytesIO()
        string = "echo leaving beginZebrackets >> zetex.log"
        os.system(string)
        return self

    # TODO: Document
    def endZebrackets(self):
        string = "echo entering endZebrackets >> zetex.log"
        os.system(string)
        inputToFilter = self.buf.getvalue()
        self.buf.close()
        self.buf = io.BytesIO()
        string = "echo endZebrackets numerator = " + str(self.numerator) + " >> zetex.log"
        os.system(string)
        self.zebracketsFilter(inputToFilter)
        outputFromFilter = self.buf.getvalue()
        self.buf.close()
        self.filterMode = False
        string = "echo leaving endZebrackets >> zetex.log"
        os.system(string)
        return outputFromFilter

    # TODO: Document
    def filterText(self, params):
        self.buf = io.BytesIO()
        params.filterMode = False
        #for line in sys.stdin:
        for line in fileinput.input():
            if not params.filterMode:
                m = re.search(r'^\\zebracketsdefaults(\[.*\])', line)
                if m:
                    params.setDefaults(m.group(1))
                    continue
                m = re.search(r'^\\zebracketsfont(\[.*\])', line)
                if m:
                    params.declareFont(m.group(1))
                    continue
                m = re.search(r'^\\begin{zebrackets}(\[.*])', line)
                if m:
                    params = params.beginZebrackets(m.group(1))
                    string = "echo after beginZebrackets " + str(params.filterMode) + " >> zetex.log"
                    os.system(string)
                    string = "echo after beginZebrackets numerator = " + str(params.numerator) + " >> zetex.log"
                    os.system(string)
                    
                    continue
                # Process a normal line
                self.buf.write(line)
            else:
                m = re.search(r'^\\end{zebrackets}', line)
                if m:
                    string = "echo filterText numerator = " + str(params.numerator) + " >> zetex.log"
                    os.system(string)
                    outputFromFilter = params.endZebrackets()
                    self.buf.write(outputFromFilter)
                    continue
                # Process a normal line
                params.buf.write(line)
        print(self.buf.getvalue())
        self.buf.close()

if __name__ == '__main__':
    if 'TEXMFHOME' not in os.environ:
       sys.exit('TEXMFHOME environment variable is not set')
    texmfHome = os.environ['TEXMFHOME']
    defaults = Params(texmfHome)
    params = copy.copy(defaults)
    defaults.filterText(params)
