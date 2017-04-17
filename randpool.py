#!/usr/bin/python3

import numpy as np

# TODO - add getters for int and support min/max ranges.

class RandPool(object):
    def __init__(self, size = 100000):
        self.pool = np.random.rand(size)
        self.n = 0
        self.size = size
        return
    
    def next(self):
        if self.n < self.size:
            r = self.pool[self.n]
            self.n += 1
            return r
    
        # allocate a new pool and return the first number
        self.pool = np.random.rand(self.size)
        r = self.pool[0]
        self.n = 1
        return r

