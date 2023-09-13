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
from zenutils import funcutils

from django.conf import settings
from django_apiview.base import ApiviewDecorator


logger = logging.getLogger(__name__)
__all__ = [
    "check_aclkey",
]


class check_aclkey(ApiviewDecorator):
    """检查请求头/请求参数/请求数据中是否有aclkey字段，并且aclkey字段是否有效。

    DJANGO_APIVIEW_ACLKEY可指定有效的aclkey值。
    DJANGO_APIVIEW_ACLKEYS可以指定多个有效的aclkey值。
    请求中提交的aclkey值，只要在DJANGO_APIVIEW_ACLKEYS里面，即为有效。
    """

    def __init__(self, aclkey=None, aclkeys=None, aclkey_field_name="aclkey"):
        """
        aclkey指定有效的aclkey。可以为回调函数。
        aclkeys指定有效的aclkeys列表。可以为有效aclkey字符串列表或集合。
        aclkey_field_name指定请求中的aclkey值的提取字段。默认为：aclkey。
        """
        self.aclkey_field_name = aclkey_field_name
        self.aclkey = aclkey or getattr(
            settings, "DJANGO_APIVIEW_ACLKEY", None
        )  # 设置中如果DJANGO_APIVIEW_ACLKEY为空，则禁用DJANGO_APIVIEW_ACLKEY的检验。检验禁用，表示检验不通过。
        self.aclkeys = set(aclkeys or getattr(settings, "DJANGO_APIVIEW_ACLKEYS", []))

    def process(self, _django_apiview_func, _django_apiview_request):
        if not self.aclkey_field_name in _django_apiview_request.data:
            raise bizerror.MissingParameter(parameter=self.aclkey_field_name)
        aclkey = _django_apiview_request.data[self.aclkey_field_name]
        if not self._check_aclkey(aclkey, _django_apiview_request):
            raise bizerror.AppAuthFailed()
        return super().process(_django_apiview_func, _django_apiview_request)

    def _check_aclkey(self, aclkey, _django_apiview_request):
        # 尝试与self.aclkey进行匹配，如果匹配成功，则返回True
        if callable(self.aclkey):
            result = funcutils.call_with_inject(
                self.aclkey, _django_apiview_request.data
            )
            if result:
                return True
        else:
            if self.aclkey and (
                self.aclkey == aclkey
            ):  # 如果self.aclkey为空，则针对self.aclkey的检验不通过。
                return True
        # 如果尝试与self.aclkey匹配失败，则尝试与self.aclkeys进行匹配
        return aclkey in self.aclkeys
