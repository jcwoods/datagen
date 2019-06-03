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

import random
import string
import sys

from itertools import groupby
from datagen.entitygenerator import EntityElement, DictElement

 
class USDriversLicenseElement(DictElement):
    def __init__(self,
                 useFormat = True,
                 pctPresent = 1.0,
                 **kwargs):

        DictElement.__init__(self, **kwargs)
        self.useFormat = useFormat   # TODO: ignored for now...
        self.pctPresent = pctPresent

        self.states = {
            "AK": lambda: self.dn(7),
            "AL": lambda: self.dn(7), 
            "AR": lambda: "9" + self.dn(8),
            "AZ": lambda: self.an(1) + self.dn(8),
            "CA": lambda: self.an(1) + self.dn(7),
            "CO": lambda: "-".join((self.dn(2), self.dn(3), self.dn(4))),
            "CT": self.ct,
            "DE": lambda: self.dn(7),
            #"FL": lambda: None,  # it's complicated...
            "GA": lambda: self.dn(9),
            "HI": lambda: 'H' + self.dn(8),
            "IA": lambda: "".join((self.dn(3), self.an(2), self.dn(4))),
            "ID": lambda: self.an(2) + self.dn(6) + self.an(1),
            #"IL": lambda: None,  # first letter of LN + 11
            "IN": lambda: '-'.join((self.dn(4), self.dn(2), self.dn(4))),
            "KS": lambda: '-'.join((self.dn(2), self.dn(2), self.dn(4))),
            "KY": lambda: '-'.join((self.an(1) + self.dn(2), self.dn(3), self.dn(3))),
            "LA": lambda: "00" + self.dn(7),
            "MA": lambda: 'S' + self.dn(8),
            #"MD": lambda: None,  # it's complicated
            "ME": lambda: self.dn(7),
            #"MI": lambda: None,  # it's complicated
            #"MN": lambda: None,  # it's complicated
            "MO": lambda: self.an(1) + self.dn(random.choice([6,7,8,9])),
            "MS": lambda: self.dn(9),
            #"MT": lambda: None,  # it's complicated
            "NC": lambda: self.dn(12),
            #"ND": lambda: None,  # it's complicated
            "NE": lambda: self.an(1) + self.dn(8),
            #"NH": lambda: None,  # it's complicated
            #"NJ": lambda: None,  # it's complicated
            "NM": lambda: self.dn(9),
            "NV": lambda: self.dn(10),
            "NY": lambda: ' '.join((self.dn(3), self.dn(3), self.dn(3))),
            "OK": lambda: self.an(1) + self.dn(8),
            "OH": lambda: self.an(2) + self.dn(6),
            "OR": lambda: self.dn(7),
            "PA": lambda: ' '.join((self.dn(2), self.dn(3), self.dn(3))),
            "RI": lambda: self.dn(7),
            "SC": lambda: self.dn(9),
            "SD": lambda: self.dn(8),
            "TN": lambda: self.dn(random.choice([8,9])),
            "TX": lambda: self.dn(8),
            "UT": lambda: self.dn(9),
            "VA": lambda: '-'.join((self.an(1) + self.dn(2), self.dn(2),
                self.dn(4))),
            "VT": lambda: self.dn(8),
            #"WA": lambda: None,  # it's compilcated
            #"WI": lambda: None,  # it's complicated
            "WV": lambda: self.an(1) + self.dn(6),
            "WY": lambda: '-'.join((self.dn(6), self.dn(3))) }

        self.allStates = list(self.states.keys())
        return

    # returns 'n' random digits as a string padded on the left with leading 0s
    # think of this as "n digits"
    @staticmethod
    def dn(n):
        return ''.join(random.choice(string.digits) for i in range(n))

    # returns 'n' random ascii as a string 
    # think of this as "n alpha"
    @staticmethod
    def an(n):
        return ''.join(random.choice(string.ascii_uppercase) for i in range(n))

    # this implementation borrowed from rosettacode.org
    @staticmethod
    def soundex(word):
        codes = ("bfpv","cgjkqsxz", "dt", "l", "mn", "r")
        soundDict = dict((ch, str(ix+1)) for ix,cod in enumerate(codes) for ch in cod)
        cmap2 = lambda kar: soundDict.get(kar, '9')
        sdx =  ''.join(cmap2(kar) for kar in word.lower())
        sdx2 = word[0].upper() + ''.join(k for k,g in list(groupby(sdx))[1:] if k!='9')
        sdx3 = sdx2[0:4].ljust(4,'0')
        return sdx3


    # CT drivers license number generator
    # dob, if provided, MUST be YYYYMMDD format!
    def ct(self, dob = None, **kwargs):
        if dob is not None:
            yob = int(dob[0:4])
            mob = int(dob[4:2])
        else:
            mob = random.choice([1, 2, 3,  4,  5,  6, 7, 8, 9, 10, 11, 12])
            yob = random.choice([0, 1])

        if yob == 1: mob += 12
        return "{0:02d}{1:s}".format(mob, self.dn(7))

    def fl(self, dob = None, **kwargs):
        return "W320-410-71-196-2"

    def create(self, state = None, **kwargs):

        if state is None:
            state = random.choice(self.allStates)
        if random.random() >= self.pctPresent:
            return None

        dl = self.states[state]()
        e = { "dlNumber": dl, "state": state }
        return e


def main(argv):
    dl = USDriversLicenseElement()
    for i in range(10000):
        print(dl.create())

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
