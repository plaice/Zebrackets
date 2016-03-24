#!/usr/bin/python3

# File zebraFont.py
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

'''zebraFont.py TYPE STYLE STRIPES SIZE FAMILY MAG
creates a new MetaFont file and then invokes it.
'''

import argparse
import glob
import io
import math
import os
import re
import subprocess
import shutil
import sys
import zebraFontFiles
import zebraHelp

class Parameters:
    def __init__(self, kind, style, slots, fontFamily,
            fontSize, mag, texmfHome, checkArgs):

        if kind not in zebraHelp.validKinds:
            raise zebraHelp.ArgError('Invalid kind')
        if style not in zebraHelp.validStyles:
            raise zebraHelp.ArgError('Invalid style')
        if slots not in zebraHelp.validSlots:
            raise zebraHelp.ArgError('Invalid number of slots')
        if fontFamily not in zebraHelp.validFontFamilies:
            raise zebraHelp.ArgError('Invalid Computer Modern font family')
        if fontSize not in zebraHelp.validFontSizes:
            raise zebraHelp.ArgError('Invalid font size')
        if fontSize not in zebraHelp.validFontPairs[fontFamily]:
            raise zebraHelp.ArgError('Invalid font family-size pair')
        if mag not in zebraHelp.validMags:
            raise zebraHelp.ArgError('Invalid magnification')
        texmfHome = zebraHelp.check_texmfhome(texmfHome)

        self.kind = kind
        self.style = style
        self.slots = slots
        self.slotsAsLetter = chr(ord('a') + self.slots)
        self.fontFamily = fontFamily
        self.fontSize = fontSize
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

def createMFcontent(kind, style, slots, sourceFont):
    '''This method creates the font file's header, returning it as string.
    '''
    styledict = { 'b' : '0', 'f' : '1',  'h' : '2' }
    textFormat = '''% Copied from rtest on p.311 of the MetaFont book.
if unknown cmbase: input cmbase fi
mode_setup;
def generate suffix t = enddef;
input {0}; font_setup;
let iff = always_iff;
           
slots:={1};
foreground:={2};
input zeroman{3};'''
    text = textFormat.format(
               sourceFont, slots,
               styledict[style], kind)
    return text

def checkAndCreateFont(fileName, destMFdir, fileContent, texmfHome, log):
    # Check if the font file exists already, and not create it. 
    # Write the content in the file. 
    fileNameMF = '{0}.mf'.format(fileName)
    try:
        subprocess.check_output(['kpsewhich', fileNameMF])
    except subprocess.CalledProcessError:
        destMFpath = '{0}/{1}.mf'.format(destMFdir, fileName)
        with open(destMFpath, 'w') as fileMF:
            fileMF.write(fileContent)
        callAndLog(['mktexlsr', texmfHome], log)

def createMFfiles(params):
    # Set up of diretories and files names
    sourceFont = '{0}{1}'.format(params.fontFamily, int(params.fontSize))
    destMFdir = '{0}/fonts/source/public/zetex'.format(params.texmfHome)
    destTFMdir = '{0}/fonts/tfm/public/zetex'.format(params.texmfHome)
    destPKdir = '{0}/fonts/pk/ljfour/public/zetex'.format(params.texmfHome)
    destMF = 'z{0}{1}{2}{3}'.format(
                 params.kind, params.style,
                 params.slotsAsLetter, sourceFont)
    destMFpath = '{0}/{1}.mf'.format(destMFdir, destMF)
    textMFfile = createMFcontent(
                     params.kind, params.style,
                     params.slots, sourceFont)

    # Check that the master font exists in the TeX ecosystem.
    try:
        subprocess.check_output(['kpsewhich', '{0}.mf'.format(sourceFont)])
    except subprocess.CalledProcessError:
        sys.exit('File "{0}.mf" does not exist'.format(destMF))

    # Create the directory where font files will be stored for this run.
    try:
        os.makedirs(destMFdir)
    except FileExistsError:
        pass

    zetexFontsLog = []

    ## This is now outside in def method
    # Check if the font file exists already, and not create it. 
    # Write the content in the file. 
    checkAndCreateFont(
        destMF, destMFdir, textMFfile, params.texmfHome, zetexFontsLog)
    checkAndCreateFont(
        'zepunctb', destMFdir, zebraFontFiles.str_zepunctb,
        params.texmfHome, zetexFontsLog)
    checkAndCreateFont(
        'zepunctp', destMFdir, zebraFontFiles.str_zepunctp,
        params.texmfHome, zetexFontsLog)
    checkAndCreateFont(
        'zeromanb', destMFdir, zebraFontFiles.str_zeromanb,
        params.texmfHome, zetexFontsLog)
    checkAndCreateFont(
        'zeromanp', destMFdir, zebraFontFiles.str_zeromanp,
        params.texmfHome, zetexFontsLog)

    # Checking main fonts exists

    # generate the TFM font and install the file
    # generate the ls-R database used by the kpathsea library
    try:
        subprocess.check_output(['kpsewhich', '{0}.tfm'.format(destMF)])
    except subprocess.CalledProcessError:
        callAndLog(['mktextfm', destMF], zetexFontsLog)
        callAndLog(
            ['mktexlsr', params.texmfHome], zetexFontsLog)

    if int(params.mag) != 1:
        dpi = params.mag * 600
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
                            format(math.sqrt(float(params.mag)), destMF)],
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

def zebraFont(kind, style, slots, fontFamily,
              fontSize, mag, texmfHome, checkArgs):

    try:
        parameters = Parameters(kind, style, slots, fontFamily,
                         fontSize, mag, texmfHome, checkArgs)
        if checkArgs is False:
            createMFfiles(parameters)
    except zebraHelp.ArgError as e:
        prt_str = 'Invalid input: ' + e.value
        return prt_str

def zebraFontParser(inputArguments = sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Build a zebrackets font.',
        epilog="This module is part of the zebrackets package.")
    parser.add_argument('--kind', type=str, choices=zebraHelp.validKinds,
        required=True, help='b = bracket, p = parenthesis')
    parser.add_argument('--style', type=str, choices=zebraHelp.validStyles,
        required=True, help='b = background, f = foreground, h = hybrid')
    parser.add_argument('--slots', type=int,
        required=True, choices=zebraHelp.validSlots,
        help='number of slots in brackets')
    parser.add_argument('--family', type=str,
        choices=zebraHelp.validFontFamilies,
        required=True, help='font family')
    parser.add_argument('--size', type=int,
        choices=zebraHelp.validFontSizes,
        required=True, help='font size')
    parser.add_argument('--mag', type=int,
        default=1, help='magnification')
    parser.add_argument('--texmfhome', type=str,
        help='substitute for variable TEXMFHOME')
    parser.add_argument('--checkargs', action='store_true',
        help='check validity of input arguments')

    args = parser.parse_args(inputArguments)
    return zebraFont(args.kind, args.style, args.slots, args.family,
        args.size, args.mag, args.texmfhome, args.checkargs)

if __name__ == '__main__':
    zebraFontParser()
