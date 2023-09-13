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

import logging

import bizerror

from django_apiview.base import ApiviewPluginBase
from django_apiview.base import ApiviewDecorator
from django_apiview.utils import get_setting_value

logger = logging.getLogger(__name__)
__all__ = [
    "allow_get",
    "allow_post",
    "allow_put",
    "allow_delete",
    "allow_patch",
    "allow_head",
    "allow_options",
    "get_default_allow_methods",
    "set_default_allow_methods",
    "RequestMethodCheckPlugin",
]


_default_allow_methods = get_setting_value(
    "DJANGO_APIVIEW_DEFAULT_ALLOW_METHODS", ["get", "post"]
)


def set_default_allow_methods(methods):
    """Set the default allow methods globally."""
    global _default_allow_methods
    _default_allow_methods = methods


def get_default_allow_methods():
    """Get current allow methods setting."""
    return _default_allow_methods


class allow_get(ApiviewDecorator):
    """Set the view to accept GET request.

    @Example:
        @apiview
        @allow_get()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_get = True
        return super().__call__(_django_apiview_func)


class allow_post(ApiviewDecorator):
    """Set the view to accept POST request.

    @Example:
        @apiview
        @allow_post()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_post = True
        return super().__call__(_django_apiview_func)


class allow_put(ApiviewDecorator):
    """Set the view to accept PUT request.

    @Example:
        @apiview
        @allow_put()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_put = True
        return super().__call__(_django_apiview_func)


class allow_delete(ApiviewDecorator):
    """Set the view to accept DELETE request.

    @Example:
        @apiview
        @allow_delete()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_delete = True
        return super().__call__(_django_apiview_func)


class allow_patch(ApiviewDecorator):
    """Set the view to accept PATCH request.

    @Example:
        @apiview
        @allow_patch()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_patch = True
        return super().__call__(_django_apiview_func)


class allow_head(ApiviewDecorator):
    """Set the view to accept HEAD request.

    @Example:
        @apiview
        @allow_head()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_head = True
        return super().__call__(_django_apiview_func)


class allow_options(ApiviewDecorator):
    """Set the view to accept OPTIONS request.

    @Example:
        @apiview
        @allow_options()
        def view_func():
            pass
    """

    def __call__(self, _django_apiview_func):
        _django_apiview_func._django_apiview_allow_options = True
        return super().__call__(_django_apiview_func)


class RequestMethodCheckPlugin(ApiviewPluginBase):
    def __call__(self, _django_apiview_request):
        _allow_methods = set([])
        _django_apiview_func = self._django_apiview_func
        _django_apiview_allow_get = getattr(
            _django_apiview_func, "_django_apiview_allow_get", None
        )
        if _django_apiview_allow_get:
            _allow_methods.add("get")
        _django_apiview_allow_post = getattr(
            _django_apiview_func, "_django_apiview_allow_post", None
        )
        if _django_apiview_allow_post:
            _allow_methods.add("post")
        _django_apiview_allow_put = getattr(
            _django_apiview_func, "_django_apiview_allow_put", None
        )
        if _django_apiview_allow_put:
            _allow_methods.add("put")
        _django_apiview_allow_delete = getattr(
            _django_apiview_func, "_django_apiview_allow_delete", None
        )
        if _django_apiview_allow_delete:
            _allow_methods.add("delete")
        _django_apiview_allow_patch = getattr(
            _django_apiview_func, "_django_apiview_allow_patch", None
        )
        if _django_apiview_allow_patch:
            _allow_methods.add("patch")
        _django_apiview_allow_head = getattr(
            _django_apiview_func, "_django_apiview_allow_head", None
        )
        if _django_apiview_allow_head:
            _allow_methods.add("head")
        _django_apiview_allow_options = getattr(
            _django_apiview_func, "_django_apiview_allow_options", None
        )
        if _django_apiview_allow_options:
            _allow_methods.add("options")
        if not _allow_methods:
            _allow_methods = set(get_default_allow_methods())
        _request = _django_apiview_request.request
        _method = _request.method.lower()
        if not _method in _allow_methods:
            raise bizerror.NotSupportedHttpMethod()
        return super().__call__(_django_apiview_request)
