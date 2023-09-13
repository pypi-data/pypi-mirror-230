#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import bizerror
from zenutils import typingutils
from zenutils import funcutils

from django_apiview.base import ApiviewDecorator

__all__ = [
    "requires",
    "choices",
    "between",
    "string_length_limit",
]


class requires(ApiviewDecorator):
    """Make sure the parameters are given.

    @Example:
        @apiview
        @requires("param1", "param2")
        def view_func(param1, param2):
            pass

    """

    def __init__(self, *required_parameter_names):
        self.required_parameter_names = required_parameter_names

    def process(self, _django_apiview_func, _django_apiview_request):
        missing_names = []
        for name in self.required_parameter_names:
            if isinstance(name, str):
                if not name in _django_apiview_request.data:
                    missing_names.append(name)
            elif isinstance(name, (list, set, tuple)):
                flag = False
                for element in name:
                    if _django_apiview_request.data.get(element, None):
                        flag = True
                        break
                if not flag:
                    missing_names.append("({0})".format(" or ".join(name)))
        if missing_names:
            raise bizerror.MissingParameter(parameter=",".join(missing_names))
        return super().process(_django_apiview_func, _django_apiview_request)


class choices(ApiviewDecorator):
    """Make sure field's value is in the choices.

    @Example:
        @apiview
        @choices("param1", ["value1", "value2"])
        def view_func(param1):
            pass
    """

    def __init__(self, field, choices, annotation=None, allow_none=False):
        self.field = field
        self.choices = choices
        self.annotation = annotation
        self.allow_none = allow_none

    def process(self, _django_apiview_func, _django_apiview_request):
        if callable(self.choices):
            params = funcutils.get_inject_params(
                self.choices, _django_apiview_request.data
            )
            values = self.choices(**params)
        else:
            values = self.choices
        value = _django_apiview_request.data.get(self.field, None)
        if self.annotation:
            value = typingutils.smart_cast(self.annotation, value)
        if (self.allow_none and value is None) or (value in self.choices):
            return super().process(_django_apiview_func, _django_apiview_request)
        else:
            raise bizerror.BadParameter(
                "field {0}'s value '{1}' is not in choices {2}.".format(
                    self.field, value, values
                )
            )


class between(ApiviewDecorator):
    """Make sure field's numeric value is in range of (min, max).

    @Example:
        @apiview
        def between("param1", 0, 10)
        def view_func(param1):
            pass
    """

    def __init__(
        self,
        field,
        min,
        max,
        include_min=True,
        include_max=True,
        annotation=typingutils.Number,
        allow_none=False,
    ):
        self.field = field
        self.min = min
        self.max = max
        self.include_min = include_min
        self.include_max = include_max
        self.annotation = annotation
        self.allow_none = allow_none

    def process(self, _django_apiview_func, _django_apiview_request):
        field = self.field
        min = self.min
        max = self.max
        include_min = self.include_min
        include_max = self.include_max
        annotation = self.annotation
        allow_none = self.allow_none

        if callable(min):
            params = funcutils.get_inject_params(min, _django_apiview_request.data)
            min_value = min(**params)
        else:
            min_value = typingutils.smart_cast(annotation, min)
        if callable(max):
            params = funcutils.get_inject_params(max, _django_apiview_request.data)
            max_value = max(**params)
        else:
            max_value = typingutils.smart_cast(annotation, max)
        value = _django_apiview_request.data.get(field, None)
        value = typingutils.smart_cast(self.annotation, value)
        if (allow_none and value is None) or (
            (include_min and min_value <= value or min_value < value)
            and (include_max and max_value >= value or max_value > value)
        ):
            return super().process(_django_apiview_func, _django_apiview_request)
        else:
            raise bizerror.BadParameter(
                "field {0}'s value '{1}' is not in range of {2}{3}, {4}{5}.".format(
                    field,
                    value,
                    include_min and "[" or "(",
                    min_value,
                    max_value,
                    include_max and "]" or ")",
                )
            )


class string_length_limit(ApiviewDecorator):
    """Check string parameter length.

    @Example:
        @apiview
        @string_length_limit("param1", 64, 2)
        def view_func(param1):
            pass
    """

    def __init__(
        self,
        field,
        max_length,
        min_length=0,
        string_too_short_error_message=None,
        string_too_long_error_message=None,
    ):
        self.field = field
        self.max_length = max_length
        self.min_length = min_length
        self.string_too_short_error_message = string_too_short_error_message
        self.string_too_long_error_message = string_too_long_error_message

    def process(self, _django_apiview_func, _django_apiview_request):
        value = _django_apiview_request.data.get(self.field, None)
        if not value is None:
            value_length = len(value)
            if value_length < self.min_length:
                raise bizerror.StringTooShort(
                    message=self.string_too_short_error_message,
                    min_length=self.min_length,
                )
            if value_length > self.max_length:
                raise bizerror.StringTooLong(
                    message=self.string_too_long_error_message,
                    max_length=self.max_length,
                )
        return super().process(_django_apiview_func, _django_apiview_request)
