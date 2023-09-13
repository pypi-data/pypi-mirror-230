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

from django.urls import path
from django_apiview.utils import get_setting_value
from django_apiview.swagger_ui import views

DJANGO_APIVIEW_SWAGGER_MAIN_PAGE_NAME = get_setting_value(
    "DJANGO_APIVIEW_SWAGGER_MAIN_PAGE_NAME", "swagger-ui.html"
)
DJANGO_APIVIEW_SWAGGER_INIT_JS_NAME = get_setting_value(
    "DJANGO_APIVIEW_SWAGGER_INIT_JS_NAME", "swagger-ui-initializer.js"
)
DJANGO_APIVIEW_SWAGGER_META_JS_NAME = get_setting_value(
    "DJANGO_APIVIEW_SWAGGER_META_JS_NAME", "swagger-ui-meta.json"
)
DJANGO_APIVIEW_SWAGGER_MAIN_PAGE_VIEWNAME = get_setting_value(
    "DJANGO_APIVIEW_SWAGGER_MAIN_PAGE_VIEWNAME", "django_apiview_swagger_ui_main"
)
DJANGO_APIVIEW_SWAGGER_INIT_JS_VIEWNAME = get_setting_value(
    "DJANGO_APIVIEW_SWAGGER_INIT_JS_VIEWNAME", "django_apiview_swagger_ui_initializer"
)
DJANGO_APIVIEW_SWAGGER_META_JS_VIEWNAME = get_setting_value(
    "DJANGO_APIVIEW_SWAGGER_META_JS_VIEWNAME", "django_apiview_swagger_ui_meta"
)

urlpatterns = [
    path(
        DJANGO_APIVIEW_SWAGGER_MAIN_PAGE_NAME,
        views.swagger_ui_view,
        name=DJANGO_APIVIEW_SWAGGER_MAIN_PAGE_VIEWNAME,
    ),
    path(
        DJANGO_APIVIEW_SWAGGER_INIT_JS_NAME,
        views.swagger_ui_initializer,
        name=DJANGO_APIVIEW_SWAGGER_INIT_JS_VIEWNAME,
    ),
    path(
        DJANGO_APIVIEW_SWAGGER_META_JS_NAME,
        views.swagger_ui_meta,
        name=DJANGO_APIVIEW_SWAGGER_META_JS_VIEWNAME,
    ),
]
