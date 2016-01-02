#!/usr/bin/python3

# File zebraFilter.py
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

'''This filter is run on a region of text.
Its arguments dictate translation of parentheses in the region.
'''

import argparse
import math
import os
import io
import subprocess
import sys
from zebrackets.zebraFont import zebraFont
import zebraHelp

# TODO: Document
valueToFunctions = {
    'b' : (lambda value : value % 256),
    'u' : (lambda value : pow(2, (value % 8)) - 1),
    'd' : (lambda value : pow(2, (value - 1) % 7) if value else value) }

valueFromFunctions = {
    'b' : (lambda value : int(math.ceil(math.log(value, 2)))),
    'u' : (lambda value : value - 1),
    'd' : (lambda value : value - 1) }

# TODO: Document
class Delimiter:
    def __init__(self, kind, _left, _right):
        self.kind = kind
        self.left = _left
        self.right = _right
        self.count = 0
        self.depth = 0;
        self.breadth = 0
        self.used = False
        self.slots = -1
        self.highestCount = 0
        self.deepestDepth = 0
        self.broadestBreadth = 0
        self.stack = [0 for level in range(64)]

# TODO: Document
class Parameters:
    def __init__(self, style, encoding, fontFamily, fontSize,
            number, slots, index, texmfHome, checkArgs):
        if style not in zebraHelp.validStyles:
            raise zebraHelp.ArgError('Invalid style')
        if encoding not in zebraHelp.validEncodings:
            raise zebraHelp.ArgError('Invalid encoding')
        if fontFamily not in zebraHelp.validFontFamilies:
            raise zebraHelp.ArgError('Invalid Computer Modern font family')
        if fontSize not in zebraHelp.validFontSizes:
            raise zebraHelp.ArgError('Invalid font size')
        if fontSize not in zebraHelp.validFontPairs[fontFamily]:
            raise zebraHelp.ArgError('Invalid font family-size pair')
        if index == 'n':
            if number < 0:
                raise zebraHelp.ArgError('Invalid number')
        elif index not in zebraHelp.validIndices:
            raise zebraHelp.ArgError('Invalid index')
        
        texmfHome = zebraHelp.check_texmfhome(texmfHome)

        self.style = style
        self.encoding = encoding
        self.valueToEncoding = valueToFunctions[encoding]
        self.valueFromEncoding = valueFromFunctions[encoding]
        self.fontFamily = fontFamily
        self.fontSize = fontSize
        self.number = number
        self.slots = slots
        self.index = index
        self.texmfHome = texmfHome
        self.checkArgs = checkArgs


# TODO: Document
def countDelimiters(params, delims, buf):
    '''Go through the buffer and count the (opening) delimiters
    in case the automatic slots counter is requested.
    '''
    for c in buf:
        for k, w in delims.items():
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

    # Calculate all the slots based upon the above tally.
    for k, w in delims.items():
        if w.used:
            if params.index == 'u':   # unique (default) mode
               w.slots = w.highestCount
            elif params.index == 'd': # depth
               w.slots = w.deepestDepth
            elif params.index == 'b': # breadth
               w.slots = w.broadestBreadth
            else:                     # manual number
               w.slots = params.number
            w.slots = params.valueFromEncoding(w.slots)
            if w.slots > 7:
                w.slots = 7

# TODO: Document
def printDeclarations(params, delims, buf, out_string):
    for k, w in delims.items():
        if params.slots != -1:
            w.slots = params.slots
        if w.used:
            fontName = 'z{0}{1}{2}{3}'.format(
                w.kind,
                params.style,
                chr(ord('a') + w.slots),
                params.fontFamily
            )
            out_string.write(
                '\\ifundefined{{{0}{1}}}\\newfont{{\\{0}{1}}}{{{0}{2}}}\\fi'.
                    format(fontName,
                           chr(ord('A') - 1 + params.fontSize),
                           params.fontSize))

