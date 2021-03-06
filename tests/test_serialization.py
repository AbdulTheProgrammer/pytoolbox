# -*- encoding: utf-8 -*-

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2015 David Fischer. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of David Fischer's pytoolbox Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/davidfischer-ch/pytoolbox.git

from __future__ import absolute_import, division, print_function, unicode_literals

import math, os

from pytoolbox.encoding import csv_reader
from pytoolbox.filesystem import remove
from pytoolbox.serialization import PickleableObject

from . import base

here = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
here = os.path.join(here, '../../..' if 'build/lib' in here else '..', 'tests')


class MyPoint(PickleableObject):

    def __init__(self, name=None, x=0, y=0):
        self.name = name
        self.x = x
        self.y = y

    @property
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y)


class TestSerialization(base.TestCase):

    tags = ('serialization', )

    def test_PickleableObject(self):
        p1 = MyPoint(name='My point', x=6, y=-3)
        p1.write('test.pkl')
        p2 = MyPoint.read('test.pkl', store_path=True)
        self.dict_equal(p2.__dict__, {'y': -3, 'x': 6, '_pickle_path': 'test.pkl', 'name': 'My point'})
        p2.write()
        p2.write('test2.pkl')
        os.remove('test.pkl')
        os.remove('test2.pkl')
        p2.write()
        self.false(os.path.exists('test2.pkl'))
        self.equal(p2._pickle_path, 'test.pkl')
        os.remove('test.pkl')
        p2.write('test2.pkl', store_path=True)
        self.false(os.path.exists('test.pkl'))
        self.equal(p2._pickle_path, 'test2.pkl')
        del p2._pickle_path
        with self.raises(ValueError):
            p2.write()
        os.remove('test2.pkl')
        remove('test3.pkl')
        p3 = MyPoint.read('test3.pkl', store_path=True, create_if_error=True, name='Default point', x=3, y=-6)
        self.dict_equal(p3.__dict__, {'x': 3, 'y': -6, '_pickle_path': 'test3.pkl', 'name': 'Default point'})
        os.remove('test3.pkl')
        with self.raises(IOError):
            MyPoint.read('test3.pkl')

    def test_csv_reader(self):
        values, i = [('David', 'Vélo'), ('Michaël', 'Tennis de table'), ('Loïc', 'Piano')], 0
        for name, hobby in csv_reader(os.path.join(here, 'unicode.csv')):
            self.tuple_equal((name, hobby), values[i])
            i += 1
