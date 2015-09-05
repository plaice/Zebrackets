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

# This filter is run on a region of text.
# Its arguments dictate translation of parentheses in the region.

# zebraFont.py TYPE STYLE STRIPES SIZE FAMILY MAG
# creates a new MetaFont file and then invokes it.

import glob
import io
import os
import re
import subprocess
import shutil
import sys

def printUsage(argv, msg):
    print('''Usage: {0} TYPE STYLE STRIPES SIZE FAMILY MAG
       TYPE:    [b = bracket, p = parenthesis]
       STYLE:   [b = background, f = foreground, h = hydrid]
       STRIPES: [0-7]
       SIZE:    float
       FAMILY:  string
       MAG:     float
       Environment variable TEXMFHOME must be set'''.format(argv[0]))
    sys.exit(msg)

class Parameters:
    def __init__(self, argv):
        print(argv)
        if len(argv[:]) != 7:
            printUsage(argv, 'Invalid number of arguments')

        if len(argv[1]) != 1 or 'bp'.find(argv[1]) == -1:
            printUsage(argv, 'Invalid kind')
        self.kind = argv[1]

        if len(argv[2]) != 1 or 'bfh'.find(argv[2]) == -1:
            printUsage(argv, 'Invalid style')
        self.style = argv[2]

        self.stripes = int(argv[3])
        if self.stripes < 0 or self.stripes > 7:
            printUsage(argv, 'Invalid number of stripes')
        self.stripesAsLetter = chr(ord('a') + self.stripes)

        self.ptSize = float(argv[4])

        self.typeFamily = argv[5]

        self.mag = float(argv[6])

        if 'TEXMFHOME' not in os.environ:
            printUsage(argv, 'TEXMFHOME environment variable is not set')
        self.texmfHome = os.environ['TEXMFHOME']

def callAndLog(args, log):
    try:
        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
        output = proc.stdout.read()
        if output != '':
            log.append(output)
    except subprocess.CalledProcessError:
        sys.exit('System died when calling {0}'.format(*args))

def createMFcontent(kind, style, stripes, sourceFont):
    styledict = { 'b' : '0', 'f' : '1',  'h' : '2' }
    text = '''% Copied from rtest on p.311 of the MetaFont book.
if unknown cmbase: input cmbase fi
mode_setup;
def generate suffix t = enddef;
input {0}; font_setup;
let iff = always_iff;
           
stripes:={1};
foreground:={2};
input zeroman{3};'''.format(sourceFont,
                      stripes,
                      styledict[style],
                      kind)
    return text

def createMFfiles(params):
    sourceFont = '{0}{1}'.format(params.typeFamily, int(params.ptSize))
    destMFdir = '{0}/fonts/source/public/zetex'.format(params.texmfHome)
    destMF = 'z{0}{1}{2}{3}'.format(params.kind,
                                    params.style,
                                    params.stripesAsLetter,
                                    sourceFont)
    destMFpath = '{0}/{1}.mf'.format(destMFdir, destMF)
    textMFfile = createMFcontent(params.kind,
                                 params.style,
                                 params.stripes,
                                 sourceFont)

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
            subprocess.check_output(['kpsewhich',
                                     '{0}.{1}pk'.format(destMF, dpi)])
        except subprocess.CalledProcessError:
            try:
                proc = subprocess.Popen(['kpsewhich',
                                         '{0}.600pk'.format(destMF)],
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True)
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

# TODO: Document
if __name__ == '__main__':
    parameters = Parameters(sys.argv)
    createMFfiles(parameters)
