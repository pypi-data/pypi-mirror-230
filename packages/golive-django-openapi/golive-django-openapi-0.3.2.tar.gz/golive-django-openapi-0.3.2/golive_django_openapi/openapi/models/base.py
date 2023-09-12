# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "PydanticModel", "pdm",
    "BaseAPIReqPDM",
    "BaseAPIQueryPDM",
    "AtLeastOneQueryMixin",
    "MediaTypes",
    "BaseJsonRespPDM",
    "KeywordReqPDM",
    "JsonQueryModifyPDM",
]

import typing
from enum import StrEnum

from django.db.models import QuerySet, Q
from django.views import View
from pydantic import Extra, root_validator

from golive_django_openapi.utils.pydantic_utils import *
from ..openapi_gen import schema_meta
from golive_django_openapi.utils.logger_utils import *


logger = get_bound_logger(__name__)


class PydanticModel(DictPDM, JSONSerializablePDM):
    pass


pdm = PydanticModel


class MediaTypes(StrEnum):
    """常用media type"""

    # json
    application__json = "application/json"

    # 通用文件
    application__octet_stream = "application/octet-stream"

    # 纯文本
    text__plain = "text/plain"

    # 普通请求体key-value型
    application__x_www_form_urlencoded = "application/x-www-form-urlencoded"

    # 支持文件上传的请求体key-value型
    multipart__form_data = "multipart/form-data"


class BaseAPIReqPDM(pdm):
    """基础请求结构"""

    def before_resp(self, view_inst: View):
        """返回之前制作一些请求侧的数据"""
        pass


class BaseAPIQueryPDM(BaseAPIReqPDM):
    """
    用于接口查询的pdm，.dict方法默认去掉None的参数
    """

    def dict(
            self,
            *,
            exclude_unset: bool = False,
            exclude_none: bool = True,
            **kwargs
    ) -> typing.Dict[str, typing.Any]:
        r = super().dict(exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs)
        ret_dict = {k: v for k, v in r.items() if v is not None}
        logger.debug(f"query parameters: {ret_dict}")
        return ret_dict


class AtLeastOneQueryMixin(pdm):

    @root_validator(pre=True)
    def at_lease_one(cls, values):
        assert any(values), "at least one query parameter is required."
        return values


class BaseJsonRespPDM(pdm):
    """基础json返回结构"""

    content: typing.Any = None  # 这是接口返回的核心数据
    msg: str = schema_meta(PDMField(""), description="提示信息")
    login_entry: str | None = schema_meta(PDMField("/login"), description="重定向登录的跳转入口")

    class Config:
        extra = Extra.allow

    @classmethod
    def make_resp(cls, view_inst: View, d):
        """包装返回数据"""
        r = cls(
            content=d,
            msg=view_inst.resp_msg
        )
        return r


class KeywordReqPDM(pdm):
    """模糊查询"""

    keyword: str | None = schema_meta(PDMField(), description="模糊查询参数")

    def query_keyword(self, qs: QuerySet, *args) -> QuerySet:
        """
        查询sql的like语句，模糊匹配
        :param qs: queryset
        :param args: 需要查询的字段
        """
        if not args or not self.keyword:
            return qs
        to_query = Q()
        for s in args:
            to_query = to_query | Q(**{f"{s}__icontains": self.keyword})
        return qs.filter(to_query)

    def dict(
            self,
            *,
            exclude_unset: bool = False,
            **kwargs
    ) -> typing.Dict[str, typing.Any]:
        r = super().dict(exclude_unset=exclude_unset, **kwargs)
        r.pop("keyword", None)
        return r


class JsonQueryModifyPDM(pdm):
    """支持query-modify结构的json body"""

    query: typing.Any | None
    modify: typing.Any | None
