#!/usr/bin/python3

import sys
import json
import gzip
from bisect import bisect
import random

from datagen.entitygenerator import EntityGenerator, DictElement
from datagen.cdf import CDF

class USCensusName(DictElement):
    def __init__(self, male = "male.dat.gz",
                       female = "female.dat.gz",
                       surname = "surname.dat.gz",
                       order=None,           # output order of full name (one
                                             #   of None, LFM, or FML).
                       pctMidName=1.0,       # percentage of names which have
                                             #   a middle name (0..1).
                       pctMidInitial=0.0,    # of the names which have a mid
                                             #   name, how many of those give
                                             #   only an initial (0..1)
                       pctFirstInitial=0.0,  # percentage of first names which
                                             #   only a first initial
                       **kwargs):

        DictElement.__init__(self, **kwargs)

        self.male = CDF(dataFile = male, delimiter="|", labelPos = 0, weightPos = 1, isCumulative = True)
        self.female = CDF(dataFile = female, delimiter="|", labelPos = 0, weightPos = 1, isCumulative = True)
        self.surname = CDF(dataFile = surname, delimiter="|", labelPos = 0, weightPos = 1, isCumulative = True)

        self.order = order
        self.pctMidName = pctMidName
        self.pctMidInitial = pctMidInitial
        self.pctFirstInitial = pctFirstInitial
        return

    def create(self, gender = None, **kwargs):

        # If we have a path to Gender (as a parameter), we'll use it over an
        # explicitly given gender.
        if self.params is not None:
            gender_path = self.params.get('gender')
            if gender_path is not None:
                gender = self.root.getValueByPath(gender_path)

        if gender is None:
            fn_gen = self.male.getName
            if random.random() < 0.5:
                 fn_gen = self.female.getName
        elif gender.lower() in ['m', 'male'] :
            fn_gen = self.male.getName
        elif gender.lower() in ['f', 'female'] :
            fn_gen = self.female.getName
        else:
            raise ValueError('Invalid gender: {0:s}'.format(gender))

        first = fn_gen()

        last = self.surname.getName()

        if random.random() < self.pctMidName:
            middle = fn_gen()
        else:
            middle = None

        if self.order is "LFM":
            if middle is not None:
                full = '{0:s} {1:s} {2:s}'.format(last, first, middle)
            else:
                full = '{0:s} {1:s}'.format(last, first)
        elif self.order is "FML":
            if middle is not None:
                full = '{0:s} {1:s} {2:s}'.format(first, middle, last)
            else:
                full = '{0:s} {1:s}'.format(first, last)
        else:
            full = None

        r = { 'first': first, 'last': last }
        if middle is not None: r['middle'] = middle
        if full is not None:   r['full'] = full

        DictElement.addChildren(self, r, **kwargs)
        return r


def main(argv):
    name = USCensusName()
    print(json.dumps(name.create()))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
