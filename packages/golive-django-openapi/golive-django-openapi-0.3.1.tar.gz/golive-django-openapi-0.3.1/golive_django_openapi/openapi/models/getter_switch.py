# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "getter_switch_annotate",
]

from typing import Type, Union, Any

from pydantic import PrivateAttr

from golive_django_openapi.utils.pydantic_utils import *
from .base import *
from ..django.model import *
from .shortcuts import *


class GetterSwitchReqMixin:

    # TODO 请注意本类是mixin，脱离BaseAPIQueryPDM是无法使用的

    _all_getters = PrivateAttr()

    @property
    def getter(self):
        for g in self._all_getters:
            if g._meta.switch_flag == self.to_dict:
                return g

    def dict(
            self,
            *,
            exclude_unset: bool = False,
            exclude_none: bool = True,
            **kwargs
    ) -> dict[str, Any]:
        r = super().dict(exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs)
        r.pop("to_dict", None)
        return r


def getter_switch_annotate(querystring: Type[pdm], model: Type[ModelPDMMixin]):
    """
    指定一个model，然后查找model可用的getter model pdm，生成可切换的返回结构
    """

    from ..base import schema_meta, annotate

    def outer(func):

        items = {
            # "_all_getters": PrivateAttr(model.ALL_GETTERS)
        }
        if model.GETTER_SWITCH_ALLOW_DEFAULT:
            items["to_dict"] = schema_meta((model.ALL_GETTERS_ENUM | None, PDMField("", alias="_to_dict")), description="返回数据结构指定")
        else:
            items["to_dict"] = schema_meta((model.ALL_GETTERS_ENUM, PDMField(alias="_to_dict")), description="返回数据结构指定")

        qs = create_model_ex(
            (GetterSwitchReqMixin, querystring),
            items,
        )

        qs._all_getters = model.ALL_GETTERS

        new_ret = pagination_list_resp(Union[*model.ALL_GETTERS])
        return annotate(querystring=qs, ret=new_ret)(func)
    return outer
