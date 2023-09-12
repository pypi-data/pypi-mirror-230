# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseModelPDM",
    "BaseModelPDMGetter",
    "BaseModelPDMSetter",
]

import typing

from pydantic import PrivateAttr, ValidationError

from golive_django_openapi.openapi.models.base import *


class BaseModelPDM(pdm):

    # 用于存放meta实例
    _meta: typing.Any = PrivateAttr()


class BaseModelPDMGetter(BaseModelPDM):
    """用于getter的model pdm"""

    @classmethod
    def from_record(cls, record) -> pdm:
        """从django model记录读取值"""
        django_model = cls._meta._django_model
        assert isinstance(record, django_model), f"{record} is not an instance of {django_model}"
        d = {}
        for k, prop_meta in cls._meta._props.items():
            d[k] = prop_meta._method(record)
        for k in cls._meta._columns.keys():
            d[k] = getattr(record, k, None)
        return cls(**d)

    @classmethod
    def from_pdm_inst(cls, pdm_inst) -> pdm:
        """从其他pdm实例读取"""
        return cls.from_dict(pdm_inst.dict())

    @classmethod
    def from_dict(cls, d) -> pdm:
        """从字典读取值"""
        assert isinstance(d, dict), f"{d} is not an instance of dict"
        return cls(**d)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value) -> pdm:
        if isinstance(value, cls._meta._django_model):
            return cls.from_record(value)
        elif isinstance(value, cls):
            return value
        # elif isinstance(value, pdm):
        #     return cls.from_pdm_inst(value)
        elif isinstance(value, dict):
            return cls.from_dict(value)
        else:
            raise ValidationError(f"bad input value type: {type(value)=}", model=cls)


class BaseModelPDMSetter(BaseModelPDM):
    """用于setter的model pdm"""

    def _gen_keys_to_exclude(self, exclude):
        """
        判断在写入record的时候需要跳过的key
        :param exclude:
        :return: 需要跳过的key元组
        """
        if exclude is None:
            return []
        elif isinstance(exclude, (tuple, list)):
            return [i for i in exclude if i]
        elif isinstance(exclude, dict):
            return [k for k, v in exclude.items() if v and k]
        else:
            assert 0, f"failed when executing to_record with exclusion: {exclude=}"

    def to_record(self, record, exclude: dict | tuple | None = None):
        """
        :param record:
        :param exclude: 需要跳过的字段，如果是字典形式，则仅value为True的视为需要囊括
        :return:
        """
        exclude = self._gen_keys_to_exclude(exclude)
        django_model = self._meta._django_model
        assert isinstance(record, django_model), f"{record} is not an instance of {django_model}"
        for k in self._meta._columns.keys():
            if k in exclude:
                continue
            if self.incoming_has(k):
                setattr(record, k, getattr(self, k))
        for k, prop_meta in self._meta._props.items():
            if k in exclude:
                continue
            if self.incoming_has(k):
                prop_meta._method(record, getattr(self, k))
