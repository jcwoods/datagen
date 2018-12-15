#!/usr/bin/python3

import sys
import json

from datagen.sqlelement import SQLElement

class USAddress(SQLElement):
    def __init__(self,
                 dataFile = 'us_address_2pct.db',
                 tableName = 'us_address',
                 **kwargs):

        SQLElement.__init__(self,
                            dataFile = dataFile,
                            tableName = tableName,
                            **kwargs)
        return


def main(argv):
    addr = USAddress()
    print(json.dumps(addr.create()))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
