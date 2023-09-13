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
import functools

import bizerror
from zenutils import jsonutils
from zenutils import funcutils
from zenutils import cacheutils
from django.http import HttpResponse

from .utils import get_request_data
from .exceptions import DoNotPack

logger = logging.getLogger(__name__)

__all__ = [
    "ApiviewDecorator",
    "ApiviewRequest",
    "Apiview",
]


class ApiviewWrapper(object):
    def process(self, _django_apiview_func, _django_apiview_request):
        if hasattr(_django_apiview_func, "_django_apiview_wrapper") and getattr(
            _django_apiview_func, "_django_apiview_wrapper"
        ):
            return _django_apiview_func(_django_apiview_request)
        else:
            logger.debug(
                "{klass} calling funcutils.call_with_inject: func={func} data={data}".format(
                    klass=self.__class__.__name__,
                    func=_django_apiview_request,
                    data=_django_apiview_request.data,
                )
            )
            result = funcutils.call_with_inject(
                _django_apiview_func, _django_apiview_request.data
            )
            logger.debug(
                "{klass} call funcutils.call_with_inject done, result={result}".format(
                    klass=self.__class__.__name__,
                    result=result,
                )
            )
            return result


class ApiviewPluginBase(ApiviewWrapper):
    """Apiview plugin base class."""

    _django_apiview_wrapper = True

    def __init__(self, _django_apiview_func):
        self._django_apiview_func = _django_apiview_func

    def __call__(self, _django_apiview_request):
        return self.process(self._django_apiview_func, _django_apiview_request)


class ApiviewDecorator(ApiviewWrapper):
    """Decorator base class."""

    def __call__(self, _django_apiview_func):
        @functools.wraps(_django_apiview_func)
        def wrapper(_django_apiview_request):
            return self.process(_django_apiview_func, _django_apiview_request)

        wrapper._django_apiview_wrapper = True
        return wrapper


class ApiviewRequest(object):
    """Process class of apiview."""

    def __init__(self, request, defaults, **kwargs):
        self._apiview_decorator = False
        self.request = request
        self.kwargs = kwargs
        self.data = {}
        self.data.update(defaults)
        self.data.update(get_request_data(self.request, self.kwargs))
        self.data["_django_apiview_request"] = self
        self.data["_django_apiview_response"] = HttpResponse(
            content_type="application/json;charset=UTF-8"
        )


class Apiview(ApiviewWrapper):
    def __init__(self, packer, preload_plugins=None, extra_parameters=None, **kwargs):
        self.packer = packer
        self.extra_parameters = extra_parameters or {}
        self.preload_plugins = preload_plugins or []
        self.apiview_init_kwargs = kwargs

    def set_packer(self, packer):
        self.packer = packer

    def add_preload_plugin(self, plugin):
        self.preload_plugins.append(plugin)

    def put_extra_parameter(self, key, value):
        self.extra_parameters[key] = value

    def put_extra_parameters(self, params):
        self.extra_parameters.update(params)

    def __call__(self, _django_apiview_func):
        """Turn the view function into apiview function. Must use as the first decorator."""

        @cacheutils.cache(
            _django_apiview_func, "_django_apiview_final_func"
        )  # _django_apiview_func引入plugin包装后最终计算函数，只能缓存至_django_apiview_func中
        def _get_django_apiview_final_func():
            target_func = _django_apiview_func
            for plugin in reversed(self.preload_plugins):
                target_func = plugin(target_func)
            return target_func

        _django_apiview_func._django_apiview_flag = True
        _django_apiview_func._django_apiview_main_wrapper = self

        @functools.wraps(_django_apiview_func)
        def wrapper(request, **kwargs):
            defaults = {}
            defaults.update(self.extra_parameters)
            defaults.update(funcutils.get_default_values(_django_apiview_func))
            _django_apiview_request = ApiviewRequest(request, defaults, **kwargs)
            package = {}
            try:
                result = self.process(
                    _get_django_apiview_final_func(), _django_apiview_request
                )
                package = self.packer.pack_result(
                    result, **_django_apiview_request.data
                )
                package_json = jsonutils.simple_json_dumps(
                    package, ensure_ascii=False, allow_nan=True, sort_keys=True
                )
                _django_apiview_request.data["_django_apiview_response"].write(
                    package_json
                )
            except DoNotPack:
                # do not need to do result pack
                pass
            except Exception as error:
                logger.exception("apiview process failed: {}".format(str(error)))
                if not isinstance(error, bizerror.BizErrorBase):
                    error = bizerror.BizError(error)
                package = self.packer.pack_error(error, **_django_apiview_request.data)
                package_json = jsonutils.simple_json_dumps(
                    package, ensure_ascii=False, allow_nan=True, sort_keys=True
                )
                _django_apiview_request.data["_django_apiview_response"].write(
                    package_json
                )
            return _django_apiview_request.data["_django_apiview_response"]

        wrapper.csrf_exempt = True
        return wrapper
