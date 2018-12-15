#!/usr/bin/python3

#   Copyright 2018 by Jeff Woods
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

import sys
import gzip
import csv
import json
import random
import os

from datagen.entitygenerator import DictElement


class TradeElement(DictElement):
    def __init__(self, dataPath=None,
                 dataFile=None,
                 countryFilter=None,
                 **kwargs):

        DictElement.__init__(self, **kwargs)

        trades = []
        fields = None

        if dataPath is None:
            dataPath = os.path.join(os.path.dirname(__file__), 'data')
    
        dataFile = os.path.join(dataPath, dataFile) 

        f = gzip.open(dataFile, 'rt', encoding='utf-8')

        # dictreader defaults to using first row as header (good!!)
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for d in reader:
            if countryFilter is not None:
                if d['country'] not in countryFilter:
                    continue

            trades.append(d)

        f.close()

        self.fields = fields
        self.trades = trades
        return

    @staticmethod
    def digits_of(number):
        return [int(i) for i in str(number)]

    @staticmethod
    def luhn_checksum(card_number):
        digits = TradeElement.digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for digit in even_digits:
            total += sum(TradeElement.digits_of(2 * digit))
        return total % 10

    @staticmethod
    def is_luhn_valid(card_number):
        return TradeElement.luhn_checksum(card_number) == 0

    def create(self):
        r = int(random.random() * len(self.trades))
        d = self.trades[r].copy()

        iin_start = int(d['iin_start'])
        iin_end = d['iin_end']
        iin_end = int(iin_end) if iin_end is not '' else iin_start
        iin_range = iin_end - iin_start

        if iin_start == iin_end:
            r = 0
        else:
            rnd = random.random()
            r = int(rnd * (iin_range + 1))

        iin = iin_start + r
        iin = str(iin)

        if d['number_length'] is not "":
            acct_len = int(d['number_length'])
        else:
            acct_len = 16
            if d['scheme'] == 'AMEX':
                acct_len = 15

        # lots of fields... don't need them all.
        for key in ['iin_start', 'iin_end', 'bank_logo', 'number_length',
                    'bank_url', 'bank_city']:
            del(d[key])

        # build the random account number
        n = acct_len - 6 - 1   # less BIN number and Luhn check digit
        acct = iin + str(int(random.random() * (10 ** n))).zfill(n)
        acct += str(self.luhn_checksum(acct))
        d['account_no'] = acct

        DictElement.addChildren(self, d)
        return d


class USCreditAccount(TradeElement):
    def __init__(self, dataPath=None,
                 dataFile='ranges.csv.gz',
                 countryFilter=['US'],
                 **kwargs):

        TradeElement.__init__(self, dataPath=dataPath,
                              dataFile=dataFile,
                              countryFilter=countryFilter,
                              **kwargs)
        return


def main(argv):
    trade = USCreditAccount()
    print(json.dumps(trade.create()))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
