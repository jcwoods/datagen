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

from bisect import bisect
from datagen.cdf import CDF
import csv
import json
import gzip
import os
import random
import sys

from datagen.entitygenerator import EntityGenerator, EntityElement, \
                                    DictElement, ArrayElement

class USCensusName(DictElement):
    def __init__(self, datapath = None,
                       male = "male.dat.gz",
                       female = "female.dat.gz",
                       surname = "surname.dat.gz",
                       suffix = None,
                       order=None,           # output order of full name (one
                                             #   of None, LFM, or FML).
                       pctMidName=1.0,       # percentage of names which have
                                             #   a middle name (0..1).
                       pctMidInitial=0.0,    # of the names which have a mid
                                             #   name, how many of those give
                                             #   only an initial (0..1)
                       pctFirstInitial=0.0,  # percentage of first names which
                                             #   only a first initial
                       pctSuffix=0,          # percentage of names which
                                             #   include a suffix
                       **kwargs):

        DictElement.__init__(self, **kwargs)

        if datapath is None:
            datagen_root = os.path.dirname(__file__)
            datapath = os.path.join(datagen_root, 'data')

        if datapath is not None:
            male = os.path.join(datapath, male)
            female = os.path.join(datapath, female)
            surname = os.path.join(datapath, surname)
            if suffix is not None:
                suffix = os.path.join(datapath, suffix)

        self.male = CDF(male, delimiter="|")
        self.female = CDF(female, delimiter="|")
        self.surname = CDF(surname, isCumulative = True, delimiter="|")
        if suffix is not None:
            self.suffix = CDF(suffix)
        else:
            self.suffix = None

        self.order = order
        self.pctMidName = pctMidName
        self.pctMidInitial = pctMidInitial
        self.pctFirstInitial = pctFirstInitial
        self.pctSuffix = pctSuffix
        return

    def buildName(self, last = None, first = None, middle = None, suffix = None):
        r = { 'first': first, 'last': last, 'suffix': suffix }
        if middle is not None: r['middle'] = middle
        full = self.buildFullName(last, first, middle, suffix)
        if full is not None:   r['full'] = full
        return r

    def buildFullName(self, last = None, first = None, middle = None, suffix = None):

        if self.order is "LFM":
            if middle is not None:
                full = " ".join((last, first, middle))
            else:
                full = " ".join((last, first))
        elif self.order is "FML":
            if middle is not None:
                full = " ".join((first, middle, last))
            else:
                full = " ".join((first, last))
        else:
            full = None

        if suffix is not None:
            full = " ".join((full, suffix))

        return full


    def create(self, gender = None, **kwargs):

        # If we have a path to Gender (as a parameter), we'll use it over an
        # explicitly given gender.
        if self.params is not None:
            gender_path = self.params.get('gender')
            if gender_path is not None:
                gender = self.root.getValueByPath(gender_path)

        if gender is None:
            if random.random():
                fn_gen = self.male.getValue
                if self.suffix is not None:
                    suffix_gen = self.suffix.getValue
                else:
                    suffix_gen = lambda: ""
            else:
                fn_gen = self.female.getValue
                suffix_gen = lambda: ""
        elif gender.lower() in ['m', 'male'] :
            fn_gen = self.male.getValue
            if self.suffix is not None:
                suffix_gen = self.suffix.getValue
            else:
                suffix_gen = lambda: ""
        elif gender.lower() in ['f', 'female'] :
            fn_gen = self.female.getValue
            suffix_gen = lambda: ""
        else:
            raise ValueError('Invalid gender: {0:s}'.format(gender))

        first = fn_gen()
        if self.pctFirstInitial > random.random():
            first = first[0]

        last = self.surname.getValue()

        if random.random() < self.pctMidName:

            ## do not allow duplicate first == middle names
            middle = fn_gen()
            #while middle == first:
            #    print("Middle: " + middle + ", First: " + first)
            #    middle == fn_gen()

            if random.random() < self.pctMidInitial:
                middle = middle[0]
        else:
            middle = None

        suffix = None
        if random.random() < self.pctSuffix:
            suffix = suffix_gen()

        r = self.buildName(last, first, middle, suffix)
        DictElement.addChildren(self, r, **kwargs)
        return r


