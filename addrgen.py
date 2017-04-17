#!/usr/bin/python3

import sys
import gzip
import json
import sqlite3

from entitygenerator import EntityElement, DictElement

class AddressElement(DictElement):
    def __init__(self, dataFile=None,
                       fields = [],
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        addrs = []
        nfields = len(fields)

        f = gzip.open(dataFile, 'r')
        for line in f:
            iline = line.decode('utf-8')
            cols = iline.split('|')
            if len(cols) != nfields:
                print("Invalid number of fields in address: " + line)
                sys.exit(1)

            d = {}
            n = 0
            for field in fields:
                d[field] = cols[n]
                n += 1

            addrs.append(d)

        f.close()


        self.fields = fields
        self.addrs = addrs

        return

    def create(self, **kwargs):
        r = int(EntityElement.pool.next() * len(self.addrs))
        d = self.addrs[r]

        DictElement.addChildren(self, d, **kwargs)
        return d

class USAddress(AddressElement):
    def __init__( self, dataFile = 'data/us_addresses.dat.gz',
                        fields = [ 'street1', 'street2', 'street3',
                                   'city', 'state', 'postalcode' ],
                        **kwargs ):

        AddressElement.__init__(self, dataFile = dataFile,
                                      fields = fields,
                                      **kwargs)
        return



def main(argv):
    addr = USAddress()

    for i in range(10):
        print(json.dumps(addr.create()))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
