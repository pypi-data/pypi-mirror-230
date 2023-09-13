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
import json

from django.conf import settings

from zenutils import strutils
from zenutils import funcutils
from zenutils import jsonutils

from django_apiview.base import ApiviewDecorator

logger = logging.getLogger(__name__)
__all__ = [
    "cache",
]


class cache(ApiviewDecorator):
    """接口缓存支持。支持模型数据变动联动缓存清理。"""

    related_models_mapping = {}

    @classmethod
    def get_entry_points(cls, app_label=None):
        if not app_label:
            eps = list(cls.related_models_mapping.values())
            eps.sort(key=lambda x: x["entry_point"])
            return eps
        else:
            eps = []
            for ep in list(cls.related_models_mapping.keys()):
                if app_label == ep.split(".")[0]:
                    eps.append(cls.related_models_mapping[ep])
            eps.sort(key=lambda x: x["entry_point"])
            return eps

    def keep_related_models_mapping(self):
        entry_point = id(self)
        self.related_models_mapping[entry_point] = {
            "entry_point": entry_point,
            "related_models": [] + self.related_models,
            "key": self.key,
        }
        logger.info(
            "Cache entry discovered: {0}".format(
                self.related_models_mapping[entry_point]
            )
        )

    def __init__(
        self,
        key,
        expire=None,
        cache_name="default",
        get_from_cache=None,
        set_to_cache=True,
        disable_get_from_cache_header=None,
        batch_mode=False,
        ignore_cache_errors=True,
        related_models=None,
    ):
        self.key = key
        self.expire = expire or getattr(
            settings, "DJANGO_APIVIEW_DEFAULT_CACHE_EXPIRE", None
        )
        self.expire = self.expire and int(self.expire) or None
        self.cache_name = cache_name
        self.get_from_cache = get_from_cache
        self.set_to_cache = set_to_cache
        self.disable_get_from_cache_header = disable_get_from_cache_header or getattr(
            settings, "DJANGO_APIVIEW_DISABLE_CACHE_HEADER_NAME", "HTTP_DISABLE_CACHE"
        )
        self.batch_mode = batch_mode
        self.ignore_cache_errors = ignore_cache_errors
        self.related_models = related_models or []
        self.keep_related_models_mapping()

    def process(self, _django_apiview_func, _django_apiview_request):
        # Import here, so that we don't need django-redis by default.
        # Only if you use cache, then you need pip install django-redis
        from django_redis import get_redis_connection

        key_template = self.key
        expire = self.expire
        cache_name = self.cache_name
        get_from_cache = self.get_from_cache
        set_to_cache = self.set_to_cache
        disable_get_from_cache_header = self.disable_get_from_cache_header
        batch_mode = self.batch_mode
        ignore_cache_errors = self.ignore_cache_errors

        if get_from_cache == False:
            get_from_cache_final = False
        else:
            if (
                _django_apiview_request.request.META.get(
                    disable_get_from_cache_header, "false"
                )
                == "true"
            ):
                get_from_cache_final = False
            else:
                get_from_cache_final = True

        set_to_cache_final = set_to_cache
        use_cache = get_from_cache_final or set_to_cache_final

        cache = None
        if use_cache:
            try:
                cache = get_redis_connection(cache_name)
            except Exception as error:
                logger.exception(
                    "get redis connection failed @cache, error_message={0}".format(
                        str(error)
                    )
                )
                if ignore_cache_errors:
                    cache = None
                else:
                    raise

        if cache and get_from_cache:
            try:
                key = strutils.format_with_mapping(
                    key_template,
                    funcutils.chain(
                        strutils.none_to_empty_string, strutils.strip_string
                    ),
                    **_django_apiview_request.data,
                )
                result_text = cache.get(key)
                if not result_text is None:
                    return json.loads(result_text)
            except Exception as error:
                logger.exception(
                    "query redis failed @cache, error_message={0}".format(str(error))
                )
                if not ignore_cache_errors:
                    raise

        result = super().process(_django_apiview_func, _django_apiview_request)

        def _set_cache(result, **kwargs):
            if isinstance(result, dict):
                key = strutils.format_with_mapping(
                    key_template,
                    funcutils.chain(
                        strutils.none_to_empty_string, strutils.strip_string
                    ),
                    **_django_apiview_request.data,
                    **result,
                    **kwargs,
                )
            else:
                key = strutils.format_with_mapping(
                    key_template,
                    funcutils.chain(
                        strutils.none_to_empty_string, strutils.strip_string
                    ),
                    **_django_apiview_request.data,
                    **kwargs,
                )
            result_text = jsonutils.simple_json_dumps(
                result, allow_nan=True, sort_keys=True
            )
            cache.set(key, result_text)
            if expire:
                cache.expire(
                    key, expire
                )  # Old version redis don't support add ttl while doing set key value, so do set ttl separately

        if cache and set_to_cache_final:
            try:
                if batch_mode:
                    if isinstance(result, list):
                        for element in result:
                            _set_cache(element)
                    elif isinstance(result, dict):
                        for key, value in result.items():
                            _set_cache(value, __key=key, __value=value)
                else:
                    _set_cache(result)
            except Exception as error:
                logger.exception(
                    "write redis failed @cache, key={0}, error_message={1}".format(
                        self.key, str(error)
                    )
                )
                if not ignore_cache_errors:
                    raise

        return result
