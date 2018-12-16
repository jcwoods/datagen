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

import random
import sys
from datagen.entitygenerator import SimpleElement

class PhoneElement(SimpleElement):
    def __init__(self, **kwargs):
        SimpleElement.__init__(self, **kwargs)
        return

    def create(self, format = True):

        # Allowed ranges: [2-9] for the first digit, and [0-9] for the
        # second and third digits. When the second and third digits of an area
        # code are the same, that code is called an easily recognizable code
        # (ERC). ERCs designate special services; e.g., 888 for toll-free
        # service. The NANP is not assigning area codes with 9 as the second
        # digit.

        npa = str(int(random.random() * 800) + 200)
        while npa[1] == '9' or npa[1] == npa[2]:
            npa = str(int(random.random() * 800) + 200)

        # Allowed ranges: [2-9] for the first digit, and [0-9] for both the
        # second and third digits (however, in geographic area codes the
        # third digit of the exchange cannot be 1 if the second digit is also
        # 1).
        nxx = str(int(random.random() * 800) + 200)
        while nxx[1] == '1' and nxx[2] == '1':
            nxx = str(int(random.random() * 800) + 200)

        # [0-9] for each of the four digits.
        # Despite the widespread usage of NXX 555 for fictional telephone
        # numbers, the only such numbers now specifically reserved for
        # fictional use are 555-0100 through 555-0199, with the remaining 555
        # numbers released for actual assignment as information numbers.
        sub = int(random.random() * 10000)
        while nxx == '555' and sub >= 100 and sub < 200:
            sub = int(random.random() * 10000)

        sub = "{:04d}".format(sub)

        if format is False:
            p = npa + nxx + sub
        else:
            p = "{0:s}-{1:s}-{2:s}".format(npa, nxx, sub)

        return p

def main(argv):
    phone = PhoneElement()
    print(phone.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
