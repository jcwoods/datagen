#!/usr/bin/python3

import sys
import gzip
import json
import os
import random
import sqlite3

from datagen.entitygenerator import EntityElement, DictElement

class AddressFile(DictElement):
    def __init__(self, datapath=None,
                       dataFile=None,
                       fields = [],
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        if datapath is None:
            p = os.path.dirname(__file__)
            datapath = os.path.join(p, 'data')

        if datapath is not None:
            dataFile = os.path.join(datapath, dataFile)

        addrs = []
        nfields = len(fields)

        f = gzip.open(dataFile, 'rt', encoding='utf-8')
        for line in f:
            cols = line.strip().split('|')
            if len(cols) != nfields:
                print("Invalid number of fields in address: " + line)
                continue

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

class AddressDB(DictElement):
    '''
    Implements support for pulling addresses from a SQLite database.
    '''

    @staticmethod
    def sqlite_dict_factory(c, r):
        '''
        Converts a row returned from SQLite to a dict()
        '''

        d = {}
        for idx, col in enumerate(c.description):
            d[col[0]] = r[idx]

        return d

    def __init__(self, datapath = None,
                       dbFile=None,
                       rownum_col=None,
                       table_name=None,
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        if datapath is None:
            p = os.path.dirname(__file__)
            datapath = os.path.join(p, 'data')

        if datapath is not None:
            dbFile = os.path.join(datapath, dbFile)

        db = sqlite3.connect(dbFile)
        cursor = db.cursor()

        min_sql = 'select min({0:s}) from {1:s}'.format(rownum_col, table_name)
        cursor.execute(min_sql)
        self.min_recno = cursor.fetchone()[0]

        max_sql = 'select max({0:s}) from {1:s}'.format(rownum_col, table_name)
        cursor.execute(max_sql)
        self.max_recno = cursor.fetchone()[0]

        #print("min(recno): " + str(self.min_recno))
        #print("max(recno): " + str(self.max_recno))

        cursor.row_factory = AddressDB.sqlite_dict_factory

        sql = 'select * from {0:s} where {1:s} = ?'.format(table_name,
                                                           rownum_col)

        self.rownum_col = rownum_col
        self.table_name = table_name
        self.query_sql = sql
        self.cursor = cursor
        self.db = db
        return

    def create(self, **kwargs):

        # select a random record between min_recno and max_recno (inclusive)
        r = int(random.random() * (self.max_recno - self.min_recno + 1)) + self.min_recno
        d = self.cursor.execute(self.query_sql, (r, )).fetchone()

        # remove the rownum column
        del(d[self.rownum_col])

        DictElement.addChildren(self, d, **kwargs)
        return d

class USAddress(AddressFile):
    def __init__( self, dataFile = 'us_addresses.dat.gz',
                        fields = [ 'street1', 'city', 'state', 'postalcode', 'lat', 'lon' ],
                        **kwargs ):

        AddressFile.__init__(self, dataFile = dataFile,
                                   fields = fields,
                                   **kwargs)
        return


class USAddressDB(AddressDB):
    def __init__( self, dbFile = 'us_addresses_10k.db',
                        rownum_col = 'recno',
                        table_name = 'us_addresses',
                        **kwargs ):

        AddressDB.__init__(self, dbFile = dbFile,
                                 rownum_col=rownum_col,
                                 table_name=table_name,
                                 **kwargs)
        return


def main(argv):
    addr = USAddressDB()

    for i in range(10):
        print(json.dumps(addr.create()))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
