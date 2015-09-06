#!/usr/bin/python3

# File zebraFont.py
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

# zebraFont.py TYPE STYLE STRIPES SIZE FAMILY MAG
# creates a new MetaFont file and then invokes it.

import argparse
import glob
import io
import os
import re
import subprocess
import shutil
import sys

validTypes = ['b', 'p']
validStyles = ['b', 'f', 'h']
validStripes = [0, 1, 2, 3, 4, 5, 6, 7]
validFontFamilies = [
    'cmb', 'cmbtt', 'cmbx', 'cmbxsl', 'cmdunh', 'cmff', 
    'cmfib', 'cmr', 'cmsl', 'cmsltt', 'cmss', 'cmssbx', 
    'cmssdc', 'cmssi', 'cmssq', 'cmssqi', 'cmtt', 'cmttb', 'cmvtt']
validFontSizes = [5, 6, 7, 8, 9, 10, 12, 17]
validFontPairs = {
    'cmb': [10],
    'cmbtt': [8, 9, 10],
    'cmbx': [5, 6, 7, 8, 9, 10, 12],
    'cmbxsl': [10],
    'cmdunh': [10],
    'cmff': [10],
    'cmfib': [8],
    'cmr': [5, 6, 7, 8, 9, 10, 12, 17],
    'cmsl': [8, 9, 10, 12],
    'cmsltt': [10],
    'cmss': [8, 9, 10, 12, 17],
    'cmssbx': [10],
    'cmssdc': [10],
    'cmssi': [8, 9, 10, 12, 17],
    'cmssq': [8],
    'cmssqi': [8],
    'cmtt': [8, 9, 10, 12],
    'cmttb': [10],
    'cmvtt': [10] }

class ArgError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Parameters:
    def __init__(self, btype, style, stripes, fontSize,
            fontFamily, mag, texmfHome, checkArgs):

        if btype not in validTypes:
            raise ArgError('Invalid type')
        if style not in validStyles:
            raise ArgError('Invalid style')
        if stripes not in validStripes:
            raise ArgError('Invalid number of stripes')
        if fontFamily not in validFontFamilies:
            raise ArgError('Invalid Computer Modern font family')
        if texmfHome is None:
            if 'TEXMFHOME' not in os.environ:
                raise ArgError('TEXMFHOME environment variable is not set')
            self.texmfHome = os.environ['TEXMFHOME']

        self.btype = btype
        self.style = style
        self.stripes = stripes
        self.stripesAsLetter = chr(ord('a') + self.stripes)
        self.fontSize = fontSize
        self.fontFamily = fontFamily
        self.mag = mag
        self.texmfHome = texmfHome
        self.checkArgs = checkArgs

def callAndLog(args, log):
    try:
        proc = subprocess.Popen(
                   args, stdout=subprocess.PIPE, universal_newlines=True)
        output = proc.stdout.read()
        if output != '':
            log.append(output)
    except subprocess.CalledProcessError:
        sys.exit('System died when calling {0}'.format(*args))

def createMFcontent(btype, style, stripes, sourceFont):
    styledict = { 'b' : '0', 'f' : '1',  'h' : '2' }
    textFormat = '''% Copied from rtest on p.311 of the MetaFont book.
if unknown cmbase: input cmbase fi
mode_setup;
def generate suffix t = enddef;
input {0}; font_setup;
let iff = always_iff;
           
stripes:={1};
foreground:={2};
input zeroman{3};'''
    text = textFormat.format(
               sourceFont, stripes,
               styledict[style], btype)
    return text

