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

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DjangoApiviewConfig(AppConfig):
    name = "django_apiview"

    def ready(self):
        pass
