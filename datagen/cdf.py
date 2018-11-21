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
