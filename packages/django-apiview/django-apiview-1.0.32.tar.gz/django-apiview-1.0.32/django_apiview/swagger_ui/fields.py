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
import collections

from magic_import import import_from_string

from django.utils.translation import gettext
from django.conf import settings as global_settings
from django import forms  # we register FormFields for django.forms.fields.
from django.db import models  # we register ModelFields for django.db.models.

logger = logging.getLogger(__name__)


class SchemaField(object):
    def get_field_info(self, field):
        return {}


class FormField(SchemaField):
    def get_field_info(self, field):
        label = field.label and gettext(field.label) or ""
        help_text = field.help_text and gettext(field.help_text) or ""
        max_length = hasattr(field, "max_length") and field.max_length or None
        min_length = hasattr(field, "min_length") and field.min_length or None
        info = super().get_field_info(field)
        info.update(
            {
                "required": field.required,
            }
        )
        if label:
            info["label"] = label
        if help_text:
            info["help_text"] = "[" + help_text + "]"
        if max_length:
            info["maxLength"] = max_length
        if min_length:
            info["minLength"] = min_length
        return info


class FormRegexField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
            }
        )
        return info


class FormDecimalField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "number",
                "type": "float",
            }
        )
        return info


class FormFloatField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "number",
                "type": "float",
            }
        )
        return info


class FormDateField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "type": "date",
            }
        )
        return info


class FormDateTimeField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "type": "date-time",
            }
        )
        return info


class FormGenericIPAddressField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "ipv4_or_ipv6",
                "example": "192.168.1.1",
            }
        )
        return info


class FormEmailField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "email",
            }
        )
        return info


class FormFileField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "file",
            }
        )
        return info


class FormImageField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "file",
            }
        )
        return info


class FormURLField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "url",
            }
        )
        return info


class FormBooleanField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "boolean",
            }
        )
        return info


class FormNullBooleanField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "boolean",
                "required": False,
            }
        )
        return info


class FormDurationField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "example": "123 12:34:56.123",
            }
        )
        return info


class FormUUIDField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "uuid",
                "example": "7e13c2e7-b7ce-4d4d-9087-5003477121b0",
            }
        )
        return info


class FormIntegerField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "integer",
                "format": "int32",
            }
        )
        return info


class FormCharField(FormField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
            }
        )
        return info


class ModelField(SchemaField):
    def get_field_info(self, field):
        help_text = field.help_text and gettext(field.help_text) or ""
        info = super().get_field_info(field)
        info.update(
            {
                "required": not (field.null or field.blank),
                "verbose_name": gettext(field.verbose_name),
            }
        )
        if help_text:
            info["help_text"] = help_text
        return info


class ModelCharField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "maxLength": field.max_length,
            }
        )
        return info


class ModelTextField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "text",
                "maxLength": 1024 * 64,
            }
        )
        return info


class ModelInteger32Field(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "integer",
                "format": "int32",
            }
        )
        return info


class ModelInteger64Field(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "integer",
                "format": "int64",
            }
        )
        return info


class ModelBooleanField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "boolean",
            }
        )
        return info


class ModelDateTimeField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update({"type": "string", "format": "date-time"})
        return info


class ModelDateField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update({"type": "string", "format": "date"})
        return info


class ModelUUIDField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "uuid",
            }
        )
        return info


class ModelEmailField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "email",
            }
        )
        return info


class ModelURLField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "url",
                "example": "http://your.server.host/your/service/path",
            }
        )
        return info


class ModelIPAddressField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update({"type": "string", "format": "ipv4", "example": "192.168.1.1"})
        return info


class ModelGenericIPAddressField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update({"type": "string", "format": "ip", "example": "192.168.1.1"})
        return info


class ModelCommaSeparatedIntegerField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "CommaSeparatedIntegers",
                "example": "123,456,789",
            }
        )
        return info


class ModelDecimalField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "number",
                "example": 12.345,
            }
        )
        return info


class ModelDurationField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "string",
                "format": "DurationField",
                "example": "10 days 10:32:32.1234",
            }
        )
        return info


class ModelImageField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "file",
                "description": "Image Field",
            }
        )
        return info


class ModelFileField(ModelField):
    def get_field_info(self, field):
        info = super().get_field_info(field)
        info.update(
            {
                "type": "file",
            }
        )
        return info


class ModelForeignKey(ModelField):
    def get_field_info(self, field):
        related_model = field.related_model
        related_model_name = f"{related_model.__module__}.{related_model.__name__}"
        info = super().get_field_info(field)
        info.update(
            {
                "$ref": "#/components/schemas/" + related_model_name,
            }
        )
        return info


SCHEMA_FIELDS = collections.OrderedDict()


