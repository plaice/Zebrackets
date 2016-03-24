#!/usr/bin/python3

# File zebraFilter.py
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

# TODO: Document
class Stacks:
    def __init__(self):
        self.max_stack = []
        self.active_stack = []
        self.count = -1
        self.depth = -1
        self.expected_right = None
        self.active = None

class Delimiter:
    def __init__(self, kind, left, right):
        self.kind = kind
        self.left = left
        self.right = right
        self.used = False
        self.stacks = None

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
    def __init__(self, style, encoding, family, size, mag,
            number, slots, index, mixcount, texmfHome, checkArgs):
        self.style = zebraHelp.validate_style(style)
        self.encoding = zebraHelp.validate_encoding(encoding)
        self.valueToEncoding = valueToFunctions[encoding]
        self.slots = slots
        self.family = zebraHelp.validate_family(family)
        self.size = zebraHelp.validate_size(size)
        zebraHelp.validate_family_size(family, size)
        self.mag = zebraHelp.validate_mag(mag)
        if index == 'n':
            zebraHelp.validate_number(number)
        else:
            zebraHelp.validate_index(index)
        if number >= 0:
            index = 'n'
        self.number = number
        self.index = index
        self.mixcount = mixcount
        self.texmfHome = zebraHelp.validate_texmfhome(texmfHome)
        self.checkArgs = checkArgs

        self.highestCount = -1
        self.deepestDepth = -1
        self.broadestBreadth = -1


# TODO: Document
def printAndReplaceSymbols(params, delims, buf, out_string = None):
    '''On the first pass, go through the buffer and count the (opening)
       delimiters in case the automatic slots counter is requested.
       On the second pass, generate the correct output.'''

    delim_opens = ['(', '[']
    delim_closes = [')', ']']
    delim_chars = ['(', ')', '[', ']']

    delims['('].stacks = Stacks()
    if params.mixcount:
        delims['['].stacks = delims['('].stacks
    else:
        delims['['].stacks = Stacks()
    
    sit = Stacks()
    
    # Each entry in active_stack
    for c in buf:
        replace = False
        if out_string != None and params.number != -1 and c in delim_chars:
            replace = True
            is_left = c in delim_opens
            c_kind = delims[c].kind
        elif c in delim_opens:
            sit = delims[c].stacks
            delims[c].used = True
            sit.count += 1
            if params.highestCount < sit.count:
                params.highestCount = sit.count
            sit.depth += 1
            if params.deepestDepth < sit.depth:
                params.deepestDepth = sit.depth
            if len(sit.max_stack) == sit.depth:
                sit.max_stack.append(-1)
                sit.active_stack.append(None)
            sit.max_stack[sit.depth] += 1
            sit.active_stack[sit.depth] = Active(sit.expected_right,
                                                 delims[c].kind,
                                                 sit.count,
                                                 sit.depth,
                                                 sit.max_stack[sit.depth])
            if params.broadestBreadth < sit.max_stack[sit.depth]:
                params.broadestBreadth = sit.max_stack[sit.depth]
            sit.expected_right = delims[c].right
            active = sit.active_stack[sit.depth]
            c_kind = active.kind
            replace = True
            is_left = True
        elif c in delim_closes:
            sit = delims[c].stacks
            if c == sit.expected_right:
                sit.expected_right = sit.active_stack[sit.depth].expected_right
                active = sit.active_stack[sit.depth]
                sit.depth -= 1
                c_kind = active.kind
                replace = True
                is_left = False
    
        if out_string != None:
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
    
                out_string.write('{{\\z{0}{1}{2}{3}{4}{5} \\symbol{{{6}}}}}'.
                      format(c_kind,
                             params.style,
                             chr(ord('a') + params.slots),
                             params.family,
                             chr(ord('A') - 1 + params.size),
                             chr(ord('A') - 1 + params.mag),
                             number))
            else:
                out_string.write(c)

    # Calculate all the slots based upon the above tally.
    if out_string == None:
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
    errors = ''
    for k, w in delims.items():
        if w.used:
            res = zebraFont(w.kind,
                               params.style,
                               params.slots,
                               params.family,
                               params.size,
                               params.mag,
                               params.texmfHome,
                               False)
            if res.flag == True:
                fontName = 'z{0}{1}{2}{3}'.format(
                    w.kind,
                    params.style,
                    chr(ord('a') + params.slots),
                    params.family
                )
                out_string.write(
                    '\\ifundefined{{{0}{1}{2}}}\\newfont{{\\{0}{1}{2}}}{{{0}{3} scaled {4}000}}\\fi'.
                        format(fontName,
                               chr(ord('A') - 1 + params.size),
                               chr(ord('A') - 1 + params.mag),
                               params.size,
                               params.mag))
            else:
                if errors == '':
                    errors = res.result
                else:
                    errors = errors + '\n' + res.result
    return errors

def zebraFilter(style, encoding, family, size, mag,
        number, slots, index, mixcount, texmfHome, string_tofilter, 
        checkArgs=False):

    try:
        parameters = Parameters(style, encoding, family, size, mag,
                                number, slots, index, mixcount,
                                texmfHome, checkArgs)
        if checkArgs is False:
            out_string = io.StringIO()
            delimiters = {}
            delimiters['['] = Delimiter('b', '[', ']')
            delimiters[']'] = delimiters['[']
            delimiters['('] = Delimiter('p', '(', ')')
            delimiters[')'] = delimiters['(']
            printAndReplaceSymbols(parameters,
                                   delimiters,
                                   string_tofilter)
            errors = printDeclarations(parameters,
                                       delimiters,
                                       string_tofilter,
                                       out_string)
            if errors == '':
                printAndReplaceSymbols(parameters,
                                       delimiters,
                                       string_tofilter,
                                       out_string)
                value = out_string.getvalue()
                out_string.close()
                return zebraHelp.Result(True, value)
            else:
                out_string.close()
                out_string.write(string_to_filter)
                return zebraHelp.Result(False, errors)
    except zebraHelp.ArgError as e:
        return zebraHelp.Result(False, "zebraFilter ArgError: " + e)

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
    parser.add_argument('--mixcount', dest='mixcount', action='store_true')
    parser.add_argument('--no-mixcount', dest='mixcount', action='store_false')
    parser.set_defaults(mixcount=True)
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
      args.index, args.mixcount, args.texmfhome,
      args.string, args.checkargs)

# TODO: Document
if __name__ == '__main__':
    zebraFilterParser()
