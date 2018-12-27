#!/usr/bin/python3

from datagen.cdf import CDF

import os
import random
import unittest


class TestCDF(unittest.TestCase):

    seed = 1

    def setUp(self):
        random.seed(TestCDF.seed)  # for test, use the same seed every time!!
        self.test_data_path = os.path.join(os.path.dirname(__file__), "testdata")

    def test_compressed(self):
        dfile = os.path.join(self.test_data_path, "is_gzip.gz")
        self.assertTrue(CDF.isGzip(dfile))

    def test_uncompressed(self):
        dfile = os.path.join(self.test_data_path, "not_gzip.dat")
        self.assertFalse(CDF.isGzip(dfile))

    def test_random(self):
        '''
        Our tests depend on the random number generator behaving as it has
        previously.  Let's check.  If this test fails, most of what follows
        will also fail.
        '''

        expected = [ 0.13436424411240122,
                     0.8474337369372327,
                     0.763774618976614,
                     0.2550690257394217,
                     0.49543508709194095 ]

        # random.seed(TestCDF.seed)

        for n in expected:
            self.assertTrue(n == random.random())

    def test_relative(self):
        cdf = CDF(dataPath = self.test_data_path,
                  dataFile = 'data_relative.csv',
                  delimiter = '|',
                  labelPos = 0,
                  weightPos = 1,
                  isCumulative = False)

        expected = { "CHARLES": 24,
                     "DAVID": 22,
                     "JAMES": 35,
                     "JOHN": 38,
                     "JOSEPH": 12,
                     "MICHAEL": 32,
                     "RICHARD": 17,
                     "ROBERT": 31,
                     "THOMAS": 13,
                     "WILLIAM": 26 }

        for i in range(250):
            n = cdf.getValue()
            expected[n] -= 1

        # make sure we get expected counts
        for k in expected.keys():
            self.assertTrue(expected[k] == 0)

        return

    def test_cumulative(self):
        cdf = CDF(dataPath = self.test_data_path,
                  dataFile = 'data_cumulative.csv',
                  delimiter = '|',
                  labelPos = 0,
                  weightPos = 1,
                  isCumulative = True)

        expected = { "CHARLES": 24,
                     "DAVID": 22,
                     "JAMES": 35,
                     "JOHN": 38,
                     "JOSEPH": 12,
                     "MICHAEL": 32,
                     "RICHARD": 17,
                     "ROBERT": 31,
                     "THOMAS": 13,
                     "WILLIAM": 26 }

        for i in range(250):
            n = cdf.getValue()
            expected[n] -= 1

        # make sure we get expected counts
        for k in expected.keys():
            self.assertTrue(expected[k] == 0)

        return


if __name__ == '__main__':
    unittest.main()
