# -*- coding: utf-8 -*-

#**************************************************************************************************#
#                               PYUTILS - SOME PYTHON UTILITY FUNCTIONS
#
#   Description : Toolbox for Python scripts
#   Authors     : David Fischer
#   Contact     : david.fischer.ch@gmail.com
#   Copyright   : 2013-2013 David Fischer. All rights reserved.
#**************************************************************************************************#
#
#  This file is part of pyutils.
#
#  This project is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with this project.
#  If not, see <http://www.gnu.org/licenses/>
#
#  Retrieved from git clone https://github.com/davidfischer-ch/pyutils.git

import inspect, json, pickle
from bson.objectid import ObjectId
from codecs import open
from py_unicode import string_types, to_bytes


# Object <-> Pickle file -----------------------------------------------------------------------------------------------

class PickleableObject(object):
    u"""
    An :class:`object` serializable/deserializable by :mod:`pickle`.
    """
    @classmethod
    def read(cls, filename, store_filename=False, create_if_error=False, **kwargs):
        u"""
        Return a deserialized instance of a pickleable object loaded from a file.
        """
        try:
            the_object = pickle.load(open(filename, u'rb'))
        except:
            if not create_if_error:
                raise
            the_object = cls(**kwargs)
            the_object.write(filename, store_filename=store_filename)
        if store_filename:
            the_object._pickle_filename = filename
        return the_object

    def write(self, filename=None, store_filename=False):
        u"""
        Serialize ``self`` to a file, excluding the attribute ``_pickle_filename``.
        """
        pickle_filename = getattr(self, '_pickle_filename', None)
        filename = filename or pickle_filename
        if filename is None:
            raise ValueError(to_bytes(u'A filename must be specified'))
        try:
            if pickle_filename:
                del self._pickle_filename
            pickle.dump(self, open(filename, u'wb'))
        finally:
            if store_filename:
                self._pickle_filename = filename
            elif pickle_filename:
                self._pickle_filename = pickle_filename


# Object <-> JSON string -----------------------------------------------------------------------------------------------

