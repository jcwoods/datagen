import os
import random
import sys
import sqlite3

from datagen.entitygenerator import DictElement


class SQLElement(DictElement):

    def __init__(self,
                 dataPath=None,
                 dataFile=None,
                 columns=None,
                 tableName=None,
                 keyCol='rowid',
                 **kwargs):
        '''
        Source data for a DictElement from a SQLite database.

        'dataFile' is the name of the SQLite database file.  This value MUST
        be provided.

        'dataPath' specifies the directory in which 'dataFile' may be found.
        If dataPath is not given, it will default to the 'data' directory
        immediately beneath the location of the package files.

        'columns' is a list of columns to include in the output.  If it is not
        specified, all columns except the keyCol will be output.

        'tableName' specifies the name of the table to be queried.

        'keyCol' is the name of the column containing the primary key.  This
        column must be a unique integer, and all values between 1..max(keyCol)
        are expected to be present.  If a value is missing, a new row will be
        selected.  While this does not result in an error, too many attempts
        to find a valid row could result in degraded performance.

        CAUTION:  do not allow external sources to provide 'tableName' or
                  'keyCol'.  These values are used to construct SQL
                  statements, and arbitrary values could be used to introduce
                  SQL injection attacks.
        '''

        DictElement.__init__(self, **kwargs)

        if dataFile is None:
            raise ValueError("dataFile must be provided.")

        if tableName is None:
            raise ValueError("tableName must be provided.")

        # defaults to package directory + '/data'
        if dataPath is None:
            dataPath = os.path.join(os.path.dirname(__file__), 'data')

        dbFile = os.path.join(dataPath, dataFile)

        db = sqlite3.connect(dbFile)
        self.db = db

        self.keyCol = keyCol
        self.tableName = tableName

        # load columns if not given
        if columns is None:
            # default to all except keyCol
            sql = "pragma table_info('{0:s}')"
            cur = db.execute(sql.format(tableName))
            columns = []
            for row in cur:
                if row[1] != keyCol:
                    columns.append(row[1])

        self.columns = columns

        # build the query we'll use to select unique rows.
        query = 'select {0:s} from {1:s} where {2:s} = ?'
        query = query.format(', '.join(columns), tableName, keyCol)
        self.query = query

        # how many entries in the database?
        rangeSql = 'select max({0:s}) from {1:s}'.format(keyCol, tableName)
        cur = db.execute(rangeSql)
        range = cur.fetchone()[0]
        self.maxRange = range

        return

    def create(self):
        r = int(random.random() * self.maxRange) + 1
        rset = self.db.execute(self.query, (r,))
        row = rset.fetchone()

        return dict(zip(self.columns, row))


def main(argv):
    se = SQLElement(dataFile='us_address.db',
                    keyCol='rowid',
                    tableName='us_address')

    print(str(se.create()))
    return


if __name__ == '__main__':
    sys.exit(main(sys.argv))
