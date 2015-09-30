#!/usr/bin/python3

# File zebraParser.py
#
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


# TODO: The manipulation of the parameters is now done.
#       It is now time to deal with the calling infrastructure.
#       Basically, from here, we call zebraFont or zebraFilter.
#       Could we put the code in this file, and not need
#       calling infrastructure?

'''This module takes as input three arguments: input file, output file and 
texmfhome directory. 
It parses the input file looking for zebrackets directives and handles them:
1. \zebracketsdefaults set the default zebrackets params for the entire document
2. \zebracketsfont modifies the default zebracket params and orders the
creation of the corresponding font in the texmfhome directory, if it does
not exist yet. 
3. \\begin{zebrackets} and \end{zebrackets} assume that the font has been 
created (should we check and throw an error if not created?), recreated the full
zebracket params based on default and the arguments given in the
\\begin{zebrackets} and output something... I think the font to be used in
this specific tex environment.
Now to stdout but it should go to a temporary file, the input of zebraFilter. 
'''

import copy
import io
import math
import os
import re
import subprocess  # Might not need if using files
import sys
import argparse
sys.path.append('/home/mancilla/development/Zebrackets/src')
from zebrackets import zebraFont
from zebrackets.zebraFilter import zebraFilter

# TODO: Document
class Params:
    def __init__(self):
        self.style = ''
        self.numerator = ''
        self.denominator = ''
        self.encoding = ''
        self.size = ''
        self.family = ''
        self.kind = ''
        self.stripes = ''
        self.index = ''
        self.mag = ''
        self.filterMode = False

doc_font_defaults = {
    'style': '',
    'numerator': '',
    'denominator': '',
    'encoding': '',
    'size': '',
    'family': '',
    'kind': '',
    'stripes': '',
    'index': '',
    'mag': '',
    'filterMode': False,
    }
## TODO: ask question
## Should the copy of doc_font_defaulst be done after running setDefaults?
## or rather, before each new parsing of fonts, should there be a copy made?
this_font_params = copy.copy(doc_font_defaults)


# TODO: Document
def setDefaults(defaults, params, args):
    ## No need for inputs except args. Others are global.
    '''This method sets the zebrackets default arguments for the entire
    document, based in the '\zebracketsdefaults' directive in the input file.
    Each subsequent occurrence of '\zebracketsFont' will modify the defaults
    to create a new font (in another method). 
    '''
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
    if m:
        doc_font_defaults['style'] = m.group(1)
    m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
    if m:
        doc_font_defaults['numerator'] = m.group(1)
    m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
    if m:
        doc_font_defaults['denominator'] = m.group(1)
    m = re.search(r'enc\w*=(\w+)[,\]]', args)
    if m:
        doc_font_defaults['encoding'] = m.group(1)
    m = re.search(r'siz\w*=(\d+)[,\]]', args)
    if m:
        doc_font_defaults['size'] = m.group(1)
    m = re.search(r'fam\w*=(\w+)[,\]]', args)
    if m:
        doc_font_defaults['family'] = m.group(1)
    m = re.search(r'str\w*=(\d+)[,\]]', args)
    if m:
        doc_font_defaults['stripes'] = m.group(1)
    m = re.search(r'typ\w*=([bp])\w+[,\]]', args)
    if m:
        doc_font_defaults['kind'] = m.group(1)
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
    if m:
        doc_font_defaults['mag'] = m.group(1)
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
    if m:
        doc_font_defaults['index'] = m.group(1)
        if (doc_font_defaults['index'] == 'b'):
            doc_font_defaults['index'] = -3
        elif (doc_font_defaults['index'] == 'd'):
            doc_font_defaults['index'] = -2
        else:
            doc_font_defaults['index'] = -1


# TODO: Document
def declareFont(defaults, params, args):
    ## No need for inputs except args. Others are global.
    '''This method is called everytime the directive '\zebracketsfont'
    is found in the input .zetex file. After the parsing of the values,
    the zebraFont module is called to create the corresponsing font file. 
    '''
    
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
        size = defaults.size
    m = re.search(r'fam\w*=(\w+)[,\]]', args)
    if m:
        family = m.group(1)
    else:
        family = defaults.family
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
    if m:
        mag = math.sqrt(float(m.group(1)))
    elif (doc_font_defaults['mag'] != ''):
        mag = math.sqrt(float(doc_font_defaults['mag']))
    else:
        mag = 1.0
    ''' postponing call to zebraFont until I know what is going on in the call

    zebraFont.zebraFont(
        kind,
        style,
        int(stripes),
        family,
        int(size),
        float(mag),
        texmfhome,
        False)
    '''

# TODO: Document
def beginZebrackets(defaults, params, args):
    ## defaults and params not needed they are global variables.
    '''This method parses the arguments to \\begin{zebrabrackets}
    '''
    this_font_params = copy.copy(doc_font_defaults)

    m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
    if m:
        this_font_params['style'] = m.group(1)
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
    if m:
        this_font_params['index'] = m.group(1)
        if this_font_params['index'] == 'b':
            this_font_params['index'] = -3
        elif this_font_params['index'] == 'd':
            this_font_params['index'] = -2
        else:
            this_font_params['index'] = -1
    m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
    if m:
        this_font_params['numerator'] = m.group(1)
    m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
    if m:
        this_font_params['denominator'] = m.group(1)
    m = re.search(r'enc\w*=(\w+)[,\]]', args)
    if m:
       this_font_params['encoding'] = m.group(1)
    m = re.search(r'siz\w*=(\d+)[,\]]', args)
    if m:
       this_font_params['size'] = m.group(1)
    m = re.search(r'fam\w*=(\w+)[,\]]', args)
    if m:
        this_font_params['family'] = m.group(1)
    m = re.search(r'mag\w*=(\w+)[,\]]', args)
    if m:
        this_font_params['mag'] = m.group(1)
    elif this_font_params['mag'] == '':
        this_font_params['mag'] = 1.0
    else:
        this_font_params['mag'] = defaults.mag
    if this_font_params['numerator'] == '':
        this_font_params['numerator'] = this_font_params['index']
    if this_font_params['denominator'] == '':
        this_font_params['denominator'] = -1
    this_font_params['filterMode'] = True
    this_font_params['buf'] = io.StringIO()

# TODO: Document
# TODO: How do we pass the input to this program?
def endZebrackets(defaults, params):
    ## defaults and params not needed they are global variables.
    string_tofilter = this_font_params['buf'].getvalue()
    string_filtered = zebraFilter(
        this_font_params['style'],
        this_font_params['encoding'][0],
        this_font_params['family'],
        str(this_font_params['size']),
        str(this_font_params['numerator']),
        str(this_font_params['denominator']),
        '/home/other/silly')
#        texmfhome)
    print(string_filtere)
    return



     
    proc = subprocess.Popen(['./zebraFilter.py',
                             params.style,
                             str(params.numerator),
                             str(params.denominator),
                             params.encoding[0],
                             str(params.size),
                             params.family],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    proc.stdin.write(string)
    proc.stdin.close()
    defaults.buf.write(proc.stdout.read())
    params.buf.close()
    params.filterMode = False

# TODO: Document
def filterText(defaults, params):
    ## No need for any input. These are global.
    '''This method parses the input file and captures all of the zebrackets
    directive, calls the corresponding method, and if necessary
    (zebracketsfont, zebracketsdefaults) supresses the line from the output.
    zebracketsdefaults only happens once.
    zebracketsfont could happen many times but at least once (?).
    '''

#    defaults.buf = io.StringIO() # this is now outfile
    this_font_params['filterMode'] = False
    for line in infile:
        if not this_font_params['filterMode']:
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
            ##defaults.buf.write(line)
            outfile.write(line)
        else:
            m = re.search(r'^\\end{zebrackets}', line)
            if m:
                endZebrackets(defaults, params)
                continue
            # Process a normal line
            ##params.buf.write(line)
            this_font_params['buf'].write(line)
    # No need for this one as the buffer was eliminated and now all we have is
    # writing directly to the output file. 
    ##print(defaults.buf.getvalue(), end='')
    # I moved this to be done at the main method.
    ##defaults.buf.close()


def zebraParser(in_file, out_file, texmfHome, checkArgs):
    '''Debating whether I should open the input and output as files in the
    argparse checking, or just grab the strings and check here if there are
    actual files. I might have more control of the opening and closing...
    '''
    global infile, outfile, texmfhome
    infile = in_file
    outfile = out_file
    print(infile, outfile)
    in_name = os.path.basename(in_file.name)
    in_base, in_ext = os.path.splitext(in_name)
    if in_ext != ".zetex":
        prt_str = "Invalid input file: zetex extension required."
        print(prt_str)
        return prt_str
    if texmfHome == None:
        if 'TEXMFHOME' not in os.environ:
            prt_str = 'TEXMFHOME environment variable is not set.'
            print(prt_str)
            return prt_str
        texmfHome = os.environ['TEXMFHOME']
    elif not os.path.isdir(texmfHome):
        prt_str = "Invalid texmf, path is not a directory."
        print(prt_str)
        return prt_str
    texmfhome = texmfHome
    if out_file == None:
        out_file_name = in_base + ".tex"
        outfile = open(out_file_name, 'w')
    print(infile.name, outfile.name)

    if checkArgs is False:
        print("Ok, here we go!")
#        defaults = Params()
#        params = copy.copy(defaults)
#        filterText(defaults, params)
        ## print(doc_font_defaults)
        ## print(this_font_params)
        filterText(doc_font_defaults, this_font_params)

def zebraParserParser(inputArguments = sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Handle zebrackets directives in input file.",
        epilog="This module is part of the zebrackets package.")
    parser.add_argument('--input', '-i', type=argparse.FileType('r'), 
        help='input file with extension .zetex',
        required=True)
    parser.add_argument('--output', '-o', type=argparse.FileType('w'), 
        help='output file name with extention .tex')
    parser.add_argument('--texmfhome', '-t', 
        help='substitute for variable TEXMFHOME')
    parser.add_argument('--checkargs', '-c', action='store_true',
        help='check validity of input arguments')

    args = parser.parse_args(inputArguments)
    return zebraParser(args.input, args.output, args.texmfhome, args.checkargs)

if __name__ == '__main__':
    zebraParserParser()
    print(infile.name, outfile.name)
    infile.close()
    outfile.close()
    print(infile.name, outfile.name)


#    if 'TEXMFHOME' not in os.environ:
#       sys.exit('TEXMFHOME environment variable is not set')
#    texmfHome = os.environ['TEXMFHOME']
#    scriptHome = texmfHome + '/scripts/zetex/python'

    
    # Need to close both input and output files
