#!/usr/bin/python3
# src/test/test_zebraFont.pyc

import unittest
import sys

sys.path.append('/home/mancilla/development/Zebrackets/src')

from zebrackets import *

full_cmd_1 = ['--type', 'b',
              '--style', 'b',
              '--stripes', '7',
              '--family', 'cmb',
              '--size', '10',
              '--texmfhome', '/home/mancilla',
              '--checkargs']

full_cmd_2 = ['--type', 'b',
              '--style', 'b',
              '--stripes', '5',
              '--family', 'cmb',
              '--size', '17', 
              '--texmfhome', '/home/mancilla',
              '--checkargs']


class TestZebraFont(unittest.TestCase):
    def setUp(self):
        pass

    ## Checking the argparse parametrization, no errors in command
    def test_zebrafont_cmd1(self):
        self.assertEqual(zebraFont.zebraFontParser(full_cmd_1), None)

    ## Checking the argparse parametrization, contradicting values
    # Invalid font, size pair
    def test_zebrafont_cmd2(self):
        self.assertIn(zebraFont.zebraFontParser(full_cmd_2),
            "Invalid input: Invalid font family-size pair")

    ## Checking the argparse parametrization, with --h
    # Argparse sends an error exit code, so we need to catch here
    def test_zebrafont_cmd3(self):
        try:
            self.assertEqual(zebraFont.zebraFontParser(['--h']), None)
        except:
            pass
#            print(sys.exc_info()[0])
#            print(sys.exc_info())

    ## Checking the argparse parametrization, with no values
    # Argparse raises an exception so we need to catch it here
    def test_zebrafont_noargs(self):
        try:
            zebraFont.zebraFontParser()
        except:
            pass

    ## Checking the actual call to create the fonts function
    # Invalid number of stripes
    def test_zebrafont_func_1(self):
        self.assertEqual(zebraFont.zebraFont(
            'b', 'b', '7', 'cmb', '17', '/home/mancilla', '1', '--checkargs'), 
            "Invalid input: Invalid number of stripes")


if __name__ == '__main__':
    unittest.main()
