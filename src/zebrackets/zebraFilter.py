#!/usr/bin/python3

# File zebraFilter.py
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

import argparse
import math
import os
import subprocess
import sys
from zebrackets import zebraFont

validStyles = ['b', 'f', 'h']
validEncodings = ['b', 'u', 'd']
validFontFamilies = [
    'cmb', 'cmbtt', 'cmbx', 'cmbxsl', 'cmdunh', 'cmff',
    'cmfib', 'cmr', 'cmsl', 'cmsltt', 'cmss', 'cmssbx',
    'cmssdc', 'cmssi', 'cmssq', 'cmssqi', 'cmtt', 'cmttb', 'cmvtt']
validFontSizes = [5, 6, 7, 8, 9, 10, 12, 17]
validFontPairs = {
    'cmb':    [10],
    'cmbtt':  [8, 9, 10],
    'cmbx':   [5, 6, 7, 8, 9, 10, 12],
    'cmbxsl': [10],
    'cmdunh': [10],
    'cmff':   [10],
    'cmfib':  [8],
    'cmr':    [5, 6, 7, 8, 9, 10, 12, 17],
    'cmsl':   [8, 9, 10, 12],
    'cmsltt': [10],
    'cmss':   [8, 9, 10, 12, 17],
    'cmssbx': [10],
    'cmssdc': [10],
    'cmssi':  [8, 9, 10, 12, 17],
    'cmssq':  [8],
    'cmssqi': [8],
    'cmtt':   [8, 9, 10, 12],
    'cmttb':  [10],
    'cmvtt':  [10] }

# This filter is run on a region of text.
#  Its arguments dictate translation of parentheses in the region.

# TODO: Document
valueToFunctions = {
    'b' : (lambda value : value % 256),
    'u' : (lambda value : pow(2, (value % 8)) - 1),
    'd' : (lambda value : pow(2, value % 7)) }

# TODO: Document
valueFromFunctions = {
    'b' : (lambda value : int(math.ceil(math.log(value, 2)))),
    'u' : (lambda value : value - 1),
    'd' : (lambda value : value) }

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

# TODO: Document
class Parameters:
    def __init__(self, style, encoding, fontFamily, fontSize,
            numerator, denominator, texmfHome, checkArgs):
        if style not in validStyles:
            raise ArgError('Invalid style')
        if encoding not in validEncodings:
            raise ArgError('Invalid encoding')
        if fontFamily not in validFontFamilies:
            raise ArgError('Invalid Computer Modern font family')
        if fontSize not in validFontSizes:
            raise ArgError('Invalid font size')
        if fontSize not in validFontPairs[fontFamily]:
            raise ArgError('Invalid font family-size pair')
        if texmfHome is None:
            if 'TEXMFHOME' not in os.environ:
                raise ArgError('TEXMFHOME environment variable is not set')
            texmfHome = os.environ['TEXMFHOME']

        if numerator < 0:
            if numerator < -3:
                ArgError('Invalid numerator')
        elif denominator < 0:
            ArgError('Invalid denominator')

        self.style = style
        self.encoding = encoding
        self.valueToEncoding = valueToFunctions[encoding]
        self.valueFromEncoding = valueFromFunctions[encoding]
        self.numerator = numerator
        self.denominator = denominator
        self.fontFamily = fontFamily
        self.fontSize = fontSize
        self.texmfHome = texmfHome
        self.checkArgs = checkArgs

# TODO: Document
def readInput():
    return sys.stdin.read()

# TODO: Document
def countDelimiters(params, delims, buf):
    # Go through the buffer and count the (opening) delimiters
    # in case the automatic stripe denominator is requested.
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

    # Calculate all the denominators based upon the above tally.
    for k, w in delims.items():
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
def printDeclarations(params, delims, buf):
    for k, w in delims.items():
        if params.denominator != -1:
            w.denominator = params.denominator
        if w.used:
            fontName = 'z{0}{1}{2}{3}'.format(w.kind,
                                              params.style,
                                              chr(ord('a') + w.denominator),
                                              params.fontFamily)
            print('\\ifundefined{{{0}{1}}}\\newfont{{\\{0}{1}}}{{{0}{2}}}\\fi'.
                  format(fontName,
                         chr(ord('A') - 1 + int(params.fontSize)),
                         int(params.fontSize)))

# TODO: Document
def printAndReplaceSymbols(params, delims, buf):
    for k, w in delims.items():
       w.count = -1
       w.depth = 0
       for level in range(64):
           w.stack[level] = 0

    for c in buf:
        replace = False
        for k, w in delims.items():
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

            print('{{\\z{0}{1}{2}{3}{4} \\symbol{{{5}}}}}'.
                  format(wsaved.kind,
                         params.style,
                         chr(ord('a') + wsaved.denominator),
                         params.fontFamily,
                         chr(ord('A') - 1 + int(params.fontSize)),
                         numerator), end='')
        else:
            print(c, end='')
         
# TODO: Document
def generateFiles(params, delims, buf):
    for k, w in delims.items():
        if w.used:
            zebraFont.zebraFont(
                w.kind,
                params.style,
                int(w.denominator),
                params.fontFamily,
                int(params.fontSize),
                1.0,
                params.texmfHome,
                False)

def zebraFilter(style, encoding, fontFamily, fontSize,
        numerator, denominator, texmfHome, checkArgs):
    try:
        parameters = Parameters(style, encoding, fontFamily, fontSize,
                         numerator, denominator, texmfHome, checkArgs)
        if checkArgs is False:
            delimiters = dict(bracket = Delimiter('b', '[', ']'),
                              parenthesis = Delimiter('p', '(', ')'))
            fileBuffer = readInput()
            countDelimiters(parameters, delimiters, fileBuffer)
            printDeclarations(parameters, delimiters, fileBuffer)
            printAndReplaceSymbols(parameters, delimiters, fileBuffer)
            generateFiles(parameters, delimiters, fileBuffer)
    except ArgError as e:
        print('Invalid input:', e.value)

def zebraFilterParser(inputArguments = sys.argv[1:]):
    parser = argparse.ArgumentParser(
                 description='Replace brackets by zebrackets in a text.')
    parser.add_argument('--style', type=str, choices=validStyles,
        required=True, help='b = background, f = foreground, h = hybrid')
    parser.add_argument('--encoding', type=str, choices=validEncodings,
        required=True, help='b = binary, u = unary, d = demux')
    parser.add_argument('--family', type=str,
        choices=validFontFamilies,
        required=True, help='font family')
    parser.add_argument('--size', type=int,
        choices=validFontSizes,
        required=True, help='font size')
    parser.add_argument('--numerator', type=int,
        required=True, help='numerator')
    parser.add_argument('--denominator', type=int,
        required=True, help='denominator')
    parser.add_argument('--texmfhome', type=str,
        help='substitute for variable TEXMFHOME')
    parser.add_argument('--checkargs', action='store_true',
        help='check validity of input arguments')
    args = parser.parse_args(inputArguments)
    zebraFilter(args.style, args.encoding, args.family, args.size,
        args.numerator, args.denominator, args.texmfhome, args.checkargs)

# TODO: Document
if __name__ == '__main__':
    zebraFilterParser()