def register_schema_field(type, klass, extra=None):
    extra = extra or {}
    if isinstance(type, str):
        type = import_from_string(type)
    if type:
        SCHEMA_FIELDS[type] = (klass, extra)


register_schema_field("django.forms.fields.UUIDField", FormUUIDField())
register_schema_field(
    "django.forms.fields.GenericIPAddressField", FormGenericIPAddressField()
)
register_schema_field("django.forms.fields.NullBooleanField", FormNullBooleanField())
register_schema_field("django.forms.fields.BooleanField", FormBooleanField())
register_schema_field("django.forms.fields.URLField", FormURLField())
register_schema_field("django.forms.fields.ImageField", FormImageField())
register_schema_field("django.forms.fields.FileField", FormFileField())
register_schema_field("django.forms.fields.EmailField", FormEmailField())
register_schema_field("django.forms.fields.RegexField", FormRegexField())
register_schema_field("django.forms.fields.DurationField", FormDurationField())
register_schema_field("django.forms.fields.DateTimeField", FormDateTimeField())
register_schema_field("django.forms.fields.DateField", FormDateField())
register_schema_field("django.forms.fields.CharField", FormCharField())
register_schema_field("django.forms.fields.IntegerField", FormIntegerField())
register_schema_field("django.forms.fields.DecimalField", FormDecimalField())
register_schema_field("django.forms.fields.FloatField", FormFloatField())

register_schema_field("models.db.models.ImageField", ModelImageField())
register_schema_field("django.db.models.ForeignKey", ModelForeignKey())
register_schema_field("django.db.models.EmailField", ModelEmailField())
register_schema_field("django.db.models.URLField", ModelURLField())
register_schema_field("django.db.models.IPAddressField", ModelIPAddressField())
register_schema_field(
    "django.db.models.GenericIPAddressField", ModelGenericIPAddressField()
)
register_schema_field("django.db.models.UUIDField", ModelUUIDField())
register_schema_field(
    "django.db.models.CommaSeparatedIntegerField", ModelCommaSeparatedIntegerField()
)
register_schema_field("django.db.models.DurationField", ModelDurationField())
register_schema_field("django.db.models.DateTimeField", ModelDateTimeField())
register_schema_field("django.db.models.DateField", ModelDateField())
register_schema_field("django.db.models.FileField", ModelFileField())
register_schema_field("django.db.models.PositiveBigIntegerField", ModelInteger64Field())
register_schema_field(
    "django.db.models.PositiveSmallIntegerField", ModelInteger32Field()
)
register_schema_field("django.db.models.SmallAutoField", ModelInteger32Field())
register_schema_field("django.db.models.PositiveIntegerField", ModelInteger32Field())
register_schema_field("django.db.models.SlugField", ModelCharField())
register_schema_field("django.db.models.CharField", ModelCharField())
register_schema_field("django.db.models.TextField", ModelTextField())
register_schema_field("django.db.models.NullBooleanField", ModelBooleanField())
register_schema_field("django.db.models.BooleanField", ModelBooleanField())
register_schema_field("django.db.models.BigAutoField", ModelInteger64Field())
register_schema_field("django.db.models.BigIntegerField", ModelInteger64Field())
register_schema_field("django.db.models.AutoField", ModelInteger32Field())
register_schema_field("django.db.models.IntegerField", ModelInteger32Field())
register_schema_field("django.db.models.DecimalField", ModelDecimalField())

register_schema_field(
    "models.Model", ModelField(), {"type": "string", "format": "unknown"}
)
register_schema_field(
    "forms.Field", FormField(), {"type": "string", "format": "unknown"}
)


def get_field_type(field):
    real_field_type = type(field)
    logger.debug(
        f"django_apiview.swagger_ui.fields.get_field_type, field={field}, field_type={real_field_type}..."
    )

    DJANGO_APIVIEW_SWAGGER_FIELDS = getattr(
        global_settings, "DJANGO_APIVIEW_SWAGGER_FIELDS", {}
    )
    for field_type, (schema_field, extra) in DJANGO_APIVIEW_SWAGGER_FIELDS.items():
        field_type = import_from_string(field_type)
        schema_field = import_from_string(schema_field)()
        if isinstance(field, field_type):
            info = schema_field.get_field_info(field)
            info.update(extra)
            return info

    for field_type, (schema_field, extra) in SCHEMA_FIELDS.items():
        if isinstance(field, field_type):
            info = schema_field.get_field_info(field)
            info.update(extra)
            return info

    logger.warning(
        f"django_apiview.swagger_ui.fields.get_field_type, {field}'s type {real_field_type} is not registered..."
    )
    return {"type": "string", "format": "unknown"}
