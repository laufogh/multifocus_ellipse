#!/usr/bin/env python3

import ellipse

import shutil, tempfile
import filecmp
import unittest

class EllipseTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_recreate_and_compare_examples(self):
        ellipse.create_drawings( self.test_dir )
        for filename in ['three_foci_without_leftovers.svg', 'three_foci_with_leftovers.svg', 'four_foci_without_leftovers.svg', 'four_foci_with_leftovers.svg', 'seven_foci_different_slacks.svg']:
            self.assertTrue(filecmp.cmp( 'examples/'+filename, self.test_dir+'/'+filename))

if __name__ == '__main__':
    unittest.main()
