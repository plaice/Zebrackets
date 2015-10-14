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

validTypes = ['b', 'p']
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
    'cmvtt':  [10] 
}


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

class ArgError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)









