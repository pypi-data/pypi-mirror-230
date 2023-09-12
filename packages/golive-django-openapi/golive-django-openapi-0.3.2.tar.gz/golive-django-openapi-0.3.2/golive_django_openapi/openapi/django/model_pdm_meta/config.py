# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseModelPDMConfig",
    "BaseSetterModelPDMConfig",
    "BaseGetterModelPDMConfig",
]

from typing import Dict

from .setter import *
from .getter import *


class BaseModelPDMConfigMeta(type):

    def __init__(cls, name, bases, attrs: Dict):
        super().__init__(name, bases, attrs)
        if not bases:
            return
        base = bases[-1]
        attrs_populated = {}
        for k in dir(base):
            if k.startswith("_"):
                continue
            attrs_populated[k] = getattr(base, k)
        for k, v in attrs.items():
            if isinstance(v, (tuple, list)):
                parent = getattr(base, k, None)
                assert isinstance(parent, tuple | list | None)
                if "include" in k.lower():
                    if parent is None:
                        attrs_populated[k] = list(v)
                    else:
                        # 列表的包含逻辑：即子类囊括的值必须是父类的子集
                        assert set(v).issubset(parent)
                        attrs_populated[k] = list(v)
                elif "exclude" in k.lower():
                    if parent is None:
                        attrs_populated[k] = list(set(v))
                    else:
                        # 列表的去除逻辑：即子类囊括的值是父类的值于子类配置的值的并集
                        attrs_populated[k] = list(set(list(parent) + list(v)))
        for k, v in attrs_populated.items():
            setattr(cls, k, v)


class BaseModelPDMConfig(metaclass=BaseModelPDMConfigMeta):

    _model_pdm_meta = None


class BaseSetterModelPDMConfig(BaseModelPDMConfig):
    """用于setter的config"""

    _model_pdm_meta = ModelPDMMetaSetter


class BaseGetterModelPDMConfig(BaseModelPDMConfig):
    """用于setter的config"""

    _model_pdm_meta = ModelPDMMetaGetter
