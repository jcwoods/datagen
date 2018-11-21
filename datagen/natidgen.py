#!/usr/bin/python3

import random
import sys

from entitygenerator import EntityElement, SimpleElement

class NationalIDElement(SimpleElement):
    def __init__(self,
                 useDashes = False,
                 **kwargs):

        SimpleElement.__init__(self, **kwargs)
        self.useDashes = useDashes
        return

    def create(self, **kwargs):

        # area cannot be 000, 666, or 900-999.
        while True:
            area = int(random.random() * 899) + 1  # 001 .. 899
            if area != 666: break

        # group cannot be 00
        group = int(random.random() * 99) + 1                 # 01 .. 99

        # serial cannot be 0000
        ser = int(random.random() * 9999) + 1                 # 0001 .. 9999

        if self.useDashes:
            return '{0:03d}-{1:02d}-{2:04d}'.format(area, group, ser)

        return '{0:03d}{1:02d}{2:04d}'.format(area, group, ser)



def main(argv):
    ssn = NationalIDElement()
    print(ssn.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
