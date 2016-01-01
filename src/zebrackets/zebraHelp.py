#!/usr/bin/python3

# File zebraHelp.py
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

'''This module contains all of the helper methods and functions used
in zebrackets.
'''

import os
import re

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
validMags = [1, 2, 3, 4, 5, 6, 7, 8]

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

class ArgError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def check_kind(params, block_args):
    m = re.search(r'typ\w*=([bp])\w*[,\]]', block_args)
    if m:
        kind = m.group(1)
        if kind not in validKinds:
            raise ArgError("Error: " + kind + " not a valid kind.")
        else:
            params.kind = kind

def check_kind_use(params, block_args):
    m = re.search(r'typ\w*=([bdp])\w*[,\]]', block_args)
    if m:
        kind = m.group(1)
        if kind not in validKindUses:
            raise ArgError("Error: " + kind + " not a valid kind.")
        else:
            params.kind = kind

def check_style(params, block_args):
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', block_args)
    if m:
        style = m.group(1)
        if style not in validStyles:
            raise ArgError("Error: " + style + " not a valid number style.")
        else:
            params.style = style

def check_slots(params, block_args):
    m = re.search(r'str\w*=(\d+)[,\]]', block_args)
    if m:
        slots = int(m.group(1))
        if slots not in validSlots:
            raise ArgError("Error: " + slots + " not a valid number of slots.")
        else:
            params.slots = slots

def check_encoding(params, block_args):
    m = re.search(r'enc\w*=([bdu])\w*[,\]]', block_args)
    if m:
        encoding = m.group(1)
        if encoding not in validEncodings:
            raise ArgError("Error: " + encoding + " not a valid encoding.")
        else:
            params.encoding = encoding

def check_index(params, block_args):
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', block_args)
    if m:
        index = m.group(1)
        if index not in validIndices:
            raise ArgError("Error: " + index + " not a valid index.")
        else:
            params.index = index

def check_number(params, block_args):
    m = re.search(r'num\w*=(\d+)[,\]]', block_args)
    if m:
        number = int(m.group(1))
        if number < 0:
            raise ArgError("Error: " + number + " not a valid glyph number.")
        else:
            params.number = number

def check_mag(params, block_args):
    m = re.search(r'mag\w*=(\d+)[,\]]', block_args)
    if m:
        mag = int(m.group(1))
        if mag not in validMags:
            raise ArgError("Error: " + mag + " not a valid magnification.")
        else:
            params.mag = mag

def check_family(params, block_args):
    m = re.search(r'fam\w*=(\w+)[,\]]', block_args)
    if m:
        family = m.group(1)
        if family not in validFontFamilies:
            raise ArgError("Error: " + m.group(1) + " not a valid font family.")
        else:
            params.family = family

def check_size(params, block_args):
    m = re.search(r'siz\w*=(\d+)[,\]]', block_args)
    if m:
        size = int(m.group(1))
        if size not in validFontSizes:
            raise ArgError("Error: " + size + " not a valid font size.")
        else:
            params.size = size

def check_texmfhome(texmfHome):
    if texmfHome == None:
        if 'TEXMFHOME' not in os.environ:
            prt_str = 'Error: TEXMFHOME environment variable is not set.'
            raise ArgError(prt_str)
        texmfHome = os.environ['TEXMFHOME']
    elif not os.path.isdir(texmfHome):
        prt_str = "Error: Invalid texmf, path is not a directory."
        raise ArgError(prt_str)
    os.environ['TEXMFHOME'] = texmfHome
    return texmfHome
