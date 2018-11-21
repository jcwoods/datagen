#!/usr/bin/python3

import sys
from datetime import datetime, timedelta
from entitygenerator import EntityElement, SimpleElement

# TODO - needs a better age distribution
class DOBElement(SimpleElement):
    def __init__(self, minAge = 18,
                       maxAge = 100,
                       dt_format = '%Y-%m-%d',
                       **kwargs):

        SimpleElement.__init__(self, **kwargs)

        yspan = maxAge - minAge
        days = int(float(yspan) * 365.25)      # roughly

        self.dt_format = dt_format
        self.minAge = minAge
        self.maxAge = maxAge
        self.days = days
        return

    def create(self, **kwargs):
        ndays = int(EntityElement.pool.next() * self.days)
        dt = datetime.now() - timedelta(days=ndays)
        return dt.strftime(self.dt_format)

def main(argv):
    dob = DOBElement()
    print(dob.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
