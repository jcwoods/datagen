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
import sys
from datagen.entitygenerator import EntityElement, SimpleElement

class PhoneElement(SimpleElement):
    def __init__(self, formatted=False, **kwargs):
        SimpleElement.__init__(self, **kwargs)
        self.formatted = formatted
        return

    # Rules taken from "Modern plan" found at:
    #     https://en.wikipedia.org/wiki/North_American_Numbering_Plan
    #
    # Stated plainly:
    # 1.  There are three sections to a phone number, NPA (area code), NXX
    #     (exchange), and XXXX (line number).
    # 2.  For the NPA:
    #     a. three digits
    #     b. 2-9 for first digit, 0-8 for second, and 0-9 for third digits
    #        (middle digit may not be a '9', which would be a trunk prefix)
    #     d. when 2nd and 3rd digits are the same, it's classified an ERC
    #        which, while not invalid, we will choose to avoid.
    # 3.  For the NXX:
    #     a. three digits
    #     b. [2-9] for first digit and [0-9] for second and third digits
    #     c. second and third digits may not both be '1'
    #     d. 555 should generally be avoided (used for informational or
    #        fictional numbers)
    #     e.  958/959 (testing) and 950/976 (service) should be avoided.
    #     f.  should not match the NPA.

    def create(self, **kwargs):

        while True:
            npai = int(random.random() * 800) + 200
            npa = '{0:03d}'.format(npai)
            if npa[1] != npa[2] and npa[1] != 9: break

        while True:
            nxxi = int(random.random() * 800) + 200
            nxx = '{0:03d}'.format(nxxi)
            if nxx[1:] != '11' and \
               nxx not in [ '555', '958', '959', '950', '976' ]:
                continue
            break

        linei = int(random.random() * 10000)
        line = '{0:04d}'.format(linei)

        if not self.formatted:
            p = npa + nxx + line
        else:
            p = '-'.join((npa,nxx,line))

        return p

def main(argv):
    phone = PhoneElement(formatted=True)

    for n in range(10):
        print(phone.create())

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
