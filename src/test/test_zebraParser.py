#!/usr/bin/python3
# src/test/test_zebraParser.py

import unittest
import sys

sys.path.append('/home/mancilla/development/Zebrackets/src')

from zebrackets import *

#full_cmd_1 = ['--input', 'somefile',
full_cmd_1 = ['-i', 'somefile',
              '--output', 'otherfile',
              '--checkargs']

full_cmd_2 = ['--input', 'somenonfile',
              '--output', 'otherfile',
              '--texmfhome', '/home/mancilla/development/Zebrackets/src/test',
              '--checkargs']

full_cmd_3 = ['--input', 'somefile.zetex',
              '--texmfhome', '/home/other',
              '--checkargs']

full_cmd_4 = ['--input', 'somefile.zetex',
              '--checkargs']

full_cmd_5 = ['--input', 'somefile.zetex',
              '--texmfhome', '/home/mancilla/development/Zebrackets/src/test',
              '--checkargs']


def begin_test(name):
    print()
    print(70*'=')
    print("On test: " + name)
    print()

class TestZebraParser(unittest.TestCase):
    def setUp(self):
        pass

    ## Checking the argparse parametrization, no errors in command
    def test_zebraparser_cmd1(self):
        begin_test("test_zebraparser_cmd1")
        self.assertEqual(
            zebraParser.zebraParserParser(full_cmd_1), 
            'Invalid input file: zetex extension required.')

    ## Checking the argparse parametrization, checking for file extensions
    def test_zebraparser_cmd2(self):
        begin_test("test_zebraparser_cmd2")
        try:
          self.assertIn(zebraParser.zebraParserParser(full_cmd_2), None)
        except:
            pass

    def test_zebraparser_cmd3(self):
        begin_test("test_zebraparser_cmd3")
        self.assertEqual(
            zebraParser.zebraParserParser(full_cmd_3),
            "Invalid texmf, path is not a directory.")

    def test_zebraparser_cmd4(self):
        begin_test("test_zebraparser_cmd4")
        self.assertEqual(
            zebraParser.zebraParserParser(full_cmd_4),
            "TEXMFHOME environment variable is not set.")

    def test_zebraparser_cmd5(self):
        begin_test("test_zebraparser_cmd5")
        self.assertEqual(zebraParser.zebraParserParser(full_cmd_5), None)

    ## Checking the argparse parametrization, with --h
    # Argparse sends an error exit code, so we need to catch here
    def test_zebraparser_cmd0(self):
        begin_test("test_zebraparser_cmd0")
        try:
            self.assertEqual(zebraParser.zebraParserParser(['--h']), None)
        except:
            pass
#            print(sys.exc_info()[0])
#            print(sys.exc_info())

    ## Checking the argparse parametrization, with no values
    # Argparse raises an exception so we need to catch it here
    def test_zebraparser_noargs(self):
        begin_test("test_zebraparser_noargs")
        try:
            zebraParser.zebraParserParser()
        except:
            pass

if __name__ == '__main__':
    unittest.main()
