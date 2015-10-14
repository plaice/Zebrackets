#!/usr/bin/python3

# File zebraParser.py
#
# Copyright (c) John Plaice and Blanca Mancilla, 2015
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


'''This module takes as input three arguments: input file, output file and 
texmfhome directory. 
It takes into consideration a region of text at a time and the arguments of
each region and the defaults, dictate translation of parentheses in the region.
The module parses the input file looking for zebrackets directives and
handles them:
1. \zebracketsdefaults set the default zebrackets params for the entire document
2. \zebracketsfont modifies the default zebracket params and orders the
creation of the corresponding font in the texmfhome directory, if it does
not exist yet. 
3. \begin{zebrackets} and \end{zebrackets} assume that the font has been 
created (should we check and throw an error if not created?). Using defaults
and block parameters, create the output having replaced normal parenthesis
with zebrackets.
'''

import io
import math
import os
import re
import sys
import argparse
sys.path.append('/home/mancilla/development/Zebrackets/src')
from zebrackets import zebraFont
from zebrackets import zebraHelp
from zebrackets.zebraFilter import zebraFilter

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

def setDefaults(params_doc_defaults, params_paragraph, doc_args):
    '''This method sets the zebrackets default arguments for the entire
    document, based in the '\zebracketsdefaults' directive in the input
    zetex file.
    '''
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', doc_args)
    if m:
        params_doc_defaults.style = m.group(1)
    m = re.search(r'num\w*=([-]?\d+)[,\]]', doc_args)
    if m:
        params_doc_defaults.numerator = m.group(1)
    m = re.search(r'den\w*=([-]?\d+)[,\]]', doc_args)
    if m:
        params_doc_defaults.denominator = m.group(1)
    m = re.search(r'enc\w*=(\w+)[,\]]', doc_args)
    if m:
        params_doc_defaults.encoding = m.group(1)
    m = re.search(r'siz\w*=(\d+)[,\]]', doc_args)
    if m:
        params_doc_defaults.size = m.group(1)
    m = re.search(r'fam\w*=(\w+)[,\]]', doc_args)
    if m:
        params_doc_defaults.family = m.group(1)
    m = re.search(r'str\w*=(\d+)[,\]]', doc_args)
    if m:
        params_doc_defaults.stripes = m.group(1)
    m = re.search(r'typ\w*=([bp])\w+[,\]]', doc_args)
    if m:
        params_doc_defaults.kind = m.group(1)
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', doc_args)
    if m:
        params_doc_defaults.mag = m.group(1)
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', doc_args)
    if m:
        params_doc_defaults.index = m.group(1)
        if (params_doc_defaults.index == 'b'):
            params_doc_defaults.index = -3
        elif (params_doc_defaults.index == 'd'):
            params_doc_defaults.index = -2
        else:
            params_doc_defaults.index = -1


def declareFont(params_doc_defaults, params_paragraph, font_args):
    '''This method is called everytime the directive '\zebracketsfont'
    is found in the input .zetex file. After the parsing of the values,
    the zebraFont module is called to create the corresponsing font file. 
    '''
    m = re.search(r'typ\w*=([bp])\w*[,\]]', font_args)
    if m:
        kind = m.group(1)
    else:
        kind = params_doc_defaults.kind
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', font_args)
    if m:
        style = m.group(1)
    else:
        style = params_doc_defaults.style
    m = re.search(r'str\w*=(\d+)[,\]]', font_args)
    if m:
        stripes = m.group(1)
    else:
        stripes = params_doc_defaults.stripes
    m = re.search(r'siz\w*=(\d+)[,\]]', font_args)
    if m:
        size = m.group(1)
    else:
        size = params_doc_defaults.size
    m = re.search(r'fam\w*=(\w+)[,\]]', font_args)
    if m:
        family = m.group(1)
    else:
        family = params_doc_defaults.family
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', font_args)
    if m:
        mag = math.sqrt(float(m.group(1)))
    elif (params_doc_defaults.mag != ''):
        mag = math.sqrt(float(params_doc_defaults.mag))
    else:
        mag = 1.0

    zebraFont.zebraFont(
        kind,
        style,
        int(stripes),
        family,
        int(size),
        float(mag),
        params_doc_defaults.texmfHome,
        False)

