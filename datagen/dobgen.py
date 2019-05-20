#!/usr/bin/python3

import random
import sys
from datetime import datetime, timedelta
from datagen.entitygenerator import EntityElement, SimpleElement

class DOBElement(SimpleElement):

    # Age distribution taken from "Demography of the United States":
    #     https://en.wikipedia.org/wiki/Demography_of_the_United_States
    #
    # The format used in the age_dist table is very easy to extract from
    # external sources.  It will be munged by the class to make it usable.
    #
    # Ranges are inclusive of their endpoints.
    #
    # The sum of all percentages SHOULD sum to nearly 100%, but some slop is
    # expected and compensated for in the algorithm.
    # 
    #            (minage, maxage, pct)
    age_dist = [ (18, 19, 0.4 * 7.1),
                 (20, 24, 7.0),
                 (25, 29, 6.8),
                 (30, 34, 6.5),
                 (35, 39, 6.5),
                 (40, 44, 6.8),
                 (45, 49, 7.4),
                 (50, 54, 7.2),
                 (55, 59, 6.4),
                 (60, 64, 5.4),
                 (65, 69, 4.0),
                 (70, 74, 3.0),
                 (75, 79, 2.4),
                 (80, 84, 1.9),
                 (85, 99, 1.8)  ]

    def initCDF(self):
        '''
        The age distribution exists in "buckets".  We need to convert this to
        a CDF (cumulative distribution function), where each entry in the
        table represents the percentage of the population at a given age
        bracket or younger.
        '''

        cum_pct = 0.0
        cdf = []

        for e in DOBElement.age_dist:
            prev_pct = cum_pct
            cum_pct += e[2]
            base_days = e[0] * 365.25
            range_years = (e[1] - e[0]) + 1
            range_days = range_years * 365.25

            entry = (prev_pct, cum_pct, base_days, range_days)
            cdf.append(entry)

        self.cdf = cdf
        self.cum_pct = cum_pct  # this allows for some slop in the table.

        return

    def __init__(self, minAge = None,
                       dt_format = '%Y-%m-%d',
                       pctPresent = 0.9382,
                       **kwargs):

        SimpleElement.__init__(self, **kwargs)
        self.initCDF()
        self.dt_format = dt_format
        self.pctPresent = pctPresent
        self.min_age = minAge
        self.now = datetime.now()

        return

    def create(self, **kwargs):

        # TODO - honor self.min_age

        if random.random() >= self.pctPresent:
            return None

        # Generate a random number 0..cum_pct. 
        rnd = random.random() * self.cum_pct

        # Find the bucket in the CDF which matches 'rnd'
        for e in self.cdf:
            if rnd >= e[0] and rnd < e[1]: break

        # 'e' now contains our matching age bracket and we can compute an age
        # (in days) for the entity.  e[2] contains the "base" (minimum) days
        # the entity must be in order to fall in this bracket, and e[3]
        # contains the number of days which span the bracket.  By adding
        # e[2] to a random number 0..e[3], we get an age in days.

        rnd_days = e[2] + (random.random() * e[3])
        dt = self.now - timedelta(days=rnd_days)
        return dt.strftime(self.dt_format)

def main(argv):
    dob = DOBElement()

    for n in range(1000):
        print(dob.create())

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