class USCensusNameSet(ArrayElement):
    '''
    Generate a logical/related set of names based on US Census data.

    A set of names (might) contain:
      * a formal name
      * a nickname (based on the formal name)
      * a married name
    '''

    def __init__(self, male = "male.dat.gz",
                       female = "female.dat.gz",
                       surname = None,
                       order = "LFM",
                       pctMidName = 1.0,
                       pctMidInitial = 0.0,
                       pctFirstInitial = 0.0,
                       pctMarried = 0.58,
                       **kwargs):
        
        ArrayElement.__init__(self, count = 1, **kwargs)
        self.namegen = USCensusName(male = male,
                                    female = female,
                                    order = order,
                                    pctMidName = pctMidName,
                                    pctMidInitial = pctMidInitial,
                                    pctFirstInitial = pctFirstInitial)

        self.pctMarried = pctMarried
        self.nicknames = Nicknames()

    def create(self, gender = None, nickname = False, married = True):
        if self.params is not None:
            gender_path = self.params.get('gender')
            if gender_path is not None:
                gender = self.root.getValueByPath(gender_path)

        nameset = []

        name = self.namegen.create(gender = gender)
        nameset.append(name)

        if nickname and random.random() < 0.60:
            nn = self.nickname(name)
            if nn is not None :
                nameset.append(nn)

        if married and gender == 'F' and random.random() < self.pctMarried:
            mn = self.married(name)
            if mn is not None :
                nameset.append(mn)

        return nameset


    def nickname(self, name, gender = None):
        '''
        Using the input name, introduce a nickname.  Input name must be parsed
        in dict as if it were generated by USCensusName generator.
        '''

        first = name.get('first', None)
        middle = name.get('middle', None)
        last = name.get('last', None)
        suffix = name.get('suffix', None)

        # A few scenarios we should consider:
        #
        # 1.  add a nickname for the first or, if first is uncommon, the middle
        # 2.  if middle name is more common than first, use middle as first and
        #     drop middle
        # 3.  If no initial used for first or middle, introduce an initial in
        #     one or both locations.

        nickname = None

        # modifications on first name
        if nickname is None and len(first) > 1:
            nickname = self.nicknames.getNickname(first, gender = gender)

            if nickname is not None:
                first = nickname
                return self.namegen.buildName(last, first, middle)        

        # attempt modifications on middle name (if nothing done on first name)
        middle = name.get('middle', None)
        if middle is None or len(middle) < 2 :
            # we can't do anything to first, and there is nothing for middle
            return None

        nickname = self.nicknames.getNickname(middle, gender = gender)
        if nickname is None:
            return None

        first = nickname
        middle = None
        return self.namegen.buildName(last, first, middle, suffix)        


    def married(self, name, married_surname = None):
        '''
        Generate a married name.  Input name must be parsed in dict as if it
        were generated by USCensusName generator.
        '''

        out_name = name.copy()

        cur_surname = name['last']
        new_surname = married_surname if married_surname is not None else self.namegen.surname.getValue()

        # One of three scenarios to apply:
        #
        # 1.  takes new surname, retains original first and middle names
        # 2.  hyphenate old-new surnames, retain first and middle names
        # 3.  takes new surname, retains original surname as middle
        #
        # Rates vary over time.  In mid-2010s, rate of #1 is "about" 18%.  See
        #  http://articles.chicagotribune.com/2013-06-26/features/sc-fam-0625-women-name-change-20130626_1_maiden-laurie-scheuble-married-name
        # Rate for #2 is estimated (non-researched) at 2%
        # Rate for #3 is the remainder (about 80%).

        r = random.random()
        if r < 0.18:  # TODO - threshold should be tunable/configurable
            out_name['middle'] = cur_surname
            out_name['last'] = new_surname
        elif  r < 0.20:
            out_name['last'] = "-".join((cur_surname, new_surname))
        else:
            out_name['last'] = new_surname

        out_name['full'] = self.namegen.buildFullName(out_name.get('last', None),
                                                      out_name.get('first', None),
                                                      out_name.get('middle', None),
                                                      out_name.get('suffix', None))

        return out_name


