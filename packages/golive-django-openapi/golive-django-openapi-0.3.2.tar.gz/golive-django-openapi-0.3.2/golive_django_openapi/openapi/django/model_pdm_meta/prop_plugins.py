# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BasePropPlugin",
    "ColumnShortPropPlugin",
    "ColumnSMVPropPlugin",
]

from pydantic import Extra

from django.db.models import Model
from django.db.models.fields import CharField

from golive_django_openapi.utils.cls_utils import *
from golive_django_openapi.utils.pydantic_utils import DictPDM
from golive_django_openapi.utils.status_machine import StatusMachine
from .prop import *


class BasePropPlugin(DictPDM):
    """prop插件"""

    class Config:
        extra = Extra.forbid

    def build(self, model):
        """构建prop"""
        raise NotImplementedError


class ColumnShortPropPlugin(BasePropPlugin):
    """用于自动生成字段缩略文本的prop插件"""

    # 需要配置缩略字段的字段名
    columns: set[str | tuple[str, int], ...]

    # 缩略字段后缀
    short_prop_postfix: str = "_short"

    # 缩略字段的description后缀
    short_prop_description_postfix: str = "(缩略字段)"

    # 默认的缩略保留长度
    default_short_length: int = 10

    # 是否忽略html中的图片
    ignore_images: bool = True

    def build(self, model: Model):
        """
        构建缩略字段
        请注意这里使用了base method model的get_short方法
        :param model:
        :return:
        """
        prepared_columns = {}
        for i in self.columns:
            if isinstance(i, str):
                prepared_columns[i] = self.default_short_length
            elif isinstance(i, tuple):
                prepared_columns[i[0]] = i[1]
            else:
                assert 0
        assert len(prepared_columns) == len(self.columns), \
            f"duplicated configured columns to build short prop in {model}.{self}"
        all_keys_of_the_model = dir(model)
        all_attname_field_dict = {f.attname: f for f in model._meta.fields}
        for c in prepared_columns:
            assert c in all_attname_field_dict.keys(), f"column '{c}' configured in {model}.{self} not existed."
            new_prop_name = f"{c}{self.short_prop_postfix}"
            assert new_prop_name not in all_keys_of_the_model, \
                f"short column prop to be created as '{new_prop_name}' already existed in {model}"
            target_column = all_attname_field_dict[c]
            new_prop_desc = f"{target_column.help_text}{self.short_prop_description_postfix}"
            method_hole = []
            template = f"""
@prop()
def {new_prop_name}(self) -> str | None:
    '''{new_prop_desc}'''
    return self.get_short(self.{c}, {prepared_columns[c]}, {self.ignore_images})
method_hole.append({new_prop_name})
"""
            exec(template, {"method_hole": method_hole, "prop": prop})
            the_prop = method_hole.pop()
            setattr(model, new_prop_name, the_prop)


class ColumnSMVPropPlugin(BasePropPlugin):
    """适用于django model中被标记值为status machine的字段，自动创建一个状态机对应当前值的一个详情，可包含额外信息"""

    # 状态机值详情字段的后缀
    smv_prop_postfix: str = "_object"

    def build(self, model):
        for field in model._meta.fields:
            # 请注意这里是判断状态机字段的关键条件
            if isinstance(field, CharField) and field.choices and safe_issubclass(field.choices, StatusMachine):
                new_prop_name = field.name + self.smv_prop_postfix
                status_machine = field.choices
                new_prop_desc = f"{status_machine.__doc__}(状态机字段值详情)"
                method_hole = []
                template = f"""
@prop()
def {new_prop_name}(self) -> dict | None:
    '''{new_prop_desc}'''
    return status_machine.ensure_get_to_dict(self.{field.name})
method_hole.append({new_prop_name})
"""
                exec(template, {
                    "method_hole": method_hole,
                    "prop": prop,
                    "status_machine": status_machine
                })
                the_prop = method_hole.pop()
                setattr(model, new_prop_name, the_prop)

