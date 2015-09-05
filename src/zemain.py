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


# TODO: The manipulation of the parameters is now done.
#       It is now time to deal with the calling infrastructure.
#       Basically, from here, we call zebraFont or zebraFilter.
#       Could we put the code in this file, and not need
#       calling infrastructure?

import copy, io, math, os, re, subprocess, sys

# TODO: Document
class Params:
    def __init__(self):
        self.style = ''
        self.numerator = ''
        self.denominator = ''
        self.encoding = ''
        self.size = ''
        self.family = ''
        self.kind = ''
        self.stripes = ''
        self.index = ''
        self.mag = ''
        self.filterMode = False

# TODO: Document
def setDefaults(defaults, params, args):
    m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
    if m:
        defaults.style = m.group(1)
    m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
    if m:
        defaults.numerator = m.group(1)
    m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
    if m:
        defaults.denominator = m.group(1)
    m = re.search(r'enc\w*=(\w+)[,\]]', args)
    if m:
        defaults.encoding = m.group(1)
    m = re.search(r'siz\w*=(\d+)[,\]]', args)
    if m:
        defaults.size = m.group(1)
    m = re.search(r'fam\w*=(\w+)[,\]]', args)
    if m:
        defaults.family = m.group(1)
    m = re.search(r'str\w*=(\d+)[,\]]', args)
    if m:
        defaults.stripes = m.group(1)
    m = re.search(r'typ\w*=([bp])\w+[,\]]', args)
    if m:
        defaults.kind = m.group(1)
    m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
    if m:
        defaults.mag = m.group(1)
    m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
    if m:
        defaults.index = m.group(1)
        if (defaults.index == 'b'):
            defaults.index = -3
        elif (defaults.index == 'd'):
            defaults.index = -2
        else:
            defaults.index = -1

# TODO: Document
def declareFont(defaults, params, args):
     m = re.search(r'typ\w*=([bp])\w*[,\]]', args)
     if m:
         kind = m.group(1)
     else:
         kind = defaults.kind
     m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
     if m:
         style = m.group(1)
     else:
         style = defaults.style
     m = re.search(r'str\w*=(\d+)[,\]]', args)
     if m:
         stripes = m.group(1)
     else:
         stripes = defaults.stripes
     m = re.search(r'siz\w*=(\d+)[,\]]', args)
     if m:
         size = m.group(1)
     else:
         size = defaults.size
     m = re.search(r'fam\w*=(\w+)[,\]]', args)
     if m:
         family = m.group(1)
     else:
         family = defaults.family
     m = re.search(r'mag\w*=(\d+(\.\d+)*)[,\]]', args)
     if m:
         mag = math.sqrt(float(m.group(1)))
     elif (defaults.mag != ''):
         mag = math.sqrt(float(defaults.mag))
     else:
         mag = 1.0
     try:
         subprocess.check_output(['./zebraFont.py',
                                  kind,
                                  style,
                                  str(stripes),
                                  str(size),
                                  family,
                                  str(mag)])
     except subprocess.CalledProcessError:
         pass


# TODO: Document
def beginZebrackets(defaults, params, args):
     m = re.search(r'sty\w*=([bfh])\w*[,\]]', args)
     if m:
         params.style = m.group(1)
     else:
         params.style = defaults.style
     m = re.search(r'ind\w*=([bdu])\w*[,\]]', args)
     if m:
         params.index = m.group(1)
         if params.index == 'b':
             params.index = -3
         elif params.index == 'd':
             params.index = -2
         else:
             params.index = -1
     else:
         params.index = defaults.index
     m = re.search(r'num\w*=([-]?\d+)[,\]]', args)
     if m:
         params.numerator = m.group(1)
     else:
         params.numerator = defaults.numerator
     m = re.search(r'den\w*=([-]?\d+)[,\]]', args)
     if m:
         params.denominator = m.group(1)
     else:
         params.denominator = defaults.denominator
     m = re.search(r'enc\w*=(\w+)[,\]]', args)
     if m:
         params.encoding = m.group(1)
     else:
         params.encoding = defaults.encoding
     m = re.search(r'siz\w*=(\d+)[,\]]', args)
     if m:
         params.size = m.group(1)
     else:
         params.size = defaults.size
     m = re.search(r'fam\w*=(\w+)[,\]]', args)
     if m:
         params.family = m.group(1)
     else:
         params.family = defaults.family
     m = re.search(r'mag\w*=(\w+)[,\]]', args)
     if m:
         params.mag = m.group(1)
     elif defaults.mag == '':
         params.mag = 1.0
     else:
         params.mag = defaults.mag
     if params.numerator == '':
         params.numerator = params.index
     if params.denominator == '':
         params.denominator = -1
     params.filterMode = True
     params.buf = io.StringIO()

# TODO: Document
# TODO: How do we pass the input to this program?
def endZebrackets(defaults, params):
#      system "cat /tmp/ze-sub_buf | $cbindir/zebrackets $style $numerator $denominator $encoding $size $family > /tmp/ze-sub_buf-out";
     string = params.buf.getvalue()
     proc = subprocess.Popen(['./zebraFilter.py',
                              params.style,
                              str(params.numerator),
                              str(params.denominator),
                              params.encoding[0],
                              str(params.size),
                              params.family],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
     proc.stdin.write(string)
     proc.stdin.close()
     defaults.buf.write(proc.stdout.read())
     params.buf.close()
     params.filterMode = False

# TODO: Document
def filterText(defaults, params):
    defaults.buf = io.StringIO()
    params.filterMode = False
    for line in sys.stdin:
        if not params.filterMode:
            m = re.search(r'^\\zebracketsdefaults(\[.*\])', line)
            if m:
                setDefaults(defaults, params, m.group(1))
                continue
            m = re.search(r'^\\zebracketsfont(\[.*\])', line)
            if m:
                declareFont(defaults, params, m.group(1))
                continue
            m = re.search(r'^\\begin{zebrackets}(\[.*])', line)
            if m:
                beginZebrackets(defaults, params, m.group(1))
                continue
            # Process a normal line
            defaults.buf.write(line)
        else:
            m = re.search(r'^\\end{zebrackets}', line)
            if m:
                endZebrackets(defaults, params)
                continue
            # Process a normal line
            params.buf.write(line)
    print(defaults.buf.getvalue(), end='')
    defaults.buf.close()

if __name__ == '__main__':
    if 'TEXMFHOME' not in os.environ:
       sys.exit('TEXMFHOME environment variable is not set')
    texmfHome = os.environ['TEXMFHOME']
    scriptHome = texmfHome + '/scripts/zetex/python'

    defaults = Params()   
    params = copy.copy(defaults)
    filterText(defaults, params)
