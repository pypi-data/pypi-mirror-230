# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "PropMeta",
    "prop",
    "PropType",
]

from typing import Callable, Any

from pydantic import BaseModel, Extra, PrivateAttr

from golive_django_openapi.utils.status_machine import *


class PropMeta(BaseModel):
    """装饰于prop方法上的元信息"""

    # prop名
    _name: str = PrivateAttr()

    # prop的django model方法
    _method: Callable = PrivateAttr()

    # 校验
    _validator: Any = PrivateAttr()

    class Config:
        extra = Extra.forbid


def prop(*, name: str = None):
    """标记一个实例方法为一个prop"""

    def outer(func):
        m = func.prop_meta = PropMeta()
        if name:
            m._name = name
        return func

    return outer


class PropType(StatusMachine):
    """prop类型"""

    getter = SMV("获取")
    setter = SMV("设置")
