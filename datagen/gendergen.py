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

import sys
from bisect import bisect
from datagen.entitygenerator import EntityElement, SimpleElement
import random

class GenderElement(SimpleElement):
    def __init__(self, pctMale=0.50, **kwargs):

        SimpleElement.__init__(self, **kwargs)

        if pctMale < 0.0 or pctMale > 1.0:
            err = 'ERROR: invalid pctMale value: {0:s}'.format(str(pctMale))
            raise ValueError(err)

        self.pctMale = pctMale
        return

    def create(self, **kwargs):
        r = random.random()
        if r <= self.pctMale: return 'M'
        return 'F'


def main(argv):
    gender = GenderElement()
    print(gender.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