def createMFfiles(params):
    sourceFont = '{0}{1}'.format(params.fontFamily, int(params.fontSize))
    destMFdir = '{0}/fonts/source/public/zetex'.format(params.texmfHome)
    destMF = 'z{0}{1}{2}{3}'.format(
                 params.btype, params.style,
                 params.stripesAsLetter, sourceFont)
    destMFpath = '{0}/{1}.mf'.format(destMFdir, destMF)
    textMFfile = createMFcontent(
                     params.btype, params.style,
                     params.stripes, sourceFont)

    try:
        subprocess.check_output(['kpsewhich', '{0}.mf'.format(sourceFont)])
    except subprocess.CalledProcessError:
        sys.exit('File "{0}.mf" does not exist'.format(destMF))

    try:
        os.makedirs(destMFdir)
    except FileExistsError:
        pass

    try:
        subprocess.check_output(['kpsewhich', destMFpath])
    except subprocess.CalledProcessError:
        with open(destMFpath, 'w') as fileMF:
            fileMF.write(textMFfile)

    zetexFontsLog = []
    try:
        subprocess.check_output(['kpsewhich', '{0}.tfm'.format(destMF)])
    except subprocess.CalledProcessError:
        callAndLog(['mktextfm', destMF], zetexFontsLog)
        callAndLog(['mktexlsr', params.texmfHome], zetexFontsLog)

    if params.mag != 1.0:
        dpi = int(params.mag * params.mag * float(600) + .5)
        try:
            subprocess.check_output(
                ['kpsewhich', '{0}.{1}pk'.format(destMF, dpi)])
        except subprocess.CalledProcessError:
            try:
                proc = subprocess.Popen(
                           ['kpsewhich', '{0}.600pk'.format(destMF)],
                            stdout=subprocess.PIPE, universal_newlines=True)
            except subprocess.CalledProcessError:
                sys.exit('Could not find file {0}.600pk'.format(destMF))
            dpidir = re.sub('/[^/]*$', '', proc.stdout.read())
            callAndLog(['mf-nowin',
                        '-progname=mf',
                        '\\mode:=ljfour; mag:={0}; nonstopmode; input {1}'.
                            format(params.mag, destMF)],
                       zetexFontsLog)
            callAndLog(['gftopk',
                        '{0}.{1}gf'.format(destMF, dpi),
                        '{0}.{1}pk'.format(destMF, dpi)],
                       zetexFontsLog)
            shutil.move('{0}.{1}pk'.format(destMF, dpi), dpidir)
            callAndLog(['mktexlsr', params.texmfHome], zetexFontsLog)
            for file in glob.glob('{0}.*'.format(destMF)):
                os.unlink(file)

    with open('zetexfonts.log', 'a') as zetexLogFile:
        for string in zetexFontsLog:
            zetexLogFile.write(string)

def zebraFont(btype, style, stripes, fontSize,
        fontFamily, mag, texmfHome, checkArgs):
    try:
        parameters = Parameters(btype, style, stripes, fontSize,
                         fontFamily, mag, texmfHome, checkArgs)
        if checkArgs is False:
            createMFfiles(parameters)
    except ArgError as e:
        print('Invalid input:', e.value)

def zebraFontParser(inputArguments = sys.argv):
    parser = argparse.ArgumentParser(description='Build a zebrackets font.')
    parser.add_argument('--type', type=str, choices=validTypes,
        required=True, help='b = bracket, p = parenthesis')
    parser.add_argument('--style', type=str, choices=validStyles,
        required=True, help='b = background, f = foreground, h=hybrid')
    parser.add_argument('--stripes', type=int,
        required=True, choices=validStripes,
        help='number of stripes in brackets')
    parser.add_argument('--size', type=int,
        choices=validFontSizes,
        required=True, help='font size')
    parser.add_argument('--family', type=str,
        choices=validFontFamilies,
        required=True, help='font family')
    parser.add_argument('--mag', type=float,
        default=1.0, help='magnification')
    parser.add_argument('--texmfhome', type=str,
        help='substitute for variable TEXMFHOME')
    parser.add_argument('--checkargs', action='store_true',
        help='check validity of input arguments')
#    ourFavoriteInput = './zebraFont.py --type b --style b --stripes 0 --size 14.4 --family zzz --mag 2.0 --texmfhome /Users/plaice --checkargs'
#    print(ourFavoriteInput)
#    print(ourFavoriteInput.split(' '))
#    print(sys.argv)
#    print(ourFavoriteInput.split(' ') == sys.argv)
    args = parser.parse_args(inputArguments)
    zebraFont(args.type, args.style, args.stripes, args.size,
        args.family, args.mag, args.texmfhome, args.checkargs)

if __name__ == '__main__':
    zebraFontParser()
