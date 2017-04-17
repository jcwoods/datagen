#!/usr/bin/python3

import sys
import numpy as np
from randpool import RandPool

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

class EntityGenerator(object):
    '''
    EntityGenerator maintains the structured relationships between initialized
    EntityElements.  It is responsible for initializing the root data element
    and walking the tree of generator Entities.  EntityElements are added to
    the EntityGenerator much like nodes might be added to an XML document when
     working with DOM.
    '''

    def __init__(self):
        self.data = None       # the current data object being built

        # the fact that children is an array is VERY IMPORTANT.  The order
        # in which the elements are created must be guaranteed so that
        # generators which reference other elements can be guaranteed that
        # referenced values exists.  As an example, assume that we have name
        # and gender elements, with the generation of the name depending on
        # the value selected for gender.  It wouldn't do much good to generate
        # the name before the gender.

        self.children = []     # a list of child generators (populate data)
        return

    def addElement(self, elem, label = None):
        if label is None:
            label = elem.name

        elem.setRoot(self)
        x = (label, elem)
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
        params   - parameters to be passed to each create() call.  The list
                   of valid parameters is relative to the generator being used
        root     - a reference to EntityGenerator object used to create this
                   data entity.
    '''

    pool = RandPool()  # a pool of random numbers everybody can share.

    def __init__(self, name = None,
                       generator = None,
                       params = None,
                       root = None):

        self.name = name

        self.root = root

        self.params = params
        self.generator = None
        self.mods = None

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

        # TODO - an ArrayElement may not have children

        # count must be a callable function, but we can also accept an integer.
        # If given an integer, we'll convert it using a lambda function which
        # returns the appropriate value.

        if not callable(count_fn):
            if type(count) is int:
                count_fn = lambda: count_fn
            else:
                raise ValueError('Invalid type for element count')

        self.count = count_fn

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
    A DictElement may have children of any type.
    '''

    def __init__(self, **kwargs):
        EntityElement.__init__(self, **kwargs)
        self.children = None
        return

    def addElement(self, elem, label = None):
        if not isinstance(elem, EntityElement):
            raise ValueError('element not EntityElement type in addElement')

        if label is None:
            label = elem.name

        # the fact that children is an array is VERY IMPORTANT.  The order
        # in which the elements are created must be guaranteed so that
        # parameters which reference other elements can be guaranteed that
        # referenced values exists.

        self.children = []

        elem.setRoot(self.root)
        x = (label, elem)
        self.children.append(x)
        return

    def addChildren(self, data, **kwargs):
        if self.children is None: return None

        for child in self.children:
            enam = child[0]
            egen = child[1]
            data[enam] = egen.create()

        return


class SimpleElement(EntityElement):
    '''
    A SimpleElement cannot have children.
    '''

    def __init__(self, **kwargs):
        EntityElement.__init__(self, **kwargs)
        # TODO - a SimpleElement may not have children
        return

    def create(self, **kwargs):
        return
