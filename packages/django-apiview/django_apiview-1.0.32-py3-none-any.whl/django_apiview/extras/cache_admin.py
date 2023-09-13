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

from django_apiview.helpers.cache_cleaners import *
from django_apiview.helpers.cache import *

# new applications don't import things here.
# new applications must import all things from django_apiviews.views.

import warnings

warnings.warn("django_apiview.extra module is deprecated.", DeprecationWarning)
