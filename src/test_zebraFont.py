import unittest
import sys
from unittest.mock import patch


import zebraFont

HelpStringUsage = '''usage: zebraFont.py [-h] --type {b,p} --style {b,f,h} --stripes
                    {0,1,2,3,4,5,6,7} --size {5,6,7,8,9,10,12,17} --family
                    {cmb,cmbtt,cmbx,cmbxsl,cmdunh,cmff,cmfib,cmr,cmsl,cmsltt,cmss,cmssbx,cmssdc,cmssi,cmssq,cmssqi,cmtt,cmttb,cmvtt}
                    [--mag MAG] [--texmfhome TEXMFHOME] [--checkargs]
zebraFont.py: error: argument --type is required
'''

HelpString = '''usage: zebraFont.py [-h] --type {b,p} --style {b,f,h} --stripes
                    {0,1,2,3,4,5,6,7} --size {5,6,7,8,9,10,12,17} --family
                    {cmb,cmbtt,cmbx,cmbxsl,cmdunh,cmff,cmfib,cmr,cmsl,cmsltt,cmss,cmssbx,cmssdc,cmssi,cmssq,cmssqi,cmtt,cmttb,cmvtt}
                    [--mag MAG] [--texmfhome TEXMFHOME] [--checkargs]

Build a zebrackets font.

optional arguments:
  -h, --help            show this help message and exit
  --type {b,p}          b = bracket, p = parenthesis
  --style {b,f,h}       b = background, f = foreground, h=hybrid
  --stripes {0,1,2,3,4,5,6,7}
                        number of stripes in brackets
  --size {5,6,7,8,9,10,12,17}
                        font size
  --family
{cmb,cmbtt,cmbx,cmbxsl,cmdunh,cmff,cmfib,cmr,cmsl,cmsltt,cmss,cmssbx,cmssdc,cmssi,cmssq,cmssqi,cmtt,cmttb,cmvtt}
                        font family
  --mag MAG             magnification
  --texmfhome TEXMFHOME
                        substitute for variable TEXMFHOME
  --checkargs           check validity of input arguments

'''

full_cmd_1 = ['--type', 'b', '--style', 'b', '--stripes', '7', '--family', 'cmb',
    '--size', '10',  '--texmfhome', '/home/mancilla', '--checkargs']
full_cmd_2 = ['--type', 'b', '--style', 'b', '--stripes', '5', '--family', 'cmb',
    '--size', '17',  '--texmfhome', '/home/mancilla', '--checkargs']


class TestZebraFont(unittest.TestCase):
#    def setUp(self):
#        self.parser = zebraFont.zebraFontParser()

    def test_zebrafont_0(self):
        self.assertEqual(zebraFont.zebraFontParser(full_cmd_1), None)
        
    def test_zebra_font_1(self):
        self.assertEqual(zebraFont.zebraFontParser(full_cmd_2), None)
        
    def test_zebra_font_2(self):
        self.assertEqual(zebraFont.zebraFont(
            'b', 'b', '7', 'cmb', '17', '/home/mancilla', '1', '--checkargs'), False)

    def test_zebra_font_3(self):
        mock.parser = zebraFont.zebraFontParser



    '''
    def test_zebra_font_4(self):
        with patch.object(sys, 'argv', full_cmd_2):
            things = zebraFont.zebraFontParser()
            print("Inside with: %s" % things)
            assert(things == full_cmd_2)
        print("Outside with: %s" % zebraFont.zebraFontParser())
'''

#        self.assertEqual(zebraFont.zebraFontParser(['--h']), None)
#        self.assertIn('usage: zebraFont.py', zebraFont.zebraFontParser())
#        self.assertMultiLineEqual(zebraFont.zebraFontParser(), HelpStringUsage)
#        self.assertEqual(zebraFont.zebraFontParser(['--h']), HelpString)


if __name__ == '__main__':
#    unittest.main()
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestZebraFont)
    runner.run(itersuite)
