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

import sys
import json

from datagen.sqlelement import SQLElement

class USAddress(SQLElement):
    '''
    USAddress is simply a wrapper class which provides some default values
    to the SQLElement class.  Nothing to see here folks...
    '''

    def __init__(self,
                 dataFile = 'us_address.db',
                 tableName = 'us_address',
                 **kwargs):

        SQLElement.__init__(self,
                            dataFile = dataFile,
                            tableName = tableName,
                            **kwargs)
        return


def main(argv):
    '''
    A simple test routine run by executing the module directly.
    '''
    addr = USAddress()
    print(json.dumps(addr.create()))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
