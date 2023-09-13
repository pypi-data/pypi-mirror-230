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

import json
from zenutils import cacheutils
from magic_import import import_from_string

from django.conf import settings as global_settings


__all__ = [
    "get_request_data",
    "get_setting_value",
]


def _get_request_data(request, extra_view_parameters):
    """从请求头&请求体中获取有效数据。"""
    data = {"_request": request}
    data.update(extra_view_parameters)
    # 将HEADERS中的数据转化后保存到data中，供后续使用
    for name, value in request.META.items():
        if isinstance(value, str) and name.startswith("HTTP_"):
            name = name[5:].lower().replace("-", "_")
            data[name] = value
    # 将GET中的数据转化后保存到data中，供后续使用
    for name, _ in request.GET.items():
        value = request.GET.getlist(name)
        if isinstance(value, (list, tuple, set)) and len(value) == 1:
            data[name] = value[0]
        else:
            data[name] = value
    # 将POST中的数据转化后保存到data中，供后续使用
    _form = {}
    for name, _ in request.POST.items():
        value = request.POST.getlist(name)
        if isinstance(value, (list, tuple, set)) and len(value) == 1:
            value = value[0]
        data[name] = value
        _form[name] = value
    data["_form"] = _form
    # 尝试将PAYLOAD转化在json数据保存到data中，供后续使用
    # 如果有文件上传的请求，直接引用request.body将会出错
    if not "multipart/form-data" in request.META.get("CONTENT_TYPE", ""):
        request_body_flag = True
        try:
            request.body
        except:
            request_body_flag = False
        if request_body_flag and request.body:
            try:
                payload = json.loads(request.body)
                data["_form"] = payload
                data["_payload"] = payload
                data.update(payload)
            except:
                pass
    # 尝试将FILES数据保存到data中，供后续使用
    _files = {}
    for name, fobj in request.FILES.items():
        data[name] = fobj
        _files[name] = fobj
    data["_files"] = _files
    return data


def get_request_data(request, extra_view_parameters):
    """获取请求头&请求体中的有效数据。将将结果数据缓存至request对象中。"""
    return cacheutils.get_cached_value(
        request,
        "_django_apiview_request_data",
        _get_request_data,
        request,
        extra_view_parameters,
    )


def get_setting_value(config_name, default=None):
    """Get value form global django settings by config name."""
    value = getattr(global_settings, config_name, default)
    if not value:
        return value
    if not isinstance(value, str):
        return value
    try:
        ivalue = import_from_string(value)
    except Exception:
        ivalue = None
    if not ivalue:
        return value
    if callable(ivalue):
        return ivalue()
    return ivalue
