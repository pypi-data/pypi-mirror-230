# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "get_field_validator",
]

from typing import Tuple, Any
from datetime import datetime, date, time

from django.db.models import fields
from django.db.models.fields.json import JSONField
from django.db.models.fields.related import ForeignKey
from pydantic.fields import FieldInfo
from pydantic import Field as pdm_field
from django.db.models.fields import NOT_PROVIDED

from ...openapi_gen import schema_meta
from golive_django_openapi.utils.cls_utils import *
from golive_django_openapi.utils.status_machine import StatusMachine


def get_field_validator(field: fields.Field) -> Tuple[Any, FieldInfo]:
    """
    返回django field对应的校验参数信息
    :return: 校验(也可能带默认值), schema_meta
    """

    from ..fields import PDMJsonField

    validator = Any
    pdm_f = pdm_field()

    def set_nullable(t, f):
        return (t | None) if f.null else t

    def set_comment(f):
        if getattr(f, "help_text", None):
            schema_meta(pdm_f, description=f.help_text)

    def set_default(f):
        if f.default is not NOT_PROVIDED:
            if callable(f.default):
                pdm_f.default = f.default()
            else:
                pdm_f.default = f.default

    if isinstance(field, fields.IntegerField):
        validator = set_nullable(int, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.BooleanField):
        validator = set_nullable(bool, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.CharField):
        if field.choices and safe_issubclass(field.choices, StatusMachine):
            # 允许char类型的字段支持status_machine
            validator = set_nullable(field.choices, field)
        else:
            validator = set_nullable(str, field)
            set_comment(field)
        set_default(field)

    elif isinstance(field, fields.TextField):
        validator = set_nullable(str, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.DateTimeField):
        from golive_django_openapi.openapi.pdm_fields import Datetime
        validator = set_nullable(Datetime, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.DateField):
        validator = set_nullable(date, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.TimeField):
        validator = set_nullable(time, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.BinaryField):
        validator = set_nullable(bytes, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, fields.FloatField):
        validator = set_nullable(float, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, PDMJsonField):
        validator = set_nullable(field.pdm | None, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, JSONField):
        validator = set_nullable(Any | None, field)
        set_comment(field)
        set_default(field)

    elif isinstance(field, ForeignKey):
        foreign_key_target_field = field.target_field
        if isinstance(foreign_key_target_field, (fields.IntegerField, fields.BigAutoField)):
            validator = set_nullable(int, field)
        elif isinstance(foreign_key_target_field, fields.CharField):
            validator = set_nullable(str, field)
        else:
            raise NotImplementedError(f"unsupported django model field: {field} (foreign key to {foreign_key_target_field})")
        set_comment(field)
        set_default(field)

    else:
        raise NotImplementedError(f"unsupported django model field: {field}")
    return validator, pdm_f
