# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "PaginationReqPDM",
    "PaginationReqJsonRespPaginationInfoPDM",
    "PaginationReqJsonRespPDM",
]

import typing

from pydantic import Field, PrivateAttr
from django.db.models import QuerySet
from django.db.models.query import RawQuerySet
from django.views import View

from ..openapi_gen import schema_meta
from ..exceptions import *
from .base import *


class PaginationReqJsonRespPaginationInfoPDM(pdm):
    """默认分页查询对应的json返回结构的分页信息"""

    page: int | None = schema_meta(Field(), description="当前页")
    per_page: int | None = schema_meta(Field(), description="每页数据量")
    total: int | None = schema_meta(Field(), description="总数据量")
    pages: int | None = schema_meta(Field(), description="总页数")


class PaginationReqPDM(BaseAPIQueryPDM):
    """默认分页的查询"""

    page: int = schema_meta(Field(1), "当前页")
    per_page: int = schema_meta(Field(20), "每页数")
    _pagination_info: PaginationReqJsonRespPaginationInfoPDM | None = PrivateAttr()

    def dict(
            self,
            *,
            exclude_unset: bool = False,
            **kwargs
    ) -> typing.Dict[str, typing.Any]:
        r = super().dict(exclude_unset=exclude_unset, **kwargs)
        r.pop("page")
        r.pop("per_page")
        return r

    def paginate(self, query: typing.Iterable | QuerySet | RawQuerySet):
        """
        分页
        :param query: 被分页的可迭代对象
        :return:
        """
        query_iterable: bool = isinstance(query, typing.Iterable)  # 判断输出的对象是否可迭代
        page = self.page
        per_page = self.per_page
        if isinstance(query, (QuerySet, RawQuerySet)) or query_iterable:
            s = (page - 1) * per_page
            items = list(query[s: s + per_page])  # 因为输出的pdm指定了必须返回列表类型
        else:
            raise OpenAPIException(f"{query=} isn't iterable")
        if page == 1 and len(items) < per_page:
            total = len(items)
        elif isinstance(query, QuerySet):
            total = query.count()
        elif query_iterable:
            total = len(query)
        else:
            assert 0
        pages = total // per_page
        if total % per_page > 0:
            pages += 1
        # 存放分页信息
        self._pagination_info = PaginationReqJsonRespPaginationInfoPDM(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages
        )
        return items

    def before_resp(self, view_inst: View):
        if not self._pagination_info:
            print("it seems no pagination is set.")
        view_inst._pagination_info = self._pagination_info


class PaginationReqJsonRespPDM(BaseJsonRespPDM):
    """默认分页查询对应的json返回结构"""

    pagination: PaginationReqJsonRespPaginationInfoPDM | None

    @classmethod
    def make_resp(cls, view_inst: View, d):
        """返回带分页信息的数据结构"""
        r = super().make_resp(view_inst, d)
        r.pagination = view_inst._pagination_info
        # if r and "__root__" in r:
        #     r = r["__root__"]
        return r