## http://stackoverflow.com/questions/6255387/mongodb-object-serialized-as-json
class SmartJSONEncoderV1(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return unicode(obj)
        if hasattr(obj, u'__dict__'):
            return obj.__dict__
        return super(SmartJSONEncoderV1, self).default(obj)


class SmartJSONEncoderV2(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return unicode(obj)
        attributes = {}
        for a in inspect.getmembers(obj):
            if inspect.isroutine(a[1]) or inspect.isbuiltin(a[1]) or a[0].startswith(u'__'):
                continue
            attributes[a[0]] = a[1]
        return attributes

def object2json(obj, include_properties):
    u"""
    Serialize an :class:`object` to a JSON string.
    """
    return json.dumps(obj, cls=(SmartJSONEncoderV2 if include_properties else SmartJSONEncoderV1))


def json2object(cls, json_string, inspect_constructor):
    u"""
    Deserialize the JSON string ``json_string`` to an instance of ``cls``.
    """
    return dict2object(cls, json.loads(json_string), inspect_constructor)


def jsonfile2object(cls, filename_or_file, inspect_constructor):
    u"""
    Load and deserialize the JSON string stored in a file ``filename`` to an instance of ``cls``.

    .. warning::

        Class constructor is responsible of converting attributes to instances of classes with ``dict2object``.

    **Example usage**:

    Define the sample class, instantiate it and serialize it to a file:

    >>> import os
    >>> from nose.tools import assert_equal
    >>> class Point(object):
    ...     def __init__(self, name=None, x=0, y=0):
    ...         self.name = name
    ...         self.x = x
    ...         self.y = y
    >>> p1 = Point(name=u'My point', x=10, y=-5)
    >>> open(u'test.json', u'w', encoding=u'utf-8').write(object2json(p1, include_properties=False))

    Deserialize the freshly saved file:

    >>> p2 = jsonfile2object(Point, u'test.json', inspect_constructor=False)
    >>> assert_equal(p1.__dict__, p2.__dict__)
    >>> p2 = jsonfile2object(Point, open(u'test.json', u'r', encoding=u'utf-8'), inspect_constructor=False)
    >>> assert_equal(p1.__dict__, p2.__dict__)
    >>> os.remove(u'test.json')
    """
    f = (open(filename_or_file, u'r', encoding=u'utf-8') if isinstance(filename_or_file, string_types)
         else filename_or_file)
    return json2object(cls, f.read(), inspect_constructor)


class JsoneableObject(object):
    u"""
    An :class:`object` serializable/deserializable by :mod:`json`.

    .. warning::

        Class constructor is responsible of converting attributes to instances of classes with ``dict2object``.

    Convert-back from JSON strings containing extra parameters:

    >>> from nose.tools import assert_equal

    >>> class User(object):
    ...     def __init__(self, first_name, last_name):
    ...         self.first_name, self.last_name = first_name, last_name
    ...     @property
    ...     def name(self):
    ...         return u'{0} {1}'.format(self.first_name, self.last_name)

    >>> class Media(JsoneableObject):
    ...     def __init__(self, author, title):
    ...         self.author = dict2object(User, author, True) if isinstance(author, dict) else author
    ...         self.title = title

    Sounds good:

    >>> media = Media(User(u'Andrés', u'Revuelta'), u'Vacances à Phucket')
    >>> media_json = media.to_json(include_properties=False)
    >>> media_back = Media.from_json(media_json, inspect_constructor=True)
    >>> isinstance(media_back.author, User)
    True
    >>> assert_equal(media_back.author.__dict__, media.author.__dict__)

    A second example handling extra arguments by using ``**kwargs`` (a.k.a the dirty way):

    >>> class User(object):
    ...     def __init__(self, first_name, last_name, **kwargs):
    ...         self.first_name, self.last_name = first_name, last_name
    ...     @property
    ...     def name(self):
    ...         return u'{0} {1}'.format(self.first_name, self.last_name)

    >>> class Media(JsoneableObject):
    ...     def __init__(self, author, title, **kwargs):
    ...         self.author = User(**author) if isinstance(author, dict) else author
    ...         self.title = title

    Sounds good:

    >>> media = Media(User(u'Andrés', u'Revuelta'), u'Vacances à Phucket')
    >>> media_json = media.to_json(include_properties=True)
    >>> media_back = Media.from_json(media_json, inspect_constructor=False)
    >>> isinstance(media_back.author, User)
    True
    >>> assert_equal(media_back.author.__dict__, media.author.__dict__)
    """
    @classmethod
    def read(cls, filename, store_filename=False, inspect_constructor=True):
        u"""
        Return a deserialized instance of a jsoneable object loaded from a file.
        """
        with open(filename, u'r', u'utf-8') as f:
            the_object = dict2object(cls, json.loads(f.read()), inspect_constructor)
            if store_filename:
                the_object._json_filename = filename
            return the_object

    def write(self, filename=None, include_properties=False):
        u"""
        Serialize ``self`` to a file, excluding the attribute ``_json_filename``.
        """
        if filename is None and hasattr(self, u'_json_filename'):
            filename = self._json_filename
            try:
                del self._json_filename
                with open(filename, u'w', u'utf-8') as f:
                    f.write(object2json(self, include_properties))
            finally:
                self._json_filename = filename
        elif filename is not None:
            with open(filename, u'w', u'utf-8') as f:
                f.write(object2json(self, include_properties))
        else:
            raise ValueError(u'A filename must be specified')

    def to_json(self, include_properties):
        return object2json(self, include_properties)

    @classmethod
    def from_json(cls, json_string, inspect_constructor):
        return dict2object(cls, json.loads(json_string), inspect_constructor)


# Object <-> Dictionary ------------------------------------------------------------------------------------------------

def object2dict(obj, include_properties):
    u"""
    Convert an :class:`object` to a python dictionary.

    .. warning::

        Current implementation serialize ``obj`` to a JSON string and then deserialize this JSON string to an instance
        of :class:`dict`.

    **Example usage**:

    Define the sample class and convert some instances to a dictionary:

    >>> from nose.tools import assert_equal
    >>> class Point(object):
    ...     def __init__(self, name, x, y, p):
    ...         self.name = name
    ...         self.x = x
    ...         self.y = y
    ...         self.p = p
    ...     @property
    ...     def z(self):
    ...         return self.x - self.y

    >>> p1_dict = {u'y': 2, u'x': 5, u'name': u'p1', u'p': {u'y': 4, u'x': 3, u'name': u'p2', u'p': None}}
    >>> assert_equal(object2dict(Point('p1', 5, 2, Point('p2', 3, 4, None)), include_properties=False), p1_dict)

    >>> p2_dict = {u'y': 4, u'p': None, u'z': -1, u'name': u'p2', u'x': 3}
    >>> p1_dict = {u'y': 2, u'p': p2_dict, u'z': 3, u'name': u'p1', u'x': 5}
    >>> assert_equal(object2dict(Point('p1', 5, 2, Point('p2', 3, 4, None)), include_properties=True), p1_dict)

    >>> p1, p2 = Point('p1', 5, 2, None), Point('p2', 3, 4, None)
    >>> p1.p, p2.p = p2, p1
    >>> print(object2dict(p1, True))
    Traceback (most recent call last):
        ...
    ValueError: Circular reference detected
    """
    return json2object(dict, object2json(obj, include_properties), inspect_constructor=False)


def object2dictV2(obj, remove_underscore):
    if isinstance(obj, dict):
        something_dict = {}
        for key, value in obj.iteritems():
            if remove_underscore and key[0] == u'_':
                key = key[1:]
            something_dict[key] = object2dict(value, remove_underscore)
        return something_dict
    elif hasattr(obj, u'__iter__'):
        return [object2dict(value, remove_underscore) for value in obj]
    elif hasattr(obj, u'__dict__'):
        something_dict = {}
        for key, value in obj.__dict__.iteritems():
            if remove_underscore and key[0] == u'_':
                key = key[1:]
            something_dict[key] = object2dict(value, remove_underscore)
        return something_dict
    return obj


def dict2object(cls, the_dict, inspect_constructor):
    u"""
    Convert a python dictionary to an instance of a class.

    * Set ``inspect_constructor`` to filter input dictionary to avoid sending unexpected keyword arguments to the
    constructor (``__init__``) of ``cls``.

    **Example usage**:

    >>> from nose.tools import assert_equal

    >>> class User(object):
    ...     def __init__(self, first_name, last_name=u'Fischer'):
    ...         self.first_name, self.last_name = first_name, last_name
    ...     @property
    ...     def name(self):
    ...        return u'{0} {1}'.format(self.first_name, self.last_name)

    >>> user_dict = {u'first_name': u'Victor', u'last_name': u'Fischer', u'unexpected': 10}

    >>> dict2object(User, user_dict, inspect_constructor=False)
    Traceback (most recent call last):
        ...
    TypeError: __init__() got an unexpected keyword argument 'unexpected'

    >>> expected = {u'first_name': 'Victor', u'last_name': 'Fischer'}
    >>> assert_equal(dict2object(User, user_dict, inspect_constructor=True).__dict__, expected)
    """
    if inspect_constructor:
        the_dict = {arg: the_dict.get(arg, None) for arg in inspect.getargspec(cls.__init__)[0] if arg != 'self'}
    return cls(**the_dict)
