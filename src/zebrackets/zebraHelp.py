#!/usr/bin/python3

# File zebraHelp.py
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

'''This module contains all of the helper methods and functions used
in zebrackets.
'''

import os
import re

class ArgError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CompError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Result:
    def __init__(self, flag, result):
        self.flag = flag
        self.result = result
    def __str__(self):
        return repr(self.result)

# Kind is parenthesis, bracket
validKinds = ['p', 'b']

# KindUse is parenthesis, bracket, dual
validKindUses = ['p', 'b', 'd']

# Style is foreground, background, hybrid
validStyles = ['f', 'b', 'h']

# Slots is a value in 0..7, inclusive
validSlots = [0, 1, 2, 3, 4, 5, 6, 7]

# Encoding is unary, binary, demux
validEncodings = ['u', 'b', 'd']

# Index is depth, unique, breadth
validIndices = ['d', 'u', 'b']

# Mag is a value in 1..8, inclusive
#validMags = [1, 2, 3, 4, 5, 6, 7, 8]
validMags = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
             11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
             31, 32]

# Font family-size pairs are hard-coded
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
    'cmvtt':  [10],
}

def validate_kind(kind):
    if kind not in validKinds:
        raise ArgError('' + str(kind) + ' not a valid kind.')
    return kind

def check_kind(params, block_args):
    m = re.search(r'kin\w*=([bp])\w*[,\]]', block_args)
    if m:
        kind = m.group(1)
        params.kind = validate_kind(kind)

def check_kind_use(params, block_args):
    m = re.search(r'kin\w*=([bdp])\w*[,\]]', block_args)
    if m:
        kind = m.group(1)
        params.kind = validate_kind(kind)

def validate_style(style):
    if style not in validStyles:
        raise ArgError('' + str(style) + ' not a valid number style.')
    return style

def check_style(params, block_args):
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', block_args)
    if m:
        style = m.group(1)
        params.style = validate_style(style)

def validate_slots(slots):
    if slots not in validSlots:
        raise ArgError('' + str(slots) + ' not a valid number of slots.')
    return slots

def check_slots(params, block_args):
    m = re.search(r'slo\w*=(\d+)[,\]]', block_args)
    if m:
        slots = int(m.group(1))
        params.slots = validate_slots(slots)

def validate_encoding(encoding):
    if encoding not in validEncodings:
        raise ArgError('' + str(encoding) + ' not a valid encoding.')
    return encoding

def check_encoding(params, block_args):
    m = re.search(r'enc\w*=([bdu])\w*[,\]]', block_args)
    if m:
        encoding = m.group(1)
        params.encoding = validate_encoding(encoding)

def validate_index(index):
    if index not in validIndices:
        raise ArgError('' + str(index) + ' not a valid index.')
    return index

def check_index(params, block_args):
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', block_args)
    if m:
        index = m.group(1)
        params.index = validate_index(index)

def validate_number(number):
    if number < 0:
        raise ArgError('' + str(number) + ' not a valid glyph number.')
    return number

def check_number(params, block_args):
    m = re.search(r'num\w*=(\d+)[,\]]', block_args)
    if m:
        number = int(m.group(1))
        params.number = validate_number(number)

def validate_mag(mag):
    if mag not in validMags:
        raise ArgError('' + str(mag) + ' not a valid magnification.')
    return mag

def check_mag(params, block_args):
    m = re.search(r'mag\w*=(\d+)[,\]]', block_args)
    if m:
        mag = int(m.group(1))
        params.mag = validate_mag(mag)

def validate_family(family):
    if family not in validFontFamilies:
        raise ArgError('' + str(family) + ' not a valid font family.')
    return family

def check_family(params, block_args):
    m = re.search(r'fam\w*=(\w+)[,\]]', block_args)
    if m:
        family = m.group(1)
        params.family = validate_family(family)

def validate_size(size):
    if size not in validFontSizes:
        raise ArgError('' + str(size) + ' not a valid font size.')
    return size

def check_size(params, block_args):
    m = re.search(r'siz\w*=(\d+)[,\]]', block_args)
    if m:
        size = int(m.group(1))
        params.size = validate_size(size)

def validate_family_size(family, size):
   if size not in validFontPairs[family]:
        raise ArgError('' + str(size) + ' not a valid font size.')

def validate_texmfhome(texmfHome):
    if texmfHome == None:
        if 'TEXMFHOME' not in os.environ:
            raise ArgError('TEXMFHOME environment variable is not set.')
        texmfHome = os.environ['TEXMFHOME']
    if not os.path.isdir(texmfHome):
        raise ArgError('Invalid texmf path, not a directory.')
    os.environ['TEXMFHOME'] = texmfHome
    return texmfHome

def check_mixcount(params, block_args):
    m = re.search(r'mix\w*[,\]]', block_args)
    if m:
        params.mixcount = True
    m = re.search(r'nomix\w*[,\]]', block_args)
    if m:
        params.mixcount = False

