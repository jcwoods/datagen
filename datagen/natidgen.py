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

class NationalIDElement(SimpleElement):
    def __init__(self,
                 useDashes = False,
                 pctPresent = 1.0,
                 **kwargs):

        SimpleElement.__init__(self, **kwargs)
        self.useDashes = useDashes
        self.pctPresent = pctPresent
        return

    def create(self, **kwargs):

        if random.random() >= self.pctPresent:
            return None

        # area cannot be 000, 666, or 900-999.
        while True:
            area = int(random.random() * 899) + 1  # 001 .. 899
            if area not in [0, 666]: break

        # group cannot be 00
        while True:
            group = int(random.random() * 99) + 1  # 01 .. 99
            if group != 0: break

        # serial cannot be 0000
        while True:
            ser = int(random.random() * 9999) + 1  # 0001 .. 9999
            if ser != 0: break

        if self.useDashes:
            return '{0:03d}-{1:02d}-{2:04d}'.format(area, group, ser)

        return '{0:03d}{1:02d}{2:04d}'.format(area, group, ser)


def main(argv):
    ssn = NationalIDElement()
    print(ssn.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
