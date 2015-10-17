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
import math

# Type is parentheses, brackets
validTypes = ['p', 'b']
# Style is background, foreground, hybrid
validStyles = ['b', 'f', 'h']
validStripes = [0, 1, 2, 3, 4, 5, 6, 7]
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
# Encoding is uniry, binary and demux
validEncodings = ['u', 'b', 'd']
# Index is breadth, depth
validIndex = ['b', 'd']


class ArgError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def check_texmfhome(texmfHome):
    if texmfHome == None:
        if 'TEXMFHOME' not in os.environ:
            prt_str = 'Error: TEXMFHOME environment variable is not set.'
            raise ArgError(prt_str)
        texmfHome = os.environ['TEXMFHOME']
    elif not os.path.isdir(texmfHome):
        prt_str = "Error: Invalid texmf, path is not a directory."
        raise ArgError(prt_str)
    return texmfHome

def check_type_(params, block_args):
    m = re.search(r'typ\w*=([bp])\w*[,\]]', block_args)
    if m:
        params.type_ = m.group(1)

def check_style(params, block_args):
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', block_args)
    if m:
        params.style = m.group(1)

def check_stripes(params, block_args):
    m = re.search(r'str\w*=(\d+)[,\]]', block_args)
    if m:
        stripe = int(m.group(1))
        if stripe not in validStripes:
            raise ArgError("Error: " + stripe + " not a valid stripe number.")
        else:
            params.stripes = stripe

def check_family(params, block_args):
    m = re.search(r'fam\w*=(\w+)[,\]]', block_args)
    if m:
        if m.group(1) not in validFontFamilies:
            raise ArgError("Error: " + m.group(1) + " not a valid font family.")
        else:
            params.family = m.group(1)

def check_size(params, block_args):
    m = re.search(r'siz\w*=(\d+)[,\]]', block_args)
    if m:
        size = int(m.group(1))
        if size not in validFontSizes:
            raise ArgError("Error: " + size + " not a valid font size.")
        else:
            params.size = int(m.group(1))

def check_mag(params, block_args):
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', block_args)
    if m:
        params.mag = math.sqrt(float(m.group(1)))

def check_index(params, block_args):
    # Index is not being used for anything. John to check.
    m = re.search(r'ind\w*=([du])\w*[,\]]', block_args)
    if m:
        params.index = m.group(1)
        if (params.index == 'b'):
            params.index = -3
        elif (params.index == 'd'):
            params.index = -2
        else:
            params.index = -1

def check_numerator(params, block_args):
    m = re.search(r'num\w*=([-]?\d+)[,\]]', block_args)
    if m:
        params.numerator = int(m.group(1))
    else:
        params.numerator = int(params.index)

def check_denominator(params, block_args):
    m = re.search(r'den\w*=([-]?\d+)[,\]]', block_args)
    if m:
        params.denominator = int(m.group(1))

def check_encoding(params, block_args):
    m = re.search(r'enc\w*=([ubdt])\w*[,\]]', block_args)
    if m:
        params.encoding = m.group(1)

