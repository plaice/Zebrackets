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

import math
import os
import subprocess
import sys

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

def printUsage(argv, msg):
    print('''Usage: {0} STYLE NUMERATOR DENOMINATOR ENCODING SIZE FAMILY
       STYLE:    [b = background, f = foreground, h = hydrid]
       NUMERATOR:
       DENOMINATOR:
       ENCODING: [b = binary, u = unary, d = demux]
       SIZE:     float
       FAMILY:   string
       Environment variable TEXMFHOME must be set'''.format(argv[0]))
    sys.exit(msg)

# TODO: Document
class Parameters:
    def __init__(self, argv):
        if len(argv[:]) != 7:
            printUsage(argv, 'Invalid number of arguments')

        if len(argv[1]) != 1 or 'bfh'.find(argv[1]) == -1:
            printUsage(argv, 'Invalid style')
        self.style = argv[1]

        self.numerator = int(argv[2])
        self.denominator = int(argv[3])
        if self.numerator < 0:
            if self.numerator < -3:
                printUsage(argv, 'Invalid numerator')
        elif self.denominator < 0:
            printUsage(argv, 'Invalid denominator')

        if len(argv[4]) != 1 or 'bud'.find(argv[4]) == -1:
            printUsage(argv, 'Invalid encoding')
        self.valueToEncoding = valueToFunctions[argv[4]]
        self.valueFromEncoding = valueFromFunctions[argv[4]]

        self.ptSize = float(argv[5])
        if self.ptSize < 0:
            printUsage(argv, 'Invalid point size')

        self.typeFamily = argv[6]

        if 'TEXMFHOME' not in os.environ:
            printUsage(argv, 'TEXMFHOME environment variable is not set')
        self.texmfHome = os.environ['TEXMFHOME']

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
                                              params.typeFamily)
            print('\\ifundefined{{{0}{1}}}\\newfont{{\\{0}{1}}}{{{0}{2}}}\\fi'.
                  format(fontName,
                         chr(ord('A') - 1 + int(params.ptSize)),
                         int(params.ptSize)))

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
                         params.typeFamily,
                         chr(ord('A') - 1 + int(params.ptSize)),
                         numerator), end='')
        else:
            print(c, end='')
         
# TODO: Document
def generateFiles(params, delims, buf):
    baseCommand = './generateFont.py'
    for k, w in delims.items():
        if w.used:
            try:
                subprocess.check_output([baseCommand,
                                         w.kind,
                                         params.style,
                                         str(w.denominator),
                                         str(params.ptSize),
                                         params.typeFamily,
                                         str(1.0)])
                                        
            except subprocess.CalledProcessError:
                pass



# TODO: Document
if __name__ == '__main__':
    parameters = Parameters(sys.argv)
    delimiters = dict(bracket = Delimiter('b', '[', ']'),
                      parenthesis = Delimiter('p', '(', ')'))
    fileBuffer = readInput()
    countDelimiters(parameters, delimiters, fileBuffer)
    printDeclarations(parameters, delimiters, fileBuffer)
    printAndReplaceSymbols(parameters, delimiters, fileBuffer)
    generateFiles(parameters, delimiters, fileBuffer)
