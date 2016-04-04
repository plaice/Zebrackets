#!/usr/bin/python3

# File zebraParser.py
#
# Copyright (c) Blanca Mancilla, John Plaice, 2015, 2016
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

1. \zebracketsdefaults set the default zebrackets params for the entire
document.

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
import copy
import os
import re
import sys
import argparse
#sys.path.append('/home/mancilla/development/Zebrackets/src')
from zebrackets import zebraFont
from zebrackets import zebraHelp
from zebrackets.zebraFilter import zebraFilter

class Params:
    '''This init method should have a set of defaults. 
    '''
    def __init__(self):
        self.kind = 'p'
        self.style = 'h'
        self.slots = -1
        self.family = 'cmr'
        self.size = 10
        self.mag = 1

        self.index = 'd'
        self.encoding = 'b'
        self.number = -1
        self.mixcount = True
        self.mirror = False
        self.zerocount = True
        self.topcount = True

        self.filterMode = False

def setDefaults(params_doc_defaults, doc_args):
    '''This method sets the zebrackets default arguments for the entire
    document, based in the '\zebracketsdefaults' directive in the input
    zetex file.
    '''
    zebraHelp.check_kind(params_doc_defaults, doc_args)
    zebraHelp.check_style(params_doc_defaults, doc_args)
    zebraHelp.check_slots(params_doc_defaults, doc_args)
    zebraHelp.check_family(params_doc_defaults, doc_args)
    zebraHelp.check_size(params_doc_defaults, doc_args)
    zebraHelp.check_mag(params_doc_defaults, doc_args)
    zebraHelp.check_index(params_doc_defaults, doc_args)
    zebraHelp.check_encoding(params_doc_defaults, doc_args)
    zebraHelp.check_mixcount(params_doc_defaults, doc_args)
    zebraHelp.check_mirror(params_doc_defaults, doc_args)
    zebraHelp.check_topcount(params_doc_defaults, doc_args)
    zebraHelp.check_zerocount(params_doc_defaults, doc_args)


def declareFont(params_doc_defaults, font_args):
    '''This method is called everytime the directive '\zebracketsfont'
    is found in the input .zetex file. After the parsing of the values,
    the zebraFont module is called to create the corresponsing font file. 
    '''
    params_font = copy.copy(params_doc_defaults)

    zebraHelp.check_kind(params_font, font_args)
    zebraHelp.check_style(params_font, font_args)
    zebraHelp.check_slots(params_font, font_args)
    zebraHelp.check_family(params_font, font_args)
    zebraHelp.check_size(params_font, font_args)
    zebraHelp.check_mag(params_font, font_args)

    res = zebraFont.zebraFont(params_font.kind,
                              params_font.style,
                              params_font.slots,
                              params_font.family,
                              params_font.size,
                              params_font.mag,
                              params_doc_defaults.texmfHome,
                              False)
    if res.flag == False:
        print(res.result)

def replaceText(params_doc_defaults, params_paragraph, par_args,
                string_tofilter):
    '''This method parses the arguments in \\zebracketstext,
    modifies the params_paragraph accordingly, and calls zebraFilter.
    '''
    
    zebraHelp.check_style(params_paragraph, par_args)
    zebraHelp.check_family(params_paragraph, par_args)
    zebraHelp.check_size(params_paragraph, par_args)
    zebraHelp.check_mag(params_paragraph, par_args)
    zebraHelp.check_slots(params_paragraph, par_args)
    zebraHelp.check_index(params_paragraph, par_args)
    zebraHelp.check_encoding(params_paragraph, par_args)
    zebraHelp.check_number(params_paragraph, par_args)
    zebraHelp.check_mixcount(params_paragraph, par_args)
    zebraHelp.check_mirror(params_paragraph, par_args)
    zebraHelp.check_zerocount(params_paragraph, par_args)
    zebraHelp.check_topcount(params_paragraph, par_args)

    res = zebraFilter(params_paragraph.style,
                      params_paragraph.encoding,
                      params_paragraph.family,
                      params_paragraph.size,
                      params_paragraph.mag,
                      params_paragraph.number,
                      params_paragraph.slots,
                      params_paragraph.index,
                      params_paragraph.mixcount,
                      params_paragraph.zerocount,
                      params_paragraph.topcount,
                      params_doc_defaults.texmfHome,
                      string_tofilter)
    if res.flag == False:
        print(res.result)
        return ''
    else:
        return res.result


def beginZebrackets(params_doc_defaults, params_paragraph, par_args):
    '''This method parses the arguments in \\begin{zebrabrackets}
    and modifies the params_paragraph accordingly.
    '''
    params_paragraph.buf = io.StringIO()
    params_doc_defaults.filterMode = True

    zebraHelp.check_style(params_paragraph, par_args)
    zebraHelp.check_family(params_paragraph, par_args)
    zebraHelp.check_size(params_paragraph, par_args)
    zebraHelp.check_mag(params_paragraph, par_args)
    zebraHelp.check_slots(params_paragraph, par_args)
    zebraHelp.check_index(params_paragraph, par_args)
    zebraHelp.check_number(params_paragraph, par_args)
    zebraHelp.check_encoding(params_paragraph, par_args)
    zebraHelp.check_mixcount(params_paragraph, par_args)
    zebraHelp.check_mirror(params_paragraph, par_args)
    zebraHelp.check_zerocount(params_paragraph, par_args)
    zebraHelp.check_topcount(params_paragraph, par_args)


def endZebrackets(params_doc_defaults, params_paragraph):
    '''This method writes the buffer into the output file. The buffer has been
    accumulating the translation between normal parenthesis and zebrackets. 
    zebraFilter is called to replace the glyphs. 
    '''
    string_tofilter = params_paragraph.buf.getvalue()
    params_paragraph.buf.close()

    res = zebraFilter(params_paragraph.style,
                      params_paragraph.encoding,
                      params_paragraph.family,
                      params_paragraph.size,
                      params_paragraph.mag,
                      params_paragraph.number,
                      params_paragraph.slots,
                      params_paragraph.index,
                      params_paragraph.mixcount,
                      params_paragraph.zerocount,
                      params_paragraph.topcount,
                      params_doc_defaults.texmfHome,
                      string_tofilter)
    if res.flag == False:
        print(res.result)
    else:
        params_doc_defaults.outfile.write(res.result)
    params_doc_defaults.filterMode = False


def filterText(params_doc_defaults, params_paragraph):
    '''This method parses the input file and captures all of the zebrackets
    directive, calls the corresponding method, and if necessary, for
    zebracketsfont, zebracketsdefaults, supresses the line from the output.
    '''
    params_doc_defaults.filterMode = False
    for line in params_doc_defaults.infile:
        saveline = line
        if not params_doc_defaults.filterMode:
            m = re.search(r'^\\zebracketsdefaults(\[.*\])', line)
            if m:
                setDefaults(params_doc_defaults, m.group(1))
                if params_doc_defaults.mirror:
                    params_doc_defaults.outfile.write('%' + saveline)
                continue
            m = re.search(r'^\\zebracketsfont(\[.*\])', line)
            if m:
                declareFont(params_doc_defaults, m.group(1))
                if params_doc_defaults.mirror:
                    params_doc_defaults.outfile.write('%' + saveline)
                continue
            m = re.search(r'^\\begin{zebrackets}(\[.*])', line)
            if m:
                params_paragraph = copy.copy(params_doc_defaults)
                beginZebrackets(
                    params_doc_defaults,
                    params_paragraph,
                    m.group(1))
                if params_paragraph.mirror:
                    params_doc_defaults.outfile.write('%' + saveline)
                continue
            m = re.search(r'\\zebracketstext(\[.*\])({.*})', line)
            mirror_line = False
            while m:
                # Find the replacement text, then sub back into line
                params_paragraph = copy.copy(params_doc_defaults)
                new_text = replaceText(params_doc_defaults, params_paragraph,
                                       m.group(1), m.group(2))
                if params_paragraph.mirror:
                    mirror_line = True
                line = re.sub(r'\\zebracketstext\[.*\]{.*}',
                              repr(new_text).strip("'").rstrip("'"), line)
                m = re.search(r'\\zebracketstext(\[.*\])({.*})', line)
            # Process a normal line
            if mirror_line:
                params_doc_defaults.outfile.write('%' + saveline)
            params_doc_defaults.outfile.write(line)
        else:
            if params_paragraph.mirror:
                params_doc_defaults.outfile.write('%' + saveline)
            m = re.search(r'^\\end{zebrackets}', line)
            if m:
                endZebrackets(params_doc_defaults, params_paragraph)
                continue
            # Process a normal line
            params_paragraph.buf.write(line)


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
        return "Error: Invalid input file, zetex extension required."
    else:
        params_doc_defaults.infile = args.input

    # If no output file name is given, build it from the input file name.
    if args.output == None:
        out_file_name = in_base + ".tex"
        params_doc_defaults.outfile = open(out_file_name, 'w')
    else:
        params_doc_defaults.outfile = args.output

    # Looking for a valid TEXMFHOME
    params_doc_defaults.texmfHome = zebraHelp.validate_texmfhome(args.texmfhome)

    if args.checkargs is False:
        try:
            filterText(params_doc_defaults, params_paragraph)
            params_doc_defaults.infile.close()
            params_doc_defaults.outfile.close()
        except zebraHelp.ArgError as e:
            params_doc_defaults.infile.close()
            params_doc_defaults.outfile.close()
            print ('zebraParse ArgError: ' + e)

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
    zebraParser(args)

if __name__ == '__main__':
    zebraParserParser()
