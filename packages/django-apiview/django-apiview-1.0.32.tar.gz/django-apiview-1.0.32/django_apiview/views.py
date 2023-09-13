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
from zenutils import funcutils

from .base import *
from .pack import *
from .exceptions import *
from .utils import *

import django_apiview.helpers.auth
import django_apiview.helpers.cache_cleaners
import django_apiview.helpers.cache
import django_apiview.helpers.cipher
import django_apiview.helpers.request_methods
import django_apiview.helpers.transformer
import django_apiview.helpers.validators

from django_apiview.helpers.auth import *
from django_apiview.helpers.cache_cleaners import *
from django_apiview.helpers.cache import *
from django_apiview.helpers.cipher import *
from django_apiview.helpers.request_methods import *
from django_apiview.helpers.validators import *
from django_apiview.helpers.transformer import *


logger = logging.getLogger(__name__)

__all__ = (
    [
        "setup_result_packer",
        "apiview",
        "safe_apiview",
    ]
    + django_apiview.helpers.auth.__all__
    + django_apiview.helpers.cache_cleaners.__all__
    + django_apiview.helpers.cache.__all__
    + django_apiview.helpers.cipher.__all__
    + django_apiview.helpers.request_methods.__all__
    + django_apiview.helpers.transformer.__all__
    + django_apiview.helpers.validators.__all__
)

_django_apiview_packer = get_setting_value(
    "DJANGO_APIVIEW_PACKER", SimpleJsonResultPacker()
)
_django_apiview_plugins = get_setting_value(
    "DJANGO_APIVIEW_PLUGINS", [RequestMethodCheckPlugin]
)
_django_apiview_kwargs = get_setting_value("DJANGO_APIVIEW_KWARGS", {})


def setup_result_packer(packer):
    global _django_apiview_packer
    _django_apiview_packer = packer


def get_result_packer():
    return _django_apiview_packer


apiview = Apiview(
    _django_apiview_packer,
    preload_plugins=_django_apiview_plugins,
    **_django_apiview_kwargs
)


def safe_apiview(packer_class=SafeJsonResultPacker, **kwargs):
    from django_apiview.helpers.cipher import decode_encrypted_data

    return Apiview(
        packer=funcutils.call_with_inject(packer_class, kwargs),
        preload_plugins=[
            funcutils.call_with_inject(decode_encrypted_data, kwargs),
        ],
        extra_parameters=kwargs,
    )
