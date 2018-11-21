#!/usr/bin/python3

import sys
from entitygenerator import EntityElement, SimpleElement

class PhoneElement(SimpleElement):
    def __init__(self, **kwargs):
        SimpleElement.__init__(self, **kwargs)
        return

    def create(self, **kwargs):
        r = int(EntityElement.pool.next() * 10000000000)
        p = '{0:010d}'.format(r)
        return p

def main(argv):
    phone = PhoneElement()
    print(phone.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
