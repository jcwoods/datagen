#!/usr/bin/python3

import sys
import gzip
import csv
import json
import os
import random

from datagen.entitygenerator import EntityElement, DictElement

class TradeElement(DictElement):
    def __init__(self, datapath = None,
                       dataFile=None,
                       countryFilter = None,
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        if datapath is None:
            p = os.path.dirname(__file__)
            datapath = os.path.join(p, 'data')

        if datapath is not None:
            dataFile = os.path.join(datapath, dataFile)

        trades = [ ]
        fields = None

        f = gzip.open(dataFile, 'rt')

        # dictreader defaults to using first row as header (good!!)
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for d in reader:
            if countryFilter is not None:
                if d['country'] not in countryFilter: continue

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

    def create(self, **kwargs):
        r = int(random.random() * len(self.trades))
        d = self.trades[r].copy()

        #print(str(d))

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
        for key in [ 'iin_start', 'iin_end', 'bank_logo', 'number_length',
                     'bank_url', 'bank_city' ]:
            del(d[key])
        
        # build the random account number
        n = acct_len - 6 - 1   # less BIN number and Luhn check digit
        acct = iin + str(int(random.random() * (10 ** n))).zfill(n)
        acct += str(self.luhn_checksum( acct ))
        d['account_no'] = acct

        DictElement.addChildren(self, d, **kwargs)
        return d

class USCreditAccount(TradeElement):
    def __init__( self, dataFile = 'ranges.csv.gz',
                        countryFilter = [ 'US' ],
                        **kwargs ):

        TradeElement.__init__(self, dataFile = dataFile,
                                    countryFilter = countryFilter,
                                    **kwargs)
        return



def main(argv):
    trade = USCreditAccount()

    for i in range(10000):
        print(json.dumps(trade.create()))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