def beginZebrackets(params_doc_defaults, params_paragraph, par_args):
    '''This method parses the arguments in \begin{zebrabrackets}
    and modifies the the params_paragraph accordingly.
    '''
    params_paragraph.buf = io.StringIO()
    params_paragraph.filterMode = True

    m = re.search(r'sty\w*=([bfh])\w*[,\]]', par_args)
    if m:
        params_paragraph.style = m.group(1)
    else:
        params_paragraph.style = params_doc_defaults.style
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', par_args)
    if m:
        params_paragraph.index = m.group(1)
        if params_paragraph.index == 'b':
            params_paragraph.index = -3
        elif params_paragraph.index == 'd':
            params_paragraph.index = -2
        else:
            params_paragraph.index = -1
    else:
        params_paragraph.index = params_doc_defaults.index
    m = re.search(r'num\w*=([-]?\d+)[,\]]', par_args)
    if m:
        params_paragraph.numerator = m.group(1)
    else:
        params_paragraph.numerator = params_doc_defaults.numerator
    m = re.search(r'den\w*=([-]?\d+)[,\]]', par_args)
    if m:
        params_paragraph.denominator = m.group(1)
    else:
        params_paragraph.denominator = params_doc_defaults.denominator
    m = re.search(r'enc\w*=(\w+)[,\]]', par_args)
    if m:
       params_paragraph.encoding = m.group(1)
    else:
        params_paragraph.encoding = params_doc_defaults.encoding
    m = re.search(r'siz\w*=(\d+)[,\]]', par_args)
    if m:
       params_paragraph.size = m.group(1)
    else:
        params_paragraph.size = params_doc_defaults.size
    m = re.search(r'fam\w*=(\w+)[,\]]', par_args)
    if m:
        params_paragraph.family = m.group(1)
    else:
        params_paragraph.family = params_doc_defaults.family
    m = re.search(r'mag\w*=(\w+)[,\]]', par_args)
    if m:
        params_paragraph.mag = m.group(1)
    elif params_paragraph.mag == '':
        params_paragraph.mag = 1.0
    else:
        params_paragraph.mag = params_doc_defaults.mag
    if params_paragraph.numerator == '':
        params_paragraph.numerator = params_paragraph.index
    if params_paragraph.denominator == '':
        params_paragraph.denominator = -1


def endZebrackets(params_doc_defaults, params_paragraph):
    '''This method writes the buffer into the output file. The buffer has been
    accumulating the translation between normal parenthesis and zebrackets. 
    zebraFilter is call to replace the glyphs. 
    '''
    string_tofilter = params_paragraph.buf.getvalue()
    params_paragraph.buf.close()

    string_filtered = zebraFilter(
        params_paragraph.style,
        params_paragraph.encoding[0],
        params_paragraph.family,
        int(params_paragraph.size),
        int(params_paragraph.numerator),
        int(params_paragraph.denominator),
        params_doc_defaults.texmfHome,
        string_tofilter,
        )
    ## Here we can check if the string_filtered contains an error message.
    ## If so, write to the log file and exit graciously.
    print(string_filtered)
    params_paragraph.filterMode = False
    params_doc_defaults.outfile.write(string_filtered)


def filterText(params_doc_defaults, params_paragraph):
    '''This method parses the input file and captures all of the zebrackets
    directive, calls the corresponding method, and if necessary, for
    zebracketsfont, zebracketsdefaults, supresses the line from the output.
    * zebracketsdefaults only happens once.
    * zebracketsfont could happen many times but at least once (?).
    '''
    params_paragraph.filterMode = False
    for line in params_doc_defaults.infile:
        if not params_paragraph.filterMode:
            m = re.search(r'^\\zebracketsdefaults(\[.*\])', line)
            if m:
                print("Going to setDefaults")
                setDefaults(params_doc_defaults, params_paragraph, m.group(1))
                continue
            m = re.search(r'^\\zebracketsfont(\[.*\])', line)
            if m:
                print("Going to declareFonts")
                declareFont(params_doc_defaults, params_paragraph, m.group(1))
                continue
            m = re.search(r'^\\begin{zebrackets}(\[.*])', line)
            if m:
                print("Going to beginZebrackets")
                beginZebrackets(params_doc_defaults, params_paragraph, m.group(1))
                continue
            # Process a normal line
            params_doc_defaults.outfile.write(line)
        else:
            m = re.search(r'^\\end{zebrackets}', line)
            if m:
                print("Going to endZebrackets")
                endZebrackets(params_doc_defaults, params_paragraph)
                continue
            # Process a normal line
            params_paragraph.buf.write(line)

    #params_paragraph.buf.close()
    #Not sure this is the correct place...
    ##defaults.buf.close()


def zebraParser(args):
    '''Final checking of the input arguments, checking if the file extensions
    conform with what is asked, and if the texmfhome is a valid path.
    '''
    params_doc_defaults = Params()
    params_paragraph = Params()

    # Assigning the input file if the input is correct
    in_name = os.path.basename(args.input.name)
    in_base, in_ext = os.path.splitext(in_name)
    if in_ext != ".zetex":
        prt_str = "Error: Invalid input file, zetex extension required."
        print(prt_str)
        return prt_str
    else:
        params_doc_defaults.infile = args.input

    # If not output file name is given, build it from the input file name.
    if args.output == None:
        out_file_name = in_base + ".tex"
        params_doc_defaults.outfile = open(out_file_name, 'w')
    else:
        params_doc_defaults.outfile = args.output

    # Looking for a valid TEXMFHOME
    try:
        params_doc_defaults.texmfHome = zebraHelp.check_texmfhome(args.texmfhome)
    except:
        print(params_doc_defaults.texmfHome)
        return params_doc_defaults.texmfHome

    if args.checkargs is False:
        print("Ok, here we go!")
        filterText(params_doc_defaults, params_paragraph)
        params_doc_defaults.infile.close()
        params_doc_defaults.outfile.close()

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
        help='substitute for environment variable TEXMFHOME')
    parser.add_argument('--checkargs', '-c', action='store_true',
        help='check validity of input arguments')

    args = parser.parse_args(inputArguments)
    print(args.input.name)
    print(args.output)
    print(args.texmfhome)
    print(args.checkargs)
    return zebraParser(args)

if __name__ == '__main__':
    zebraParserParser()
