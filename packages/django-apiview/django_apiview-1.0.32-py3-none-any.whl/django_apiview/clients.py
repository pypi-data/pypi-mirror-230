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

from zenutils import funcutils

from .views import get_result_packer

__all__ = [
    "ApiviewClient",
]


class ApiviewClient(object):
    def __init__(self, packer=None, retry_sleep=0, retry_limit=3):
        self.packer = packer or get_result_packer()
        self.retry_sleep = retry_sleep
        self.retry_limit = retry_limit

    def get(self, url, params=None, headers=None, verify=False):
        params = params or {}
        headers = headers or {}

        @funcutils.retry(sleep=self.retry_sleep, limit=self.retry_limit)
        def do_get():
            import requests

            return requests.get(url, params=params, headers=headers, verify=verify)

        response = do_get()
        return self.packer.unpack(response.content)

    def post(self, url, params=None, data=None, json=None, headers=None, verify=False):
        params = params or {}
        data = data or {}
        json = json or {}
        headers = headers or {}

        @funcutils.retry(sleep=self.retry_sleep, limit=self.retry_limit)
        def do_post():
            import requests

            if json:
                return requests.post(
                    url, params=params, json=json, headers=headers, verify=verify
                )
            else:
                return requests.post(
                    url, params=params, data=data, headers=headers, verify=verify
                )

        response = do_post()
        return self.packer.unpack(response.content)
