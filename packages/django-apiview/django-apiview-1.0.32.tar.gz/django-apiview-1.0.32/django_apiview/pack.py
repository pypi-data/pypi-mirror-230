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
from datetime import datetime

import bizerror
from zenutils import jsonutils
from zenutils import strutils
from fastutils import cipherutils
from fastutils import rsautils

from django_middleware_request_id.middlewares import get_request_id

__all__ = [
    "AbstractResultPacker",
    "SimpleJsonResultPacker",
    "SafeJsonResultPacker",
    "DeetrResultPacker",
    "DmrsPacker",
]


class AbstractResultPacker(object):
    """第1个位置参数加入了后缀，避免与kwargs中的参数冲突。"""

    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        raise NotImplementedError()

    def pack_error(self, _error_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        raise NotImplementedError()

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        raise NotImplementedError()


class DmrsPacker(AbstractResultPacker):
    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        result = _result_Pu1dvy86uRLpdNu2Czyf
        return {
            "data": result,
            "message": "OK",
            "returnCode": 0,
            "successSign": True,
        }

    def pack_error(self, _error_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        error = bizerror.BizError(_error_Pu1dvy86uRLpdNu2Czyf)
        return {
            "data": None,
            "message": error.message,
            "returnCode": error.code,
            "successSign": False,
        }

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        data = _data_Pu1dvy86uRLpdNu2Czyf
        if not data:
            raise bizerror.BadResponseContent(content=data)
        if isinstance(data, (str, bytes)):
            try:
                data = json.loads(data)
            except Exception:
                raise bizerror.ParseJsonError(text=data)
        if not isinstance(data, dict):
            raise bizerror.BadResponseContent(content=data)
        if not "successSign" in data:
            raise bizerror.BadResponseContent(content=data)
        if data["successSign"]:
            if not "data" in data:
                raise bizerror.BadResponseContent(content=data)
            else:
                return data["data"]
        else:
            if not "message" in data:
                raise bizerror.BadResponseContent(content=data)
            if not "returnCode" in data:
                raise bizerror.BadResponseContent(content=data)
            raise bizerror.BizError(message=data["message"], code=data["returnCode"])


class DeetrResultPacker(AbstractResultPacker):
    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        result = _result_Pu1dvy86uRLpdNu2Czyf
        return {
            "data": result,
            "errcode": 0,
            "errmsg": "OK",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reqid": get_request_id(),
        }

    def pack_error(self, _error_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        error = bizerror.BizError(_error_Pu1dvy86uRLpdNu2Czyf)
        return {
            "data": None,
            "errcode": error.code,
            "errmsg": error.message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reqid": get_request_id(),
        }

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        data = _data_Pu1dvy86uRLpdNu2Czyf
        if not data:
            raise bizerror.BadResponseContent(content=data)
        if isinstance(data, (str, bytes)):
            try:
                data = json.loads(data)
            except Exception:
                raise bizerror.ParseJsonError(text=data)
        if not isinstance(data, dict):
            raise bizerror.BadResponseContent(content=data)
        if not "errcode" in data:
            raise bizerror.BadResponseContent(content=data)
        if data["errcode"] == 0:
            if not "data" in data:
                raise bizerror.BadResponseContent(content=data)
            else:
                return data["data"]
        else:
            if not "errmsg" in data:
                raise bizerror.BadResponseContent(content=data)
            else:
                raise bizerror.BizError(message=data["errmsg"], code=data["errcode"])


class SimpleJsonResultPacker(AbstractResultPacker):
    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        result = _result_Pu1dvy86uRLpdNu2Czyf
        return {
            "success": True,
            "result": result,
        }

    def pack_error(self, _error_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        error = _error_Pu1dvy86uRLpdNu2Czyf
        return {
            "success": False,
            "error": error,
        }

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        data = _data_Pu1dvy86uRLpdNu2Czyf
        if not data:
            raise bizerror.BadResponseContent(content=data)
        if isinstance(data, (str, bytes)):
            try:
                data = json.loads(data)
            except Exception:
                raise bizerror.ParseJsonError(text=data)
        if not isinstance(data, dict):
            raise bizerror.BadResponseContent(content=data)
        if not "success" in data:
            raise bizerror.BadResponseContent(content=data)
        success = data["success"]
        if success == True:
            if not "result" in data:
                raise bizerror.BadResponseContent(content=data)
            else:
                return data["result"]
        else:
            if not "error" in data:
                raise bizerror.BadResponseContent(content=data)
            else:
                raise bizerror.BizError(data["error"])


class SafeJsonResultPacker(SimpleJsonResultPacker):
    def __init__(
        self,
        result_encoder=cipherutils.SafeBase64Encoder(),
        password_length=32,
        client_id_fieldname="clientId",
        encrypted_password_fieldname="encryptedPassword",
        encrypted_data_fieldname="encryptedData",
    ):
        self.password_length = password_length
        self.encrypted_password_fieldname = encrypted_password_fieldname
        self.encrypted_data_fieldname = encrypted_data_fieldname
        self.result_encoder = result_encoder
        self.client_id_fieldname = client_id_fieldname

    def pack_result(self, _result_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        result = _result_Pu1dvy86uRLpdNu2Czyf
        result = super().pack_result(result, **kwargs)
        return self.encrypt_data(result, **kwargs)

    def pack_error(self, _error_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        error = _error_Pu1dvy86uRLpdNu2Czyf
        error = super().pack_error(error, **kwargs)
        return self.encrypt_data(_error_Pu1dvy86uRLpdNu2Czyf, **kwargs)

    def encrypt_data(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        data = _data_Pu1dvy86uRLpdNu2Czyf
        # get client rsa publickey
        get_client_rsa_publickey = kwargs["get_client_rsa_publickey"]
        client_id = kwargs[self.client_id_fieldname]
        client_rsa_publickey = get_client_rsa_publickey(client_id)
        # do data encrypt
        result_text = jsonutils.simple_json_dumps(data)
        password = strutils.random_string(self.password_length)
        result_cipher = cipherutils.AesCipher(
            password=password, result_encoder=self.result_encoder
        )
        result_data = result_cipher.encrypt(result_text.encode("utf-8"))
        encrypted_password = rsautils.encrypt(password.encode(), client_rsa_publickey)
        return {
            self.encrypted_password_fieldname: encrypted_password,
            self.encrypted_data_fieldname: result_data,
        }

    def unpack(self, _data_Pu1dvy86uRLpdNu2Czyf, **kwargs):
        data = _data_Pu1dvy86uRLpdNu2Czyf
        if not data:
            raise bizerror.BadResponseContent(content=data)
        if isinstance(data, (str, bytes)):
            try:
                data = json.loads(data)
            except Exception:
                raise bizerror.ParseJsonError(text=data)
        client_rsa_privatekey = kwargs["client_rsa_privatekey"]
        encrypted_password = data[self.encrypted_password_fieldname]
        encrypted_data = data[self.encrypted_data_fieldname]
        password = rsautils.decrypt(encrypted_password, client_rsa_privatekey)
        result_cipher = cipherutils.AesCipher(
            password=password, result_encoder=self.result_encoder
        )
        data_json = result_cipher.decrypt(encrypted_data)
        return super().unpack(data_json, **kwargs)
