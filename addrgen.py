#!/usr/bin/python3

import sys
import json
import sqlite3

from entitygenerator import EntityElement, DictElement

class AddressElement(DictElement):
    def __init__(self, dataFile=None,
                       table = None,
                       id_col = None,
                       fields = [],
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        con = sqlite3.connect(dataFile)

        cur = con.cursor()
        cur.execute('select min(id), max(id) from addresses')

        min_id, max_id = cur.fetchone()

        con.row_factory = sqlite3.Row
        self.con = con
        self.min_id = int(min_id)
        self.max_id = int(max_id)
        self.range_id = self.max_id - self.min_id
        self.table = table
        self.fields = fields

        cols = ', '.join(fields)
        self.sql = 'select {0:s} from {1:s} where {2:s} = ?'.format(cols,
                                                                    table,
                                                                    id_col)
        return

    def create(self, **kwargs):
        r = int(EntityElement.pool.next() * self.range_id) + self.min_id
        cur = self.con.cursor()
        cur.execute(self.sql, (r,))
        row = cur.fetchone()

        d = {}
        for col in row.keys():
            d[col] = row[col]

        DictElement.addChildren(self, d, **kwargs)
        return d

    def dumpAsCSV(self):
        '''
        A utility method which can be used to dump the SQLite database
        to a text format.  This method intended to help with transition
        to a plain text (vs binary database) address file.
        '''

        cols = ', '.join(self.fields)
        sql = 'select {0:s} from {1:s}'.format(cols, self.table)

        cur = self.con.cursor()
        cur.execute(sql)
        
        for row in cur:
            print('|'.join(row))

class USAddress(AddressElement):
    def __init__( self, dataFile = 'data/us_addresses.db',
                        table = 'addresses',
                        id_col = 'id',
                        fields = [ 'street1', 'street2', 'street3',
                                   'city', 'state', 'postalcode' ],
                        **kwargs ):

        AddressElement.__init__(self, dataFile = dataFile,
                                      table = table,
                                      id_col = id_col,
                                      fields = fields,
                                      **kwargs)
        return



def main(argv):
    addr = USAddress()

    if len(argv) > 1 and argv[1] == '--dump':
        addr.dumpAsCSV()
        return 0

    print(json.dumps(addr.create()))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
