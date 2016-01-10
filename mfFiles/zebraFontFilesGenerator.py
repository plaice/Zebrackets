#!/usr/bin/python3

# File zebraFontFilesGenerator.py
#
# Copyright (c) Blanca Mancilla, 2015
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

import os
import stat

file_content = '''#!/usr/bin/python3

# File zebraFontFiles.py
#
# Copyright (c) Blanca Mancilla, 2015
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
#
# This file is part of the zebrackets package
\n\n
'''

def build_str(str_name, str_content):
    return "{0} = '''{1}'''\n\n".format(str_name, str_content)

## Read in the files and create a string for each.
file_zepunctb = open('zepunctb.mf')
str_zepunctb = file_zepunctb.read()
file_zepunctb.close()
file_zepunctp = open('zepunctp.mf')
str_zepunctp = file_zepunctp.read()
file_zepunctp.close()
file_zeromanb = open('zeromanb.mf')
str_zeromanb = file_zeromanb.read()
file_zeromanb.close()
file_zeromanp = open('zeromanp.mf')
str_zeromanp = file_zeromanp.read()
file_zeromanp.close()

file_content += build_str('str_zepunctb', str_zepunctb)
file_content += build_str('str_zepunctp', str_zepunctp)
file_content += build_str('str_zeromanb', str_zeromanb)
file_content += build_str('str_zeromanp', str_zeromanp)

dest_file = '../src/zebrackets/zebraFontFiles.py'
with open(dest_file, 'w') as fontfile:
    fontfile.write(file_content)
os.chmod(dest_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                    stat.S_IRGRP | stat.S_IXGRP |
                    stat.S_IROTH | stat.S_IXOTH)
