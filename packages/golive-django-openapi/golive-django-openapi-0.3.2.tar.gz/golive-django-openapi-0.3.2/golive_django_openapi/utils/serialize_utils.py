# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "DefaultJsonSerializer",
]

from decimal import Decimal
from enum import Enum

from .dt_utils import *


class DefaultJsonSerializer:

    @classmethod
    def serialize(cls, v):
        if isinstance(v, (int, float, str)):
            return v
        elif isinstance(v, (list, tuple, set)):
            ret = []
            for i in v:
                ret.append(cls.serialize(i))
            return ret
        elif isinstance(v, dict):
            ret = {}
            for k, value in v.items():
                ret[k] = cls.serialize(value)
            return ret
        elif v is None:
            return v
        elif isinstance(v, Decimal):
            return float(v)
        elif isinstance(v, datetime):
            return dt_to_str(v)
        elif isinstance(v, date):
            return d_to_str(v)
        elif isinstance(v, time):
            return t_to_str(v)
        elif isinstance(v, Enum):
            return str(v)
        else:
            assert 0, f"{v=} is not json serializable !"
