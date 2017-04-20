#!/usr/bin/python3

import sys
import gzip
import csv
import json

from entitygenerator import EntityElement, DictElement

class TradeElement(DictElement):
    def __init__(self, dataFile=None,
                       countryFilter = None,
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        trades = [ ]
        fields = None

        f = gzip.open(dataFile, 'rt', encoding='utf-8')

        # dictreader defaults to using first row as header (good!!)
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for d in reader:
            if countryFilter is not None:
                if d['country'] not in countryFilter: continue
                if d['iin_start'] is "": continue

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
        return luhn_checksum(card_number) == 0

    def create(self, **kwargs):
        r = int(EntityElement.pool.next() * len(self.trades))
        d = self.trades[r]

        # TODO - For some reason, iin_start does not exist at times?
        try:
            iin = d['iin_start']  # TODO - also use to iin_end
        except:
            print("*** BOOM ***")
            print(str(d))
            sys.exit(1)

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
        acct = iin + str(int(EntityElement.pool.next() * (10 ** n))).zfill(n)
        acct += str(self.luhn_checksum( acct ))
        d['account_no'] = acct

        DictElement.addChildren(self, d, **kwargs)
        return d

class USCreditAccount(TradeElement):
    def __init__( self, dataFile = 'data/ranges.csv.gz',
                        countryFilter = [ 'US' ],
                        **kwargs ):

        TradeElement.__init__(self, dataFile = dataFile,
                                    countryFilter = countryFilter,
                                    **kwargs)
        return



def main(argv):
    trade = USCreditAccount()

    for i in range(10):
        print(json.dumps(trade.create()))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
