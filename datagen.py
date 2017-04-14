#!/usr/bin/python3

import sys
import json
import sqlite3

import numpy as np
from bisect import bisect
from datetime import datetime, timedelta

from randpool import RandPool

# TODO - Modifier functions, two types: pre- and post-serialization.
# pre-modifiers change the object before it is written.  This might
# be useful for introducing intentional errors, nicknames, modifying
# structure, etc.  The post-serialization modifiers can be used to
# create changes to the object which was just serialized so that it
# can be serialized again.  This should be an efficient way to create
# relationships (where large parts of the object might be reused).

# TODO - need serializers (JSON, CSV, others?)

# TODO - nicknames, name variations

# TODO - need pre-output modifier functions.  This might randomly disrupt
# otherwise too-clean data.

# TODO - need post-output modifier functions.  These operate on the entity
# which was just output, and might be employed to reuse large portions of
# the original record.  This might be useful for generating a spouse or a
# parent/child (biological) relationship.  Once a post-output modifier has
# operated on an entity, we will have to serialize the modified object
# again in its modified state.

# TODO - generate trade data

# TODO - when an EntityElement has children, those children need to be
# executed as part of the create() sequence.

class EntityGenerator(object):
    '''
    EntityGenerator maintains the structured relations of EntityElements.
    It is the owner of the root data element, which is always a dict.  Child
    elements are added to this root element much like nodes are added to an
    XML document root when working with DOM.
    '''

    def __init__(self):
        self.data = None       # the current data object being built
        self.children = None   # a list of child generators (populate data)
        return

    def addElement(self, name, elem):

        # the fact that children is an array is VERY IMPORTANT.  The order
        # in which the elements are created must be guaranteed so that
        # generators which reference other elements can be guaranteed that
        # referenced values exists.  As an example, assume that we have name
        # and gender elements, with the generation of the name depending on
        # the value selected for gender.  It wouldn't do much good to generate
        # the name before the gender.

        if self.children is None:
            self.children = []

        elem.setRoot(self)
        x = (name, elem)
        self.children.append(x)
        return

    def create(self, **kwargs):
        self.data = {}

        for elem in self.children:
            e_nam = elem[0]
            e_val = elem[1].create(**kwargs)
            self.data[e_nam] = e_val

        return self.data

    def getValueByPath(self, path):
        '''
        Traverse the data element being generated and return the value
        matching the given path.  If the path cannot be parsed, we will assume
        that the given value was intended to be a literal value.  If we
        encounter an array during our traversal, we will always select or
        navigate through the last element in the list (assuming it is the
        most recently generated).
        '''

        parts = path.split('/')

        if len(parts[0]) == 0:
            element = self.data
            for i in parts[1:]:            # skip the first (empty) part
                if type(element) is list:
                    element = element[-1]

                element = element[i]

            return element

        return path  # can't parse?  return the whole dang thing as literal


class EntityElement(object):
    '''
    Base class for all Entity Elements.  An EntityElement may be added to
    either an Entity (as an element on the root of the element) or
    as a child of another EntityElement.

    Constructor accepts the arguments:
        name    - the name of the element in generated output (dict key)
        count   - the number of times this element will be repeated.  This
                  may be a callable (function) or an integer value.
        generator - the generator class used to create data
        children - (may not be necessary... stay tuned)
        mods     - (may not be necessary... stay tuned)
        params   - parameters to be passed to each create() call.  The list
                   of valid parameters is relative to the generator being used
        root     - a reference to EntityGenerator object used to create this
                   data entity.
    '''

    pool = RandPool()  # a pool of random numbers everybody can share.

    def __init__(self, name = None,
                       count = 1,
                       generator = None,
                       children = None,
                       mods = None,
                       params = None,
                       root = None):

        #if name is None or type(name) is not str:
        #    raise ValueError('Invalid element name')
        self.name = name

        # count must be a callable function, but we can also accept an integer.
        # If given an integer, we'll convert it using a lambda function which
        # returns the appropriate value.

        if callable(count):
            count_fn = count
        else:
            if type(count) is int:
                count_fn = lambda: count
            else:
                raise ValueError('Invalid type for element count')

        self.count = count_fn
        self.root = root

        self.params = params
        self.generator = None
        self.children = None
        self.mods = None

        return

    def addElement(self, name, elem):
        if not isinstance(elem, EntityElement):
            raise ValueError('element not EntityElement type in addElement')

        # the fact that children is an array is VERY IMPORTANT.  The order
        # in which the elements are created must be guaranteed so that
        # parameters which reference other elements can be guaranteed that
        # referenced values exists.

        if self.children is None:
            self.children = []

        elem.setRoot(self.root)
        x = (name, elem)
        self.children.append(x)
        return

    def setRoot(self, root):
        self.root = root

    @staticmethod
    def count_const_fn(x):
        return lambda: x

    @staticmethod
    def count_rand_fn(max, min=0):
        if max <= min:
            raise ValueError('min must be less than max in count_rand_fn()')

        return lambda: int(((max - min) * np.random.rand()) + min)

    @staticmethod
    def count_norm_fn(mean=0.0, stdev=1.0, integer=False):
        if integer is False:
            return lambda: np.random.normal(loc=mean, scale=stdev)

        return lambda: int(np.random.normal(loc=mean, scale=stdev))
    

