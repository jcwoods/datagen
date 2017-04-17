#!/usr/bin/python3

import sys
import json
import sqlite3

import numpy as np
from randpool import RandPool

from entitygenerator import EntityGenerator, EntityElement, ArrayElement
from namegen import USCensusName
from addrgen import USAddress
from phonegen import PhoneElement
from gendergen import GenderElement
from natidgen import NationalIDElement
from dobgen import DOBElement

# TODO - Modifier functions, two types: pre- and post-serialization.
# pre-modifiers change the object before it is serialized.  This might
# be useful for introducing intentional errors, nicknames, modifying
# structure, etc.  The post-serialization modifiers can be used to
# create changes to the object which was just serialized so that it
# can be serialized again.  This should be an efficient way to create
# relationships (where large parts of the object might be reused), such
# as husband/wife, parent/child, roommates, or co-applicants (credit).

# TODO - include nicknames, name variations (maiden/married)

# TODO - need pre-output modifier functions.  This might randomly disrupt
# otherwise too-clean data.

# TODO - need post-output modifier functions.  These operate on the entity
# which was just output, and might be employed to reuse large portions of
# the original record.  This might be useful for generating a spouse or a
# parent/child (biological) relationship.  Once a post-output modifier has
# operated on an entity, we will have to serialize the modified object
# again in its modified state.

# TODO - generate trade (credit account) data

# TODO - email generator?

# TODO - when generating an array of addresses, it would be nice to be able
# to specify "generate local addresses".  It's unrealistic that a person would
# move large distances frequently.  Instead, pick addresses (based on a
# probability) where the leading 1, 2, or 3 digits of the zip code (for US
# addresses) are the same.

# TODO - create address history, with from/to dates.

# TODO - need better phone generator:
#        - Create a CDF for each zip code with area code frequencies
#        - do not use invalid exchanges or sequence numbers


# ### Entity Generator ###
# The EntityGenerator class serves as a container for Elements.  When the
# create() method is called on this object, it walks through its list of
# children calling create() on each of them in turn.

# ### Elements ###
# There are three main types of elements.  These elements are all derrived
# from the EntityElement class, and each may be added as a child to the
# EntityGenerator object (above).  These Element types include:
#
#    - A SimpleElement.  This is an Element which creates nothing more than
#      a simple value, such as a string or integer.
#    - An ArrayElement.  This Element is implemented as a list of homogenous
#      items.  The items INSIDE this container, which are created by the 
#      generator passed in the object initialization, may be of any supported
#      Element type (Simple, Array, or Dict).  The number of items generated
#      inside the array will be repeated as described by the count_fn param.
#    - A DictElement.  This Element returns a dict populated with key/value
#      pairs.  This is the most sophisticated Element, supporting the nesting
#      of child Elements (see below).
#
# Each type of Element supports one or more generators.  A sample of
# generators might include gender (simple), dob (simple), name (dict),
# address (dict), and ssn (simple).  An entity would almost certainly have
# more than one address, so we could employ an ArrayElement to enclose the
# address dict.

# ### Child Elements ###
# Outside of the EntityGenerator class, only Elements based on the DictElement
# class may have children.  This makes sense because:
#    - the entity to which the child is added must be a container of some
#      sort.  Of the three Element types, only Dict and Array qualify.
#    - An ArrayElement gets filled with a consistent type of element (names,
#      addresses, trades, etc).


def serialize_csv(e):
    fname = e['name'].get('first', '')
    mname = e['name'].get('middle', '')
    lname = e['name'].get('last', '')
    dob = e.get('dob', '')
    ssn = e.get('ssn', '')
    phone = e.get('phone', '')
    gender = e.get('gender', '')

    for addr in e['addrs']:
        s = '|'.join(( fname, mname, lname,
                       ssn, dob, phone, gender,
                       addr['street1'], addr['street2'], addr['street3'],
                       addr['city'], addr['state'], addr['postalcode']) )
        print(s)

    return

def serialize_json(e):
    print(json.dumps(e))
    return

def main(argv):
    if len(argv) > 2:
        raise Exception('Invalid number of arguments received')

    n = 10
    if len(argv) == 2:
        try:
            n = int(argv[1])
        except:
            raise Exception('Invalid command line argument: ' + argv[1])

    egen = EntityGenerator()

    gender = GenderElement(name = 'gender')
    egen.addElement(gender)

    dob = DOBElement(name = 'dob',
                     dt_format = '%Y%m%d')
    egen.addElement(dob)

    ssn = NationalIDElement(name = 'ssn',
                            useDashes = False)
    egen.addElement(ssn)

    name = USCensusName(name = 'name',
                        order = 'LFM',
                        pctMidName=0.7,
                        pctMidInitial=0.5,
                        pctFirstInitial=0.15,
                        params = { 'gender': '/gender' } )
    egen.addElement(name)

    # we're going to get a bit crazy here (because we can!).  Each entity is
    # going to get a block of addresses.  Each address will be generated by
    # the USAddress Entity class, and the number of addresses in each block
    # will be random (range  [1..5) ).  Each address will get a block of phone
    # numbers, and there will be exactly two phone numbers in each block.

    addr = USAddress()
    addrBlock = ArrayElement(name = 'addresses',
                             count_fn = EntityElement.count_rand_fn(max = 5,
                                                                    min = 1),
                             generator = addr)

    # Create a block of phone numbers
    phone = PhoneElement()
    phoneBlock = ArrayElement(name = 'phones',
                              count_fn = EntityElement.count_const_fn(2),
                              generator = phone)

    addr.addElement(phoneBlock)  # add the block of phones to each address...
    egen.addElement(addrBlock)   # ...and finally add the addresses to the entity.


    # create a few entities 
    serialize = serialize_json
    #serialize = serialize_csv
    for i in range(n):
        entity = egen.create()
        serialize(entity)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
