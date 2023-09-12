# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "DictPDM",
    "PDMField",
    "create_model_ex",
    "create_pdm",
    "field",
    "JSONSerializablePDM",
    "pop_root",
]

import os
import uuid
import types
from typing import Any, Type, Tuple, Optional

from pydantic import BaseModel, Field as PDMField
from pydantic.fields import FieldInfo
from pydantic.fields import Undefined
from pydantic.main import ModelMetaclass

from .serialize_utils import *
from .cls_utils import *
from .logger_utils import *


logger = get_bound_logger(__name__)


# 记录命名的pdm的名称
NAMED_PDM_NAMES = set()

# 未指定名称的子模块名的占位符
ANONYMOUS_SUB_MODEL_NAME_PLACEHOLDER = "AnonymousDictPDM"


def gen_anonymous_sub_model_name():
    return f"{ANONYMOUS_SUB_MODEL_NAME_PLACEHOLDER}_{uuid.uuid4().hex}"


def create_model_ex(base: BaseModel | Tuple[BaseModel, ...],
                    d: dict[str, Type | Tuple[Type, FieldInfo] | Tuple[Type, Any] | types.UnionType],
                    description: str = None,
                    **config):
    """
    字典方式定义子类
    :param base: 父类或者多个父类
    :param d: https://docs.pydantic.dev/usage/models/
              字典，三种形式可选。
              1)"key": (type, Field-Object)
              2)"key": (type, default-value)
              3)"key": type
    :param description: 新子类的__doc__
    :param config: https://docs.pydantic.dev/usage/model_config/
    :return:
    """
    assert isinstance(base, tuple) or safe_issubclass(base, BaseModel), f"bad {base=}"
    if safe_issubclass(base, BaseModel):
        base = (base,)
    parent_model_name = "*base"

    # 修正传入的构造字段
    kw = {}
    for k, v in d.items():
        assert isinstance(k, str), "pdm key should be string"
        if isinstance(v, tuple):
            assert len(v) == 2, "if you're going to use format like 'key: (type, Field-Object)', " \
                                "make sure the tuple contains exactly 2 items"
            if isinstance(v[1], FieldInfo):
                kw[k] = (v[0], v[1])
            else:
                kw[k] = (v[0], PDMField(v[1]))
        else:
            kw[k] = (v, Undefined)

    # 子类名
    is_anonymous: bool = False
    sub_model_name = config.get("title", None)
    if not sub_model_name:
        sub_model_name = gen_anonymous_sub_model_name()
        is_anonymous: bool = True

    # 用来装载产生的model
    created_model_hole = []

    # 用于在exec内设置参数
    key_values_to_set = {}

    # 准备model的字段
    fields = []
    for i, (k, v) in enumerate(kw.items()):
        t, f = v
        key_values_to_set[f"kw_{i}_t"] = t
        key_values_to_set[f"kw_{i}_f"] = f
        fields.append(f"    {k}: key_values_to_set['kw_{i}_t'] = key_values_to_set['kw_{i}_f']")
    if not fields:
        fields = ["    pass"]

    # 准备model的config字段
    configs = []
    for i, k in enumerate(config.keys()):
        v = config[k]
        key_values_to_set[f"config_{i}_v"] = v
        configs.append(f"        {k} = key_values_to_set['config_{i}_v']")
    if not configs:
        configs = ["        pass"]

    # 渲染模板
    template = f"""
class {sub_model_name}({parent_model_name}):
    '''{description if description else ""}'''

{os.linesep.join(fields)}

    class Config:
{os.linesep.join(configs)}

created_model_hole.append({sub_model_name})
"""
    exec(template, {
        "base": base,
        "key_values_to_set": key_values_to_set,
        "created_model_hole": created_model_hole
    })
    the_model = created_model_hole[0]

    if is_anonymous and sub_model_name in NAMED_PDM_NAMES:
        logger.warning(f"dynamically build a pdm with duplicated name '{sub_model_name}', consider it's a bug.")
    else:
        NAMED_PDM_NAMES.add(sub_model_name)

    return the_model


def pop_root(something_from_model_dict):
    """
    pydantic的BaseModel.dict在model配置__root__为非model的时候，.dict是无法输出__root__内的东西的
    因此需要手动判断并且弹出__root__的值
    :param something_from_model_dict:
    :return:
    """
    if something_from_model_dict and "__root__" in something_from_model_dict:
        return something_from_model_dict["__root__"]
    return something_from_model_dict


class AllOptionalPDMMeta(ModelMetaclass):
    """一个可配置生成全部字段为可选的元类"""

    # 配置开关位于Config内：是否开启全部字段可选
    # class Config:
    #     all_optional: bool = False

    def __new__(cls, name, bases, namespaces, **kwargs):
        if getattr(namespaces.get("Config", object), "all_optional", False):
            try:
                del namespaces["Config"].all_optional
            except:
                pass
            annotations = namespaces.get('__annotations__', {})
            for base in bases:
                annotations.update(base.__annotations__)
            for field in annotations:
                if not field.startswith('__'):
                    annotations[field] = Optional[annotations[field]]
            namespaces['__annotations__'] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class DictPDM(BaseModel, metaclass=AllOptionalPDMMeta):
    """
    一个允许以字典方式定义子类的pydantic.BaseModel
    PDM == 'PyDanticModel' 以区别于django.model
    """

    @classmethod
    def sub(cls, *args, **kwargs):
        return create_model_ex(cls, *args, **kwargs)

    def incoming_keys(self) -> set[str]:
        """查询实际传入的key"""
        return self._calculate_keys(None, None, exclude_unset=True)

    def incoming_has(self, key: str) -> bool:
        """判断是否实际传入该字段"""
        return key in self.incoming_keys()


create_pdm = DictPDM.sub
field = PDMField


class JSONSerializablePDM(BaseModel):
    """一个支持序列化为json的pdm"""

    JSON_SERIALIZER = DefaultJsonSerializer

    def json_dict(self):
        """转换为可以直接json.dumps的字典"""
        return self.JSON_SERIALIZER.serialize(self.dict())
