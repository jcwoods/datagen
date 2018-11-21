#!/usr/bin/python3

import sys
import gzip
import os
import random
from bisect import bisect

class CDF(object):

    '''
    Implements a simple class which loads a set of values that occur with
    dissimilar frequencies.
    '''

    def __init__(self, dataPath=None, dataFile=None, delimiter=None,
                       labelPos=0, weightPos=1, isCumulative=True):
        '''
            dataPath:      location (path) of the data files to be loaded.
                           If None, defaults to the location of this
                           module + "/data".
            dataFile:      the name of the file to be loaded.
            delimiter:     the delimiter which separates fields in dataFile.
                           If None, whitespace will be used.
            labelPos:      the position (0-based) of the label field.  This
                           is the value which will be returned by getValue().
            weightPos:     the weight associated with the label.  This may be
                           absolute/relative or cumulative.
            isCumulative:  if False, weights are absolute/relative.  If True,
                           weights are cumulative and must be given in sorted
                           (ascending) order.
        '''

        self.cumweight = []
        self.labels = []

        self.maxweight = 0.0

        # dataPath defaults to "$PWD/data" if not given
        if dataPath is None:
            p = os.path.dirname(__file__)
            dataPath = os.path.join(p, 'data')

        if dataFile is None:
            raise ValueError("dataFile parameter must be provided")

        dataFile = os.path.join(dataPath, dataFile)

        if self.isGzip(dataFile):
            f = gzip.open(dataFile, 'r')
        else:
            f = open(dataFile, 'r')

        for line in f:
            fields = line.decode('utf-8').strip().split(delimiter)
            self.labels.append(fields[labelPos])

            weight = float(fields[weightPos])
            if isCumulative:
                self.maxweight = weight
            else:
                self.maxweight += weight

            self.cumweight.append(self.maxweight)

        f.close()

        #print("maxweight: " + str(self.maxweight))
        #print("labels: " + str(self.labels))
        #print("cumweight: " + str(self.cumweight))
        
        return

    @staticmethod
    def isGzip(file):
        with open(file, "rb") as fd:
            b = fd.read(3)
            if b == b"\x1f\x8b\x08":
                return True

        return False

    def getValue(self):
        r = random.random() * self.maxweight
        pos = bisect(self.cumweight, r)
        return self.labels[pos]

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

        counts   = { "CHARLES": 0,
                     "DAVID": 0,
                     "JAMES": 0,
                     "JOHN": 0,
                     "JOSEPH": 0,
                     "MICHAEL": 0,
                     "RICHARD": 0,
                     "ROBERT": 0,
                     "THOMAS": 0,
                     "WILLIAM": 0 }

        for i in range(250):
            n = cdf.getValue()
            counts[n] += 1

        # make sure we get expected counts
        for k in expected.keys():
            self.assertTrue(expected[k] == counts[k])

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

        counts   = { "CHARLES": 0,
                     "DAVID": 0,
                     "JAMES": 0,
                     "JOHN": 0,
                     "JOSEPH": 0,
                     "MICHAEL": 0,
                     "RICHARD": 0,
                     "ROBERT": 0,
                     "THOMAS": 0,
                     "WILLIAM": 0 }

        for i in range(250):
            n = cdf.getValue()
            counts[n] += 1

        # make sure we get expected counts
        for k in expected.keys():
            self.assertTrue(expected[k] == counts[k])

        return



if __name__ == '__main__':
    unittest.main()