# TODO: Document
def printAndReplaceSymbols(params, delims, buf, out_string):
    for k, w in delims.items():
       w.count = -1
       w.depth = 0
       for level in range(64):
           w.stack[level] = -1

    for c in buf:
        replace = False
        for k, w in delims.items():
            if c == w.left:
                endIsLeft = True
                if params.index == 'u':       # unique (default) mode
                    w.stack[w.depth] = w.count
                else:
                    w.stack[w.depth] += 1
                w.breadth = w.stack[w.depth]
                w.depth += 1
                w.count += 1
            elif c == w.right:
                endIsLeft = False
                w.depth -= 1
                w.breadth = w.stack[w.depth]
            else:
                continue
            replace = True
            wsaved = w
            break

        if replace:
            if params.number != -1:
                number = params.number
            elif params.index == 'u':       # unique (default) mode
                if endIsLeft:
                    number = wsaved.count
                else:
                    number = wsaved.stack[wsaved.depth] + 1
            elif params.index == 'd':     # depth
                if endIsLeft:
                    number = wsaved.depth - 1
                else:
                    number = wsaved.depth
            else: #params.index == 'b'     # breadth
                number = wsaved.breadth
            number = params.valueToEncoding(number)
            if not endIsLeft:
                number += pow(2, wsaved.slots)

            out_string.write('{{\\z{0}{1}{2}{3}{4} \\symbol{{{5}}}}}'.
                  format(wsaved.kind,
                         params.style,
                         chr(ord('a') + wsaved.slots),
                         params.fontFamily,
                         chr(ord('A') - 1 + params.fontSize),
                         number))
        else:
            out_string.write(c)
         
# TODO: Document
def generateFiles(params, delims, buf):
    for k, w in delims.items():
        if w.used:
            zebraFont(
                w.kind,
                params.style,
                w.slots,
                params.fontFamily,
                params.fontSize,
                1,
                params.texmfHome,
                False)

def zebraFilter(style, encoding, fontFamily, fontSize,
        number, slots, index, texmfHome, string_tofilter, 
        checkArgs=False):
    print('zebraFilter: ',
          'style', style, 'encoding', encoding,
          'fontFamily', fontFamily, 'fontSize', fontSize,
          'number', number, 'slots', slots,
          'index', index, 'texmfHome', texmfHome,
          'string_to_filter', string_tofilter)

    try:
        parameters = Parameters(style, encoding, fontFamily, fontSize,
                         number, slots, index, texmfHome, checkArgs)
        if checkArgs is False:
            out_string = io.StringIO()
            delimiters = dict(bracket = Delimiter('b', '[', ']'),
                              parenthesis = Delimiter('p', '(', ')'))
            countDelimiters(parameters, delimiters, string_tofilter)
            printDeclarations(
                parameters,
                delimiters,
                string_tofilter,
                out_string)
            printAndReplaceSymbols(
                parameters,
                delimiters,
                string_tofilter,
                out_string)
            generateFiles(parameters, delimiters, string_tofilter)
            value =  out_string.getvalue()
            out_string.close()
            return value

    except zebraHelp.ArgError as e:
        print('Invalid input:', e.value)

def zebraFilterParser(inputArguments = sys.argv[1:]):
    parser = argparse.ArgumentParser(
                 description='Replace brackets by zebrackets in a text.')
    parser.add_argument('--style', type=str, choices=zebraHelp.validStyles,
        required=True, help='b = background, f = foreground, h = hybrid')
    parser.add_argument('--encoding', type=str, choices=zebraHelp.validEncodings,
        required=True, help='b = binary, u = unary, d = demux')
    parser.add_argument('--family', type=str,
        choices=zebraHelp.validFontFamilies,
        required=True, help='font family')
    parser.add_argument('--size', type=int,
        choices=zebraHelp.validFontSizes,
        required=True, help='font size')
    parser.add_argument('--number', type=int,
        default=-1, help='number')
    parser.add_argument('--slots', type=int,
        choices=zebraHelp.validSlots,
        default=-1, help='slots')
    parser.add_argument('--index', type=str,
        choices=zebraHelp.validIndices,
        default='n', help='index')
    parser.add_argument('--texmfhome', type=str,
        help='substitute for variable TEXMFHOME')
    parser.add_argument('--string', type=str,
        required=True,
        help='text within the zebrackets environment')
    parser.add_argument('--checkargs', action='store_true',
        help='check validity of input arguments')
    args = parser.parse_args(inputArguments)
    filtered_string = zebraFilter(
      args.style, args.encoding, args.family,
      args.size, args.number, args.slots,
      args.index, args.texmfhome,
      args.string, args.checkargs)
    print ('Output is: "', filtered_string, '"', sep='')

# TODO: Document
if __name__ == '__main__':
    zebraFilterParser()
