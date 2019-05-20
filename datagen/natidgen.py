#!/usr/bin/python3

import random
import sys
from datagen.entitygenerator import EntityElement, SimpleElement

class NationalIDElement(SimpleElement):
    def __init__(self,
                 useDashes = False,
                 pctPresent = 1.0,
                 **kwargs):

        SimpleElement.__init__(self, **kwargs)
        self.useDashes = useDashes
        self.pctPresent = pctPresent
        return

    def create(self, **kwargs):

        if random.random() >= self.pctPresent:
            return None

        # area cannot be 000, 666, or 900-999.
        while True:
            area = int(random.random() * 899) + 1  # 001 .. 899
            if area not in [0, 666]: break

        # group cannot be 00
        while True:
            group = int(random.random() * 99) + 1  # 01 .. 99
            if group != 0: break

        # serial cannot be 0000
        while True:
            ser = int(random.random() * 9999) + 1  # 0001 .. 9999
            if ser != 0: break

        if self.useDashes:
            return '{0:03d}-{1:02d}-{2:04d}'.format(area, group, ser)

        return '{0:03d}{1:02d}{2:04d}'.format(area, group, ser)


def main(argv):
    ssn = NationalIDElement()
    print(ssn.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
