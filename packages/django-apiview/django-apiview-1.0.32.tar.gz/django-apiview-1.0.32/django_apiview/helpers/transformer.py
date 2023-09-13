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

from zenutils import baseutils

from django_apiview.base import ApiviewDecorator

__all__ = [
    "cookie_variable",
    "meta_variable",
    "body_alias",
]


class body_alias(ApiviewDecorator):
    """Assign the whole body payload to a new variable.

    @Example:
        @apiview
        @body_alias("user")
        def view_func(user): # the post body json will be assigned to variable user
            pass
    """

    def __init__(self, variable_name):
        self.variable_name = variable_name

    def __call__(self, func):
        func._django_apiview_body_alias = self.variable_name
        return super().__call__(func)

    def process(self, _django_apiview_func, _django_apiview_request):
        _django_apiview_request.data[
            self.variable_name
        ] = _django_apiview_request.data.get(
            "_payload", _django_apiview_request.data.get("_form", None)
        )
        return super().process(_django_apiview_func, _django_apiview_request)


class cookie_variable(ApiviewDecorator):
    """Get variable from cookies.

    @Example:
        @apiview
        @cookie_variable("userid")
        def view_func1(userid):
            pass

        @apiview
        @cookie_variable("userid", "uid")
        def view_func2(userid): # cookie key is "uid", and assigned the cookie value to variable "userid"
            pass
    """

    def __init__(self, variable_name, cookie_name=None, default=baseutils.Null):
        """
        variable_name: 业务控制器需要的变量名。
        cookie_name: 提取cookie_name对应的值作为业务控制器所需变量的值。
        default: cookie_name所对应的cookie不存在时，默认的变量值。如果不设置default值，则当没有cookie_name所对应的cookie值，ApiviewRequest.data中不会加入variable_name键值对。
        """
        self.variable_name = variable_name
        self.cookie_name = cookie_name or self.variable_name
        self.default = default

    def process(self, _django_apiview_func, _django_apiview_request):
        value = _django_apiview_request.request.COOKIES.get(
            self.cookie_name, baseutils.Null
        )
        if (
            value is baseutils.Null
        ):  # 如果cookie中不存在cookie_name所对应的值，则value需要设置为self.default
            value = self.default
        if (
            value != baseutils.Null
        ):  # 如果self.default也没有有效值，则ApiviewRequest.data中不加有效的self.variable_name的键值对。注意：控制器有可能因为缺少必要参数而报错。
            _django_apiview_request.data[self.variable_name] = value
        return super().process(_django_apiview_func, _django_apiview_request)


class meta_variable(ApiviewDecorator):
    """Get variable from meta.

    @Example:
        @apiview
        @meta_variable("aclkey", "HTTP_ACLKEY")
        def view_func1(aclkey): # mostly Django's meta key is startswith HTTP_
            pass
    """

    def __init__(self, variable_name, meta_name, default=baseutils.Null):
        """
        variable_name: 业务控制器需要的变量名。
        meta_name: 提取meta_name对应的值作为业务控制器所需变量的值。注意：请求头将被转化为HTTP_XXX格式的meta_name，如请求头Test-Auth-Key将被转化为HTTP_TEST_AUTH_KEY。
        default: meta_name所对应的值不存在时，默认的变量值。如果不设置default值，则当没有meta_name所对应的值时，ApiviewRequest.data中不会加入variable_name健值对。

        注意：
        ApiviewRequest.data中已经加入了所有请求头转化的变量。如：Test-Auth_key将被转化为test_auth_key控制器变量。
        """
        self.variable_name = variable_name
        self.meta_name = meta_name
        self.default = default

    def process(self, _django_apiview_func, _django_apiview_request):
        value = _django_apiview_request.request.META.get(self.meta_name, baseutils.Null)
        if value is baseutils.Null:  # 如果meta中不存在meta_name所对应的值，则value需要设置为self.default
            value = self.default
        if (
            value != baseutils.Null
        ):  # 如果self.default也没有有效值，则ApiviewRequest.data中不加有效的self.variable_name的健值对。注意：控制器有可能因为缺少必要参数而报错。
            _django_apiview_request.data[self.variable_name] = value
        return super().process(_django_apiview_func, _django_apiview_request)
