# -*- encoding: utf-8 -*-

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2015 David Fischer. All rights reserved.
#  Origin         : https://github.com/davidfischer-ch/pytoolbox.git
#
#**********************************************************************************************************************#

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Extra fields for your models.
"""

import math, os

from django.conf import settings
from django.db import models
from django.core import validators as dj_validators
from django.db.models.fields import files
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from . import mixins
from ...core import validators
from .... import module

_all = module.All(globals())


# Char & Text

class StripCharField(mixins.StripMixin, models.CharField):
    pass


class StripTextField(mixins.StripMixin, models.TextField):
    pass


class ExtraChoicesField(StripCharField):

    def __init__(self, verbose_name=None, extra_choices=None, **kwargs):
        self.extra_choices = extra_choices or []
        super(ExtraChoicesField, self).__init__(verbose_name=verbose_name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ExtraChoicesField, self).deconstruct()
        if self.extra_choices:
            kwargs['extra_choices'] = self.extra_choices
        return name, path, args, kwargs

    def validate(self, value, model_instance):
        choices = self._choices
        try:
            self._choices = list(self.choices) + list(self.extra_choices)
            return super(ExtraChoicesField, self).validate(value, model_instance)
        finally:
            self._choices = choices


# Date and time

class CreatedAtField(mixins.OptionsMixin, models.DateTimeField):

    default_options = {'default': now, 'editable': False, 'verbose_name': _('Created at')}


class UpdatedAtField(mixins.OptionsMixin, models.DateTimeField):

    default_options = {'auto_now': True, 'editable': False, 'verbose_name': _('Updated at')}


# Miscellaneous

class CreatedByField(mixins.OptionsMixin, models.ForeignKey):

    default_options = {'to': settings.AUTH_USER_MODEL, 'editable': False}


class MD5ChecksumField(mixins.OptionsMixin, StripCharField):

    default_error_messages = {'invalid': _('Enter a valid MD5 checksum')}
    default_options = {'max_length': 32}
    default_validators = [validators.MD5ChecksumValidator()]


class MoneyField(models.DecimalField):

    def __init__(self, max_value):
        self.max_value = max_value
        max_digits = int(math.log10(max_value)) + 3
        super(MoneyField, self).__init__(max_digits=max_digits, decimal_places=2, editable=False, validators=[
            dj_validators.MinValueValidator(0), dj_validators.MaxValueValidator(max_value)
        ])

    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()
        return name, path, [self.max_value], {}


class URLField(StripCharField, models.URLField):

    default_kwargs = {'max_length': 8000}  # http://tools.ietf.org/html/rfc7230#section-3.1.1


# Storage

class FieldFile(files.FieldFile):

    @property
    def basename(self):
        return os.path.basename(self.name) if self else None

    @basename.setter
    def basename(self, value):
        # FIXME use storage.get_valid_name
        self.name = self.field.upload_to(self.instance, os.path.basename(value))
        setattr(self.instance, self.field.name, self.name)

    @property
    def exists(self):
        return bool(self) and self.storage.exists(self.name)


class FileField(models.FileField):

    attr_class = FieldFile

__all__ = _all.diff(globals())
