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
from django.conf import settings

from fastutils import rsautils
from fastutils import cipherutils

from django_apiview.base import ApiviewDecorator

__all__ = [
    "rsa_decrypt",
    "decode_encrypted_data",
]


class rsa_decrypt(ApiviewDecorator):
    """Do rsa-decrypt to the given field with private_key."""

    def __init__(self, field, private_key):
        self.field = field
        self.private_key = private_key

    def process(self, _django_apiview_func, _django_apiview_request):
        if self.field in _django_apiview_request.data:
            field_value = _django_apiview_request.data[self.field]
            if field_value:
                field_data = rsautils.smart_get_binary_data(field_value)
                plain_data = rsautils.decrypt(field_data, self.private_key)
                plain_text = plain_data.decode("utf-8")
                _django_apiview_request.data[self.field] = plain_text
        return super().process(_django_apiview_func, _django_apiview_request)


class decode_encrypted_data(ApiviewDecorator):
    def __init__(
        self,
        result_encoder=cipherutils.SafeBase64Encoder(),
        privatekey=None,
        server_rsa_privatekey_filedname="RSA_PRIVATEKEY",
        encrypted_password_fieldname="encryptedPassword",
        encrypted_data_fieldname="encryptedData",
    ):
        self.result_encoder = result_encoder
        self.server_rsa_privatekey_filedname = server_rsa_privatekey_filedname
        self.privatekey = privatekey
        self.encrypted_password_fieldname = encrypted_password_fieldname
        self.encrypted_data_fieldname = encrypted_data_fieldname

    def process(self, _django_apiview_func, _django_apiview_request):
        privatekey = self.privatekey or getattr(
            settings, self.server_rsa_privatekey_filedname, None
        )
        encrypted_password = _django_apiview_request.data.get(
            self.encrypted_password_fieldname, ""
        )
        encrypted_data = _django_apiview_request.data.get(
            self.encrypted_data_fieldname, ""
        )
        if privatekey and encrypted_password and encrypted_data:
            password = rsautils.decrypt(encrypted_password, privatekey)
            cipher = cipherutils.AesCipher(
                password=password, result_encoder=self.result_encoder
            )
            data_text = cipher.decrypt(encrypted_data)
            data = json.loads(data_text)
            _django_apiview_request.data.update(data)
        return super().process(_django_apiview_func, _django_apiview_request)