class Nicknames():
    def __init__(self, datapath = None,
                       nicknames_file = 'nicknames.csv',
                       male_dist = 'male.dat.gz',
                       female_dist = 'female.dat.gz'):

        if datapath is None:
            p = os.path.dirname(__file__)
            datapath = os.path.join(p, 'data')

        male_dist_file = os.path.join(datapath, male_dist)
        female_dist_file = os.path.join(datapath, female_dist)
        nicknames_file  = os.path.join(datapath, nicknames_file)

        self.male_dist = Nicknames._load_freq(male_dist_file)
        self.female_dist = Nicknames._load_freq(female_dist_file)
        self.nicknames = Nicknames._load_nicknames(nicknames_file)

        return

    @staticmethod
    def _load_nicknames(file):
        '''
        Build a set of reference data containing possible name substitutions.

        Load known alias tables.  Each line contains bi-directional
        associations.  For example, given the data:

        JEFF,JEFFREY,JEFFERY
        GEOFF,JEFF
        GEOFFREY,GEOFF

        a lookup of JEFF could return JEFFREY, JEFFERY, or GEOFF, but not
        GEOFFREY.  A lookup of GEOFF might return either JEFF or GEOFFREY.

        This may make more sense given the context:

        PATRICK,PAT
        PATRICIA,PAT,PATTY

        Here, we might want to substitute PAT for PATRICK, but we would not
        want use PATTY for PATRICK.

        These lookups need to be reduced to:

        { "PATRICK":  [ "PAT" ],
          "PATRICIA": [ "PAT", "PATTY" ],
          "PAT":      [ "PATRICK", "PATTY", "PATRICIA" ],
          "PATTY":    [ "PAT", "PATRICIA" ],

          "JEFF":     [ "JEFFREY", "JEFFERY", "GEOFF" ],
          "JEFFREY":  [ "JEFF", "JEFFERY" ],
          "JEFFERY":  [ "JEFF", "JEFFREY" ],
          "GEOFF":    [ "JEFF", "GEOFFREY" ],
          "GEOFFREY": [ "GEOFF" ] }

        In other words, for each possible name, we maintain a set of potential
        associated nicknames.

        When we select a nickname, we will use the gender information (if
        given to select an appropriate value.
        '''

        nicknames = {}

        with open(file, "r") as csvfile:
            reader = csv.reader(csvfile)
            for record in reader:
                for name_l in record:
                    for name_r in record:
                        name_l = name_l.upper()
                        name_r = name_r.upper()
                        if name_l == name_r: continue  # skip matches, eg PAT == PAT

                        try:
                            a = nicknames[name_l]
                        except KeyError:
                            nicknames[name_l] = []
                            a = nicknames[name_l]

                        exists = False
                        for e in a:
                            if e == name_r:
                                exists = True
                                break

                        if not exists:
                            a.append(name_r)

        return nicknames

    @staticmethod
    def _load_freq(file):
        '''
        This method is intended to work with files provided by the US Census
        and require the format "NAME  PCT  CUMPCT RANK":

            JAMES          3.318  3.318      1
            JOHN           3.271  6.589      2
            ROBERT         3.143  9.732      3

        NAME is the name for a specific entry (line).  PCT is the percentage
        of the population which was observed to use this name.  CUM_PCT is
        the cumulative percentage of all names observed up to and including
        the current name.  Rank is the absolute ordinal rank of the name
        when sorted by PCT.

        Truth be told, only the NAME and PCT fields are required by this
        loader.

        Male distributions may be found here:

            https://www2.census.gov/topics/genealogy/1990surnames/dist.male.first

        Female distributions may be found here:

            https://www2.census.gov/topics/genealogy/1990surnames/dist.female.first

        If you use data from other sources, either implement a new loader
        method in this class or adapt your data to conform with this format.

        This method returns a dict containing "NAME: PCT" pairs.
        '''

        freq = {}
        with gzip.open(file, "r") as dist:
            for line in dist:
                line = line.decode("utf-8")
                fields = line.strip().split("|")
                name = fields[0].upper()
                pct = float(fields[1]) / 100
                freq[name] = pct

        return freq


    def getNickname(self, name, gender=None):
        '''
        Each nickname has a frequency (weight) which makes it more or less
        common than others in the list.  This weight is taken from the name
        frequency tables.  A name with a weight of 0.0 will never be
        selected.
        '''
        nicks = self.nicknames.get(name.upper(), None)
        
        if nicks is None:
            return

        if gender is not None: gender = gender.upper()
        weights = []    # a list of weights corresponding to each name in 'a'

        for n in nicks:
            # Add the weight for the specified gender.  If we don't have a
            # gender, we'll sum the weights for both male and female dists.

            w = 0.0
            if gender in [ 'M', "MALE", None ]:
                w += self.male_dist.get(n.upper(), 0.0)

            if gender in [ 'F', "FEMALE", None ]:
                w += self.female_dist.get(n.upper(), 0.0)

            weights.append(w)

        tot_weight = sum(weights)

        if tot_weight == 0.0:
            # no valid aliases for this name/gender
            return None

        r = random.uniform(0, tot_weight)
        cum_pct = 0.0
        prev_pct = 0.0
        for e in zip(nicks, weights):
            cum_pct += e[1]
            if r >= prev_pct and r < cum_pct:
                return e[0]

        return None

def main(argv):
    ns = USCensusNameSet()
    for i in range(10):
        print(str(ns.create(married=True, gender='F')))

    return 0

if __name__ == '__main__':
    main(sys.argv)
