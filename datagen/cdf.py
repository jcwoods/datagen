#!/usr/bin/python3


#   Copyright 2019 by Jeff Woods
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import bisect
import gzip
import random
import sys

class CDF(object):

    '''
    Select items with non-uniform distributions from a list.

    Input data file is expected to contain two columns (but may contain more):
    a name and a relative frequency.  As an example, given the input:

        JOHN     2.8
        ROBERT   1.4
        WILLIAM  0.7

    The name JOHN would be selected four times as often as WILLIAM and twice
    as often as ROBERT.

    Likewise,

        JOHN     0.6758
        ROBERT   0.6758
        WILLIAM  0.6758

    All three names would be selected at the same frequency (eg, they are
    uniformly distributed).
    
    There is no requirement on the range or sum of the frequency values.  All
    frequencies are relative.
    '''

    def __init__(self, dataFile, delimiter = None, isCumulative = False,
                       skipHeader = False, tagCol = 0, freqCol = 1, valType = None):
        '''
        Create a new CDF, loading distribution data from the named file.

        dataFile specifies the name of the file from which data will be read.
        Both compressed (gzip) and uncompressed files are supported.  The file
        must not contain a header row.

        If isCumulative is True, the frequency is taken as a cumulative
        distribution.  If it is false, the frequency column is read as a
        relative distribution.

        If delimiter is None (default), the rows will be split on groupings of
        whitespace.  Otherwise, the specified delimiter will be used.

        tagCol identifies the column (by index) which contains the item name.
        This is the value which will be returned by the search.  By default,
        this will be the first column.

        distCol identifies the column (by index) which contains the frequency
        distribution.
        '''

        self.cumdist = []
        self.values = []

        self.range = 0.0

        if self._is_gzip(dataFile):
            f = gzip.open(dataFile, 'r')
        else:
            f = open(dataFile, 'rb')

        if skipHeader: line = f.readline()
        for data in f:

            try:
                line = data.decode('utf-8')
                fields = line.strip().split(delimiter)
                tag = str(fields[tagCol])
                freq = float(fields[freqCol])
            except UnicodeError:
                continue

            if isCumulative:
                if freq < self.range:
                    raise RuntimeError('cumulative distributions are not sorted!')

                self.range = freq
            else:
                if freq == 0.0: continue
                self.range += freq

            if valType is not None:
                if valType == 'int':
                    tag = int(tag)

            self.values.append(tag if tag != "" else None)
            self.cumdist.append(self.range)

        f.close()
        return

    @staticmethod
    def _is_gzip(file):
        '''
        Returns True if the named file is gzip compressed.
        '''

        f = open(file, 'rb')
        hdr = f.read(2)
        f.close()

        return True if hdr == b'\x1f\x8b' else False

    def getValue(self, r = None):
        '''
        Select a random value.
        
        If provided, 'r' must be in the range 0 <= r < 1.  If r is not
        provided, the standard random library will be used.
        '''

        if r is None: r = random.random()

        r *= self.range
        pos = bisect.bisect(self.cumdist, r)
        return self.values[pos]


def main(argv):
    delimiter = None
    if (len(argv) == 3): delimiter = argv[2]

    cdf = CDF(argv[1], delimiter = delimiter)

    for n in range(10):
        print('{0:d}: {1:s}'.format(n, cdf.getValue()))

    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )

