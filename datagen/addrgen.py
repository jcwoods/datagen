#!/usr/bin/python3

import sys
import gzip
import json
import os
import random
import sqlite3

from datagen.entitygenerator import EntityElement, DictElement

class AddressElement(DictElement):
    def __init__(self, dataPath = None,
                       dataFile=None,
                       fields = [],
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        addrs = []
        nfields = len(fields)

        if dataPath is None:
            dataPath = os.path.join(os.path.dirname(__file__), 'data')

        f = gzip.open(os.path.join(dataPath, dataFile), 'r')
        for line in f:
            iline = line.decode('utf-8').rstrip('\r\n')
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
        r = int(random.random() * len(self.addrs))
        d = self.addrs[r]

        DictElement.addChildren(self, d, **kwargs)
        return d

class USAddress(AddressElement):
    def __init__( self, dataPath = None,
                        dataFile = 'us_addresses.dat.gz',
                        fields = [ 'street1', 'street2', 'street3',
                                   'city', 'state', 'postalcode' ],
                        **kwargs ):

        AddressElement.__init__(self, dataFile = dataFile,
                                      fields = fields,
                                      **kwargs)
        return



def main(argv):
    addr = USAddress()
    print(json.dumps(addr.create()))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
