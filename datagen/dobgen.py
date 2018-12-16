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

import bisect
import random
import sys

from datetime import datetime, timedelta
from datagen.entitygenerator import EntityElement, SimpleElement

# Age distributions taken from Wikipedia:
# https://en.wikipedia.org/wiki/Demography_of_the_United_States
#    15-19 (7.1%) (and we're only interested in the 18-19 range here!)
#    20-24 (7.0%)
#    25-29 (6.8%)
#    30-34 (6.5%)
#    35-39 (6.5%)
#    40-44 (6.8%)
#    45-49 (7.4%)
#    50-54 (7.2%)
#    55-59 (6.4%)
#    60-64 (5.4%)
#    65-69 (4.0%)
#    70-74 (3.0%)
#    75-79 (2.4%)
#    80-84 (1.9%)
#    85+   (1.8%)

class DOBElement(SimpleElement):

    '''
    This is an awful log like what we already did in the CDF class, but it
    doesn't quite fit.
    '''

    # format is ("percent", ("min days", "max days")).
    ageDistribution = [ (0.4 * 0.071, (365.25 * 18, 365.25 * 20)),
                        (      0.070, (365.25 * 20, 365.25 * 25)),
                        (      0.068, (365.25 * 25, 365.25 * 30)),
                        (      0.065, (365.25 * 30, 365.25 * 35)),
                        (      0.065, (365.25 * 35, 365.25 * 40)),
                        (      0.068, (365.25 * 40, 365.25 * 45)),
                        (      0.074, (365.25 * 45, 365.25 * 50)),
                        (      0.072, (365.25 * 50, 365.25 * 55)),
                        (      0.064, (365.25 * 55, 365.25 * 60)),
                        (      0.054, (365.25 * 60, 365.25 * 65)),
                        (      0.040, (365.25 * 65, 365.25 * 70)),
                        (      0.030, (365.25 * 70, 365.25 * 75)),
                        (      0.024, (365.25 * 75, 365.25 * 80)),
                        (      0.019, (365.25 * 80, 365.25 * 85)),
                        (      0.018, (365.25 * 85, 365.25 * 105)) ]

    @staticmethod
    def daysOld(x):
        '''
        Given a bucket from ageDistribution, how many days old EXACTLY?
        '''

        return r

    def __init__(self, minAge = 18,
                       maxAge = 100,
                       dateFormat = '%Y-%m-%d',
                       **kwargs):

        SimpleElement.__init__(self, **kwargs)

        self.dist = []

        maxPct = 0
        for i in DOBElement.ageDistribution:
            maxPct += i[0]
            self.dist.append((maxPct, i[1]))

        self.maxPct = maxPct

        self.dt_format = dateFormat
        return

    def create(self):
        r = random.random() * self.maxPct

        i = bisect.bisect(self.dist, (r, ))
        entry = self.dist[i][1]

        days_min = entry[0]
        days_max = entry[1]
        days_range = days_max - days_min

        ndays = (random.random() * days_range) + days_min

        dt = datetime.now() - timedelta(days=ndays)
        return dt.strftime(self.dt_format)

def main(argv):
    dob = DOBElement()
    print(dob.create())

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
