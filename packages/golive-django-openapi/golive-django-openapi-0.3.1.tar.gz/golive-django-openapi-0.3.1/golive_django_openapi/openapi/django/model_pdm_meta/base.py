# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ConfigUnset",
    "BaseModelPDMMeta",
]


import re
import typing
from typing import Type

from pydantic import Extra, PrivateAttr, ValidationError, Field
from django.db.models import Model, Field as django_field

from golive_django_openapi.utils.cls_utils import *
from golive_django_openapi.utils.logger_utils import *
from ...models.base import pdm
from .convert import *
from .prop import *
from ..model_pdm import BaseModelPDM


logger = get_bound_logger(__name__)


class ConfigUnset:
    """标记modelPDMConfig的参数未配置"""

    pass


class BaseModelPDMMeta(pdm):
    """django model输出pdm的配置"""

    # 使用哪个pdm的基类，一般不需要动
    base_pdm: Type[pdm] = Field(BaseModelPDM)
    # 表字段仅包含
    column_include: tuple[typing.Union[str, django_field], ...] = Field(ConfigUnset)
    # 表字段去除
    column_exclude: tuple[typing.Union[str, django_field], ...] = Field(ConfigUnset)
    # prop仅包含
    prop_include: tuple[str, ...] = Field(ConfigUnset)
    # prop去除
    prop_exclude: tuple[str, ...] = Field(ConfigUnset)
    # 子类插槽字典，
    # 在用BASE_PDM为父类，依照先column再prop的方式创建完pdm之后的pdm，再拼接下述参数生成子类
    # 这个字段用于部分参数校验的修正
    sub_pdm_slot_dict: dict[str, typing.Any] = Field(ConfigUnset)
    # 强制全部字段可选
    all_optional: bool = Field(False)
    # 用于getter switch的标志，注意本标志在一个django model的全部modelPDM中不允许重复
    switch_flag: str = Field("")

    # 下面是用户不应该手动配置的参数
    # 所属的django model
    _django_model = PrivateAttr()
    # 实际使用的表字段:  类型定义
    _columns: dict[str, typing.Any] = PrivateAttr()
    # 实际使用的prop名: prop-meta实例
    _props: dict[str: PropMeta] = PrivateAttr()
    # 最终可用的键
    _keys: set[str] = PrivateAttr()
    # 生成的pdm
    _pdm: Type[pdm] = PrivateAttr()

    # prop的regex
    _prop_method_regex: str = PrivateAttr(r"^(.+?)$")

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def prepare_columns(self, model):
        """.column_*的内容在配置的时候是str，这里转为django_field"""
        def _inner(target_name: str):
            r = set()
            target = getattr(self, target_name)
            if target is ConfigUnset:
                return
            for c in target:
                assert isinstance(c, (str, django_field)), \
                    f"pass django field name or field to {target_name}, not {type(c)=}"
                if isinstance(c, str):
                    try:
                        c = getattr(getattr(model, c), "field")
                    except (NameError, AttributeError) as e:
                        assert 0, f"column name {c} not exists in {model}: {e}"
                r.add(c)
            setattr(self, target_name, tuple(r))

        _inner("column_include")
        _inner("column_exclude")

    def prepare_props(self, model):
        def _inner(target_name: str):
            r = set()
            target = getattr(self, target_name)
            if target is ConfigUnset:
                return

        _inner("prop_include")
        _inner("prop_exclude")

    @staticmethod
    def raise_mutually_exclusive(a, b):
        """互斥的两个字段的值不能有交集"""
        if a is not ConfigUnset and b is not ConfigUnset:
            intersection = set(a).intersection(b)
            if intersection:
                raise ValueError(f"{a} and {b} are mutually exclusive and can't have intersection: {intersection}")

    def column_need(self, c):
        """
        :param c: django model field
        :return:
        """
        if self.column_include is not ConfigUnset:
            return c in self.column_include
        return any([
            self.column_exclude is not ConfigUnset and c not in self.column_exclude,
            self.column_include is ConfigUnset and self.column_exclude is ConfigUnset
        ])

    def prop_need(self, c: str):
        """
        :param c: prop的实际名称
        :return:
        """
        if self.prop_include is not ConfigUnset:
            return c in self.prop_include
        return any([
            self.prop_exclude is not ConfigUnset and c not in self.prop_exclude,
            self.prop_include is ConfigUnset and self.prop_exclude is ConfigUnset
        ])

    def get_columns(self, model):
        """
        初始化._columns内容
        :param model:
        :return:
        """
        self.raise_mutually_exclusive(self.column_include, self.column_exclude)
        assert safe_issubclass(model, Model)
        r = {}
        for field in model._meta.fields:
            if not self.column_need(field):
                continue
            t, field_info = get_field_validator(field)
            r[field.attname] = (t, field_info)
        self._columns = r

    def get_prop_validator(self, prop):
        """找到prop的类型"""
        raise NotImplementedError

    def get_props(self, model):
        """
        初始化._props内容
        :param model:
        :return:
        """
        self.raise_mutually_exclusive(self.prop_include, self.prop_exclude)
        assert safe_issubclass(model, Model)
        r = {}
        for prop_method_name in dir(model):
            try:
                suppose_prop_name = re.compile(self._prop_method_regex).findall(prop_method_name)[0]
                if not suppose_prop_name:
                    assert 0
            except:
                continue
            v = getattr(model, prop_method_name)  # v is the method
            meta_of_v = getattr(v, "prop_meta", None)
            if not meta_of_v:
                continue  # without meta, a method of the model will never become a prop
            assert callable(v), f"bad prop {prop_method_name=} in {model}, callable required."
            if not getattr(meta_of_v, "_name", None):
                meta_of_v._name = suppose_prop_name
            if not self.prop_need(meta_of_v._name):
                continue
            meta_of_v._validator = self.get_prop_validator(v)
            meta_of_v._method = v
            r[meta_of_v._name] = meta_of_v
        self._props = r

    def get_props_type_dict(self) -> dict[str, typing.Any]:
        """返回._props内的prop的类型字典"""
        r = {}
        for prop_name, prop_meta in self._props.items():
            r[prop_name] = prop_meta._validator
        return r

    def check_integrity(self, model):
        """检查表字段和prop是否有重复，有重复的必须明确去留"""
        intersection = set(self._props.keys()).intersection(self._columns.keys())
        if intersection:
            raise ValueError(f"duplication in columns and props {intersection} at {model}")
        self._keys = set(list(self._props.keys()) + list(self._columns.keys()))

    @classmethod
    def get_pdm_model_name(cls, model, *args):
        """返回一个给新生成的pdm用的名字"""
        return "__".join([model.__module__, model.__name__, *args]).replace(".", "_") + "__PDM"

    @classmethod
    def plugin_names(cls) -> set[str]:
        r = [p.flag for p in cls.plugins]
        assert len(r) == len(set(r)), f"duplicated plugins in {cls}: {r}"
        return set(r)

    @classmethod
    def init_config(cls, model, c: Type) -> Type[BaseModelPDM]:
        """装载配置"""
        d = {}
        if c:
            d = {k: getattr(c, k) for k in dir(c) if not k.startswith("_") and k not in ("mro",)}
            assert isinstance(d, dict), f"misconfigured for {model} -> {c=}"
        try:
            meta = cls(**d)
        except ValidationError as e:
            assert 0, f"bad configuration argument for {model} in {c}: {str(e)}"
        meta.prepare_columns(model)
        meta.prepare_props(model)
        meta.get_columns(model)
        meta.get_props(model)
        meta.check_integrity(model)
        slot = {}
        if meta.sub_pdm_slot_dict is not ConfigUnset:
            if not set(meta.sub_pdm_slot_dict.keys()).issubset(meta._keys):
                diff = set(meta.sub_pdm_slot_dict.keys()).difference(meta._keys)
                raise ValueError(f"{meta.sub_pdm_slot_dict} contains keys "
                                 f"which are not existed in columns or props: {diff}")
            slot = meta.sub_pdm_slot_dict
        meta._django_model = model
        intermediate_model_pdm = meta.base_pdm.sub({
            **meta._columns,
            **meta.get_props_type_dict(),
            **slot
        }, title=cls.get_pdm_model_name(model, c.__name__), all_optional=meta.all_optional)
        model_pdm = intermediate_model_pdm
        model_pdm._meta = meta
        return model_pdm