class ArrayElement(EntityElement):
    '''
    '''
    def __init__(self, generator = None,
                       count_fn = None,
                       **kwargs):

        EntityElement.__init__(self, **kwargs)

        self.count_fn = count_fn
        self.generator = generator

        return

    def create(self, **kwargs):
        data = []

        if self.count_fn is None: return data

        c = self.count_fn()
        while c > 0:
            e = self.generator.create(root = data)
            data.append(e)
            c -= 1

        return data


class DictElement(EntityElement):
    '''
    '''
    def __init__(self, **kwargs):
        EntityElement.__init__(self, **kwargs)
        return

    def create(self, **kwargs):
        return


class SimpleElement(EntityElement):
    '''
    '''
    def __init__(self, **kwargs):
        EntityElement.__init__(self, **kwargs)
        return

    def create(self, **kwargs):
        return


class GenderElement(SimpleElement):
    def __init__(self, pctMale=0.50, **kwargs):

        SimpleElement.__init__(self, **kwargs)

        if pctMale < 0.0 or pctMale > 1.0:
            err = 'ERROR: invalid pctMale value: {0:s}'.format(str(pctMale))
            raise ValueError(err)

        self.pctMale = pctMale
        return

    def create(self, **kwargs):
        r = EntityElement.pool.next()
        if r <= self.pctMale: return 'M'
        return 'F'


# TODO - need better phone generator:
#        - Create a CDF for each zip code with area code frequencies
#        - do not use invalid exchanges or sequence numbers
class PhoneElement(SimpleElement):
    def __init__(self, **kwargs):
        SimpleElement.__init__(self, **kwargs)
        return

    def create(self, **kwargs):
        r = int(EntityElement.pool.next() * 10000000000)
        p = '{0:010d}'.format(r)
        return p


class NameCDF(object):

    '''
    Implements a simple class which loads a CDF and executes a bisect operation
    on it to locate random values (based on CDF distribution).  This is useful
    for things such as names.  ;)
    '''

    def __init__(self, dataFile=None, delimiter='|'):
        self.cumpct = []
        self.names = []


        f = open(dataFile, 'r')
        for line in f:
            fields = line.strip().split(delimiter)
            self.names.append(fields[0])
            self.cumpct.append(float(fields[1]))

        f.close()
        return

    def getName(self):
        pos = bisect(self.cumpct, EntityElement.pool.next())
        return self.names[pos]


class USCensusName(DictElement):
    def __init__(self, male = "data/male.dat",
                       female = "data/female.dat",
                       surname = "data/surname.dat",
                       #params=None,
                       order=None,           # output order of full name (one
                                             #   of None, LFM, or FML).
                       pctMidName=1.0,       # percentage of names which have
                                             #   a middle name (0..1).
                       pctMidInitial=0.0,    # of the names which have a mid
                                             #   name, how many of those give
                                             #   only an initial (0..1)
                       pctFirstInitial=0.0,  # percentage of first names which
                                             #   only a first initial
                       **kwargs):

        DictElement.__init__(self, **kwargs)

        self.male = NameCDF(male)
        self.female = NameCDF(female)
        self.surname = NameCDF(surname)

        self.order = order
        self.pctMidName = pctMidName
        self.pctMidInitial = pctMidInitial
        self.pctFirstInitial = pctFirstInitial
        return

    def create(self, gender = None, **kwargs):

        # If we have a path to Gender (as a parameter), we'll use it over an
        # explicitly given gender.
        if self.params is not None:
            gender_path = self.params.get('gender')
            if gender_path is not None:
                gender = self.root.getValueByPath(gender_path)

        if gender is None:
            fn_gen = self.male.getName
            if EntityElement.pool.next() < 0.5:
                 fn_gen = self.female.getName
        elif gender.lower() in ['m', 'male'] :
            fn_gen = self.male.getName
        elif gender.lower() in ['f', 'female'] :
            fn_gen = self.female.getName
        else:
            raise ValueError('Invalid gender: {0:s}'.format(gender))

        first = fn_gen()
        if self.pctFirstInitial > EntityElement.pool.next():
            first = first[0]

        last = self.surname.getName()

        if EntityElement.pool.next() < self.pctMidName:
            middle = fn_gen()
            if EntityElement.pool.next() < self.pctMidInitial:
                middle = middle[0]
        else:
            middle = None

        if self.order is "LFM":
            if middle is not None:
                full = '{0:s} {1:s} {2:s}'.format(last, first, middle)
            else:
                full = '{0:s} {1:s}'.format(last, first)
        elif self.order is "FML":
            if middle is not None:
                full = '{0:s} {1:s} {2:s}'.format(first, middle, last)
            else:
                full = '{0:s} {1:s}'.format(first, last)
        else:
            full = None

        r = { 'first': first, 'last': last }
        if middle is not None: r['middle'] = middle
        if full is not None:   r['full'] = full

        return r


