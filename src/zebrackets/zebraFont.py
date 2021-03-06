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
    def __init__(self, kind, style, slots, family,
            size, mag, texmfHome, checkArgs):
        self.kind = zebraHelp.validate_kind(kind)
        self.style = zebraHelp.validate_style(style)
        self.slots = zebraHelp.validate_slots(slots)
        self.slotsAsLetter = chr(ord('a') + self.slots)
        self.family = zebraHelp.validate_family(family)
        self.size = zebraHelp.validate_size(size)
        zebraHelp.validate_family_size(family, size)
        self.mag = zebraHelp.validate_mag(mag)
        self.texmfHome = zebraHelp.validate_texmfhome(texmfHome)
        self.checkArgs = checkArgs

def callAndLog(args, log):
    try:
        proc = subprocess.Popen(
                   args, stdout=subprocess.PIPE, universal_newlines=True)
        output = proc.stdout.read()
        if output != '':
            log.append(output)
    except subprocess.CalledProcessError:
        raise zebraHelp.CompError('System died when calling {0}'.format(*args))

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
    sourceFont = '{0}{1}'.format(params.family, int(params.size))
    destMFdir = '{0}/fonts/source/public/zbtex'.format(params.texmfHome)
    destTFMdir = '{0}/fonts/tfm/public/zbtex'.format(params.texmfHome)
    destPKdir = '{0}/fonts/pk/ljfour/public/zbtex'.format(params.texmfHome)
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
        raise zebraHelp.CompError('File "{0}.mf" does not exist'.format(destMF))

    # Create the directory where font files will be stored for this run.
    try:
        os.makedirs(destMFdir)
    except FileExistsError:
        pass

    zbtexFontsLog = []

    ## This is now outside in def method
    # Check if the font file exists already, and not create it. 
    # Write the content in the file. 
    checkAndCreateFont(
        destMF, destMFdir, textMFfile, params.texmfHome, zbtexFontsLog)
    checkAndCreateFont(
        'zepunctb', destMFdir, zebraFontFiles.str_zepunctb,
        params.texmfHome, zbtexFontsLog)
    checkAndCreateFont(
        'zepunctp', destMFdir, zebraFontFiles.str_zepunctp,
        params.texmfHome, zbtexFontsLog)
    checkAndCreateFont(
        'zeromanb', destMFdir, zebraFontFiles.str_zeromanb,
        params.texmfHome, zbtexFontsLog)
    checkAndCreateFont(
        'zeromanp', destMFdir, zebraFontFiles.str_zeromanp,
        params.texmfHome, zbtexFontsLog)

    # Checking main fonts exists

    # generate the TFM font and install the file
    # generate the ls-R database used by the kpathsea library
    try:
        subprocess.check_output(['kpsewhich', '{0}.tfm'.format(destMF)])
    except subprocess.CalledProcessError:
        callAndLog(['mktextfm', destMF], zbtexFontsLog)
        callAndLog(
            ['mktexlsr', params.texmfHome], zbtexFontsLog)

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
                raise zebraHelp.CompError('Could not find file {0}.600pk'.
                                          format(destMF))
            dpidir = re.sub('/[^/]*$', '', proc.stdout.read())
            callAndLog(['mf-nowin',
                        '-progname=mf',
                        '\\mode:=ljfour; mag:={0}; nonstopmode; input {1}'.
                            format(math.sqrt(float(params.mag)), destMF)],
                       zbtexFontsLog)
            callAndLog(['gftopk',
                        '{0}.{1}gf'.format(destMF, dpi),
                        '{0}.{1}pk'.format(destMF, dpi)],
                       zbtexFontsLog)
            shutil.move('{0}.{1}pk'.format(destMF, dpi), dpidir)
            callAndLog(['mktexlsr', params.texmfHome], zbtexFontsLog)
            for file in glob.glob('{0}.*'.format(destMF)):
                os.unlink(file)

    with open('zbtexfonts.log', 'a') as zbtexLogFile:
        for string in zbtexFontsLog:
            zbtexLogFile.write(string)

def zebraFont(kind, style, slots, family,
              size, mag, texmfHome, checkArgs):

    try:
        parameters = Parameters(kind, style, slots, family,
                         size, mag, texmfHome, checkArgs)
        if checkArgs is False:
            createMFfiles(parameters)
        return zebraHelp.Result(True, "")
    except zebraHelp.ArgError as e:
        return zebraHelp.Result(False, "zebraFont ArgError: " + e)
    except zebraHelp.CompError as e:
        return zebraHelp.Result(False, "zebraFont CompError: " + e)

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
