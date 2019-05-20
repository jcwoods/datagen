#!/usr/bin/python3

import sys
from bisect import bisect
from datagen.entitygenerator import EntityElement, SimpleElement
import random

class GenderElement(SimpleElement):
    def __init__(self, pctMale=0.50, **kwargs):

        SimpleElement.__init__(self, **kwargs)

        if pctMale < 0.0 or pctMale > 1.0:
            err = 'ERROR: invalid pctMale value: {0:s}'.format(str(pctMale))
            raise ValueError(err)

        self.pctMale = pctMale
        return

    def create(self, **kwargs):
        r = random.random()
        if r <= self.pctMale: return 'M'
        return 'F'


def main(argv):
    gender = GenderElement()
    print(gender.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
