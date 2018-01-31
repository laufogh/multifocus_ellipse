#!/usr/bin/env python3

import ellipse

import shutil, tempfile
import filecmp
import unittest

class EllipseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory before all the tests
        cls.test_dir = tempfile.mkdtemp()
        ellipse.create_drawings( cls.test_dir )

    @classmethod
    def tearDownClass(cls):
        # Remove the directory after all the tests
        shutil.rmtree( cls.test_dir )

    def _compare_one_file(self, filename):
        self.assertTrue(filecmp.cmp( 'examples/'+filename, self.test_dir+'/'+filename), msg=filename+" is ok")

    def test_three_foci_without_leftovers(self):
        self._compare_one_file('three_foci_without_leftovers.svg')

    def test_three_foci_with_leftovers(self):
        self._compare_one_file('three_foci_with_leftovers.svg')

    def test_four_foci_without_leftovers(self):
        self._compare_one_file('four_foci_without_leftovers.svg')

    def test_four_foci_with_leftovers(self):
        self._compare_one_file('four_foci_with_leftovers.svg')

    def test_seven_foci_different_slacks(self):
        self._compare_one_file('seven_foci_different_slacks.svg')

if __name__ == '__main__':
    unittest.main()
