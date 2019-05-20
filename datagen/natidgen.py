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

class NationalIDElement(SimpleElement):
    def __init__(self,
                 format = False,
                 **kwargs):

        SimpleElement.__init__(self, **kwargs)
        self.format = format
        return

    def create(self):

        # area cannot be 000, 666, or 900-999.
        while True:
            area = int(random.random() * 899) + 1  # 001 .. 899
            if area != 666: break

        # group cannot be 00
        group = int(random.random() * 99) + 1                 # 01 .. 99

        # serial cannot be 0000
        ser = int(random.random() * 9999) + 1                 # 0001 .. 9999

        if self.format:
            return '{0:03d}-{1:02d}-{2:04d}'.format(area, group, ser)

        return '{0:03d}{1:02d}{2:04d}'.format(area, group, ser)



def main(argv):
    ssn = NationalIDElement()
    print(ssn.create())
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
