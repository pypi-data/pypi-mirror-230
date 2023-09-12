# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "build_query",
    "qm",
    "resp",
    "list_resp",
    "pagination_list_resp",
]

from .pagination import *
from .base import *
from ..openapi_gen import schema_meta
from golive_django_openapi.utils import pydantic_utils


def build_query(d: dict, *, paginate: bool = False, keyword: bool = False, at_least_one: bool = False):
    """
    快捷方法:构造查询条件的pdm，提供模糊关键字和分页信息的配置
    :param d: 其他参数，必须是字典
    :param paginate: 是否支持分页
    :param keyword: 是否支持模糊查询
    :param at_least_one: 是否至少要求传入一个查询参数
    :return:
    """
    assert isinstance(d, dict), "create_query only support dict to define pdm, " \
                                f"if you're using pdm, " \
                                f"please make sub classes from {BaseAPIQueryPDM}."
    bases = []
    if keyword:
        bases.append(KeywordReqPDM)
    if paginate:
        bases.append(PaginationReqPDM)
    if not bases:
        bases.append(BaseAPIQueryPDM)
    if at_least_one:
        bases.append(AtLeastOneQueryMixin)
    r = pydantic_utils.create_model_ex(
        tuple(bases),
        d=d,
        description=pydantic_utils.gen_anonymous_sub_model_name()
    )
    return r


def qm(query=None, modify=None):
    q = query
    m = modify
    r = {}
    if q is not None:
        r["query"] = schema_meta(q, description="查询参数")
    if m is not None:
        r["modify"] = schema_meta(m, description="修改参数")
    return JsonQueryModifyPDM.sub(r)


def resp(m):
    """
    快捷方法:构造通用返回结构的pdm
    :param m:
    :return:
    """
    return BaseJsonRespPDM.sub({"content": m | None})


def list_resp(m):
    """
    快捷方法:构造通用列表返回结构的pdm
    :param m:
    :return:
    """
    return BaseJsonRespPDM.sub({"content": list[m] | None})


def pagination_list_resp(m):
    """
    快捷方法:构造带分页的列表返回结构pdm
    :param m:
    :return:
    """
    return PaginationReqJsonRespPDM.sub({"content": list[m] | None})