class AddressElement(DictElement):
    def __init__(self, dataFile=None,
                       table = None,
                       id_col = None,
                       fields = [],
                       **kwargs ):

        DictElement.__init__(self, **kwargs)

        con = sqlite3.connect(dataFile)

        cur = con.cursor()
        cur.execute('select min(id), max(id) from addresses')

        min_id, max_id = cur.fetchone()

        con.row_factory = sqlite3.Row
        self.con = con
        self.min_id = int(min_id)
        self.max_id = int(max_id)
        self.range_id = self.max_id - self.min_id
        self.fields = fields

        cols = ', '.join(fields)
        self.sql = 'select {0:s} from {1:s} where {2:s} = ?'.format(cols,
                                                                    table,
                                                                    id_col)
        return

    def create(self, **kwargs):
        r = int(EntityElement.pool.next() * self.range_id) + self.min_id
        cur = self.con.cursor()
        cur.execute(self.sql, (r,))
        row = cur.fetchone()

        d = {}
        for col in row.keys():
            d[col] = row[col]

        return d

class USAddress(AddressElement):
    def __init__( self, dataFile = 'data/us_addresses.db',
                        table = 'addresses',
                        id_col = 'id',
                        fields = [ 'street1', 'street2', 'street3',
                                   'city', 'state', 'postalcode' ],
                        **kwargs ):

        AddressElement.__init__(self, dataFile = dataFile,
                                      table = table,
                                      id_col = id_col,
                                      fields = fields,
                                      **kwargs)
        return


class NationalIDElement(SimpleElement):
    def __init__(self,
                 useDashes = False,
                 **kwargs):

        SimpleElement.__init__(self, **kwargs)
        self.useDashes = useDashes
        return

    def create(self, **kwargs):

        # area cannot be 000, 666, or 900-999.
        while True:
            area = int(EntityElement.pool.next() * 899) + 1  # 001 .. 899
            if area != 666: break

        # group cannot be 00
        group = int(self.pool.next() * 99) + 1                 # 01 .. 99

        # serial cannot be 0000
        ser = int(self.pool.next() * 9999) + 1                 # 0001 .. 9999

        if self.useDashes:
            return '{0:03d}-{1:02d}-{2:04d}'.format(area, group, ser)

        return '{0:03d}{1:02d}{2:04d}'.format(area, group, ser)


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
    egen = EntityGenerator()

    gender = GenderElement()


    dob = DOBElement(dt_format = '%Y%m%d')

    ssn = NationalIDElement(useDashes = False)

    name = USCensusName(order = 'LFM',
                        pctMidName=0.7,
                        pctMidInitial=0.5,
                        pctFirstInitial=0.15,
                        params = { 'gender': '/gender' } )

    phone = PhoneElement()

    addr = USAddress()
    addrBlock = ArrayElement(name = 'addresses',
                             count_fn = EntityElement.count_rand_fn(max = 5,
                                                                    min = 1),
                             generator = addr)

    egen.addElement('gender', gender)
    egen.addElement('dob', dob)
    egen.addElement('ssn', ssn)
    egen.addElement('name', name)
    egen.addElement('phone', phone)
    egen.addElement('addrs', addrBlock)

    for i in range(10):
        e = egen.create()
        print('{0: 2d}: {1:s}'.format(i, json.dumps(e)))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
