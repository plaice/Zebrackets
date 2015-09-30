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

import copy        # Might need if using a dict instead of a class
import io          # Might not need if using files
import math
import os
import re
import subprocess  # Might not need if using files
import sys
import argparse
#import zebraFont
sys.path.append('/home/mancilla/development/Zebrackets/src')
from zebrackets import zebraFont

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

doc_defaults = {
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
this_font_params = copy.copy(doc_defaults)


# TODO: Document
def setDefaults(defaults, params, args):
    '''This method sets the zebrackets default arguments for the entire 
    document, based in the '\zebracketsdefaults' directive in the input file.
    Each subsequent occurrence of '\zebracketsFont' will modify the defaults
    to create a new font (in another method). 
    '''
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
        defaults.size = m.group(1)
    m = re.search(r'fam\w*=(\w+)[,\]]', args)
    if m:
        defaults.family = m.group(1)
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
    elif (defaults.mag != ''):
        mag = math.sqrt(float(defaults.mag))
    else:
        mag = 1.0
    zebraFont.zebraFont(
        kind,
        style,
        int(stripes),
        family,
        int(size),
        float(mag),
        texmfHome,
        False)


# TODO: Document
def beginZebrackets(defaults, params, args):
    '''This method parses the arguments to \\begin{zebrabrackets}
    '''
     m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
     if m:
         params.style = m.group(1)
     else:
         # We do not need this. That is why we have a copy made before.
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
         params.size = m.group(1)
     else:
         params.size = defaults.size
     m = re.search(r'fam\w*=(\w+)[,\]]', args)
     if m:
         params.family = m.group(1)
     else:
         params.family = defaults.family
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
     ## There should be a call to zebraFont here.
     ## What is filterMode for? 
     params.buf = io.StringIO()

# TODO: Document
# TODO: How do we pass the input to this program?
def endZebrackets(defaults, params):
#      system "cat /tmp/ze-sub_buf | $cbindir/zebrackets $style $numerator $denominator $encoding $size $family > /tmp/ze-sub_buf-out";
     string = params.buf.getvalue()
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
    '''This method parses the input file and captures all of the zebrackets
    directive, calls the corresponding method, and if necessary
    (zebracketsfont, zebracketsdefaults) supresses the line from the output.
    zebracketsdefaults only happens once.
    zebracketsfont could happen many times but at least once (?).
    '''

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


def zebraParser(in_file, out_file, texmfHome, checkArgs):
    '''Debating whether I should open the input and output as files in the
    argparse checking, or just grab the strings and check here if there are
    actual files. I might have more control of the opening and closing...
    '''
    global infile, outfile
    infile = in_file
    outfile = out_file
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
        prt_str = "Invalid textmf, path is not a directory."
        print(prt_str)
        return prt_str
    if out_file == None:
        out_file_name = in_name + ".tmp"

    if checkArgs is False:
        print("Ok, here we go!")
#        defaults = Params()   
#        params = copy.copy(defaults)
#        filterText(defaults, params)
        print(doc_defaults)
        print(font_params)
#        filterText(doc_defaults, font_params)
        

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
    infile.close()
    outfile.close()


#    if 'TEXMFHOME' not in os.environ:
#       sys.exit('TEXMFHOME environment variable is not set')
#    texmfHome = os.environ['TEXMFHOME']
#    scriptHome = texmfHome + '/scripts/zetex/python'

    
    # Need to close both input and output files
