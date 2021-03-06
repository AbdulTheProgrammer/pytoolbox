# -*- encoding: utf-8 -*-

"""
Mix-ins for building your own models fields.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from ...core import validators
from .... import collections, module

_all = module.All(globals())


class OptionsMixin(object):

    default_options = {}
    override_options = {}

    def __init__(self, **kwargs):
        super(OptionsMixin, self).__init__(**collections.merge_dicts(
            self.default_options, kwargs, self.override_options
        ))


class StripMixin(object):
    """https://code.djangoproject.com/ticket/6362#no1"""

    default_validators = [validators.EmptyValidator()]

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            value = value.strip()
            setattr(model_instance, self.attname, value)
        return value

__all__ = _all.diff(globals())
