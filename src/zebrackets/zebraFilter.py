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

valueToFunctions = {
    'b' : (lambda value : value % 256),
    'u' : (lambda value : pow(2, (value % 8)) - 1),
    'd' : (lambda value : pow(2, (value - 1) % 7) if value else value) }

#valueFromFunctions = {
#    'b' : (lambda value : int(math.ceil(math.log(value, 2)))),
#    'u' : (lambda value : value - 1),
#    'd' : (lambda value : value - 1) }

# TODO: Document
class Delimiter:
    def __init__(self, kind, left, right):
        self.kind = kind
        self.left = left
        self.right = right
        self.used = False

class Active:
    def __init__(self, expected_right, kind, count, depth, breadth):
        self.expected_right = expected_right
        self.kind = kind
        self.count = count
        self.depth = depth
        self.breadth = breadth

    def __repr__(self):
        return "<Active expected:%s, kind:%s, count:%s, depth:%s, breadth:%s>" % (self.expected_right, self.kind, self.count, self.depth, self.breadth)

# TODO: Document
class Parameters:
    def __init__(self, style, encoding, fontFamily, fontSize, mag,
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
        if mag not in zebraHelp.validMags:
            raise zebraHelp.ArgError('Invalid magnification')
        if index == 'n':
            if number < 0:
                raise zebraHelp.ArgError('Invalid number')
        elif index not in zebraHelp.validIndices:
            raise zebraHelp.ArgError('Invalid index')
        if number >= 0:
            index = 'n'
        
        texmfHome = zebraHelp.check_texmfhome(texmfHome)

        self.style = style
        self.encoding = encoding
        self.valueToEncoding = valueToFunctions[encoding]
#        self.valueFromEncoding = valueFromFunctions[encoding]
        self.fontFamily = fontFamily
        self.fontSize = fontSize
        self.mag = mag
        self.number = number
        self.slots = slots
        self.index = index
        self.texmfHome = texmfHome
        self.checkArgs = checkArgs

        self.highestCount = -1
        self.deepestDepth = -1
        self.broadestBreadth = -1


# TODO: Document
def countDelimiters(params, delims, buf):
    '''Go through the buffer and count the (opening) delimiters
    in case the automatic slots counter is requested.
    '''

    delim_opens = ['(', '[']
    max_stack = []
    active_stack = []
    count = -1
    depth = -1
    expected_right = None
    
    # Each entry in active_stack
    for c in buf:
        if c in delim_opens:
            delims[c].used = True
            count += 1
            if params.highestCount < count:
                params.highestCount = count
            depth += 1
            if params.deepestDepth < depth:
                params.deepestDepth = depth
            if len(max_stack) == depth:
                max_stack.append(-1)
                active_stack.append(None)
            max_stack[depth] += 1
            active_stack[depth] = Active(expected_right, delims[c].kind,
                                         count, depth, max_stack[depth])
            expected_right = delims[c].right
            if params.broadestBreadth < max_stack[depth]:
                params.broadestBreadth = max_stack[depth]
        elif c == expected_right:
            expected_right = active_stack[depth].expected_right
            active_stack[depth] = None
            depth -= 1

    # Calculate all the slots based upon the above tally.
    if params.slots == -1:
        if params.index == 'u':
            params.slots = params.highestCount
        elif params.index == 'd':
            params.slots = params.deepestDepth
        elif params.index == 'b':
            params.slots = params.broadestBreadth
        else:
            params.slots = params.number
    if params.slots > 7:
        params.slots = 7

# TODO: Document
def printDeclarations(params, delims, buf, out_string):
    for k, w in delims.items():
        if w.used:
            fontName = 'z{0}{1}{2}{3}'.format(
                w.kind,
                params.style,
                chr(ord('a') + params.slots),
                params.fontFamily
            )
            out_string.write(
                '\\ifundefined{{{0}{1}}}\\newfont{{\\{0}{1}}}{{{0}{2}}}\\fi'.
                    format(fontName,
                           chr(ord('A') - 1 + params.fontSize),
                           params.fontSize))

# TODO: Document
def printAndReplaceSymbols(params, delims, buf, out_string):

    delim_opens = ['(', '[']
    delim_chars = ['(', ')', '[', ']']
    max_stack = []
    active_stack = []
    count = -1
    depth = -1
    expected_right = None
    active = None
    
    # Each entry in active_stack
    for c in buf:
        replace = False
        if params.number != -1 and c in delim_chars:
            replace = True
            is_left = c in delim_opens
            c_kind = delims[c].kind
        elif c in delim_opens:
            delims[c].used = True
            count += 1
            if params.highestCount < count:
                params.highestCount = count
            depth += 1
            if params.deepestDepth < depth:
                params.deepestDepth = depth
            if len(max_stack) == depth:
                max_stack.append(-1)
                active_stack.append(None)
            max_stack[depth] += 1
            active_stack[depth] = Active(expected_right, delims[c].kind,
                                         count, depth, max_stack[depth])
            expected_right = delims[c].right
            if params.broadestBreadth < max_stack[depth]:
                params.broadestBreadth = max_stack[depth]
            replace = True
            is_left = True
            active = active_stack[depth]
            c_kind = active.kind
        elif c == expected_right:
            expected_right = active_stack[depth].expected_right
            active = active_stack[depth]
            c_kind = active.kind
            depth -= 1
            replace = True
            is_left = False

        if replace:
            if params.index == 'u':
                number = active.count
            elif params.index == 'd':
                number = active.depth
            elif params.index == 'b':
                number = active.breadth
            else:
                number = params.number
            number = params.valueToEncoding(number)
            if not is_left:
                number += pow(2, params.slots)

            out_string.write('{{\\z{0}{1}{2}{3}{4} \\symbol{{{5}}}}}'.
                  format(c_kind,
                         params.style,
                         chr(ord('a') + params.slots),
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
                params.slots,
                params.fontFamily,
                params.fontSize,
                params.mag,
                params.texmfHome,
                False)

def zebraFilter(style, encoding, fontFamily, fontSize, mag,
        number, slots, index, texmfHome, string_tofilter, 
        checkArgs=False):

    try:
        parameters = Parameters(style, encoding, fontFamily, fontSize, mag,
                         number, slots, index, texmfHome, checkArgs)
        if checkArgs is False:
            out_string = io.StringIO()
            delimiters = {}
            delimiters['['] = Delimiter('b', '[', ']')
            delimiters[']'] = Delimiter('b', '[', ']')
            delimiters['('] = Delimiter('p', '(', ')')
            delimiters[')'] = Delimiter('p', '(', ')')
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
            value = out_string.getvalue()
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
    parser.add_argument('--mag', type=int,
        choices=zebraHelp.validMags,
        default=1, help='magnification')
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
      args.size, args.mag, args.number, args.slots,
      args.index, args.texmfhome,
      args.string, args.checkargs)
#    print ('Output is: "', filtered_string, '"', sep='')

# TODO: Document
if __name__ == '__main__':
    zebraFilterParser()
