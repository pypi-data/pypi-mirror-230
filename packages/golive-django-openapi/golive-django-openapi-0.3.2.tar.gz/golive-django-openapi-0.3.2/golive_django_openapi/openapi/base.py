# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseOpenAPIHandlerType",
    "BaseOpenAPIHandler",
    "annotate",
    "req_meta",
    "resp_meta",
    "schema_meta",
    "pdm_field",
]

import os
import re
import json
import copy
import types
import typing
import traceback

from django.views import View
from django.urls import path as as_django_path
from django.http.response import HttpResponse
from django.db import IntegrityError
from django.db.models import QuerySet
from pydantic.error_wrappers import ValidationError
from pydantic import Field as pdm_field

from golive_django_openapi.utils.self_collecting_model import *
from golive_django_openapi.utils.logger_utils import *
from golive_django_openapi.utils.cls_utils import *
from golive_django_openapi.utils.pydantic_utils import *
from .exceptions import *
from .openapi_gen import *
from .models import base as pdm
from .method_processor import BaseOpenAPIMethodProcessor


class BaseOpenAPIHandlerType(SelfCollectingModelMeta, LoggerMixin):
    """openapi元类"""

    def __init__(cls, name, bases, attrs):

        # 当前api的url后缀
        cls.URL_POSTFIX: str = attrs.get("URL_POSTFIX", "")

        super().__init__(name, bases, attrs)

        # django urlpatterns
        assert getattr(cls, "urlpatterns", None) is not None
        assert getattr(cls, "COLLECTED", None) is not None

        # api模块的根module
        assert getattr(cls, "MODULE_PREFIX")

        # json序列化缺省参数
        assert getattr(cls, "RESPONSE_JSON_ENSURE_ASCII", None) is not None

        # json序列化缺省参数
        assert getattr(cls, "RESPONSE_JSON_INDENT", None) is not None

        # 执行一下请求方法预处理器（如果有）
        for hmn in cls.http_method_names:
            method_or_processor = getattr(cls, hmn, None)
            if isinstance(method_or_processor, BaseOpenAPIMethodProcessor):
                setattr(cls, hmn, method_or_processor.build(hmn))


class RequestMethodValidator(pdm.pdm):
    """请求类型方法与对应的校验器结构"""

    # 方法名
    method_name: str
    # 方法引用
    method: typing.Callable
    # url查询字串
    querystring: typing.Type[pdm.pdm] | None
    # 请求头
    headers: typing.Type[pdm.pdm] | None
    # body数据json
    body: typing.Type[pdm.pdm] | None
    # 返回数据结构
    ret: typing.Type[pdm.BaseJsonRespPDM | HttpResponse] = pdm.BaseJsonRespPDM

    def all_models(self) -> set[typing.Any]:
        return {i for i in [self.querystring, self.headers, self.body, self.ret] if i}


def annotate(**kwargs):

    def outer(func):
        if "ret" in kwargs:
            kwargs["return"] = kwargs.pop("ret")
        func.__annotations__.update(kwargs)
        return func
    return outer


class RequestMethodMeta(pdm.pdm):
    """请求的元信息"""

    # 请求体数据类型
    body_media_type: str = pdm.MediaTypes.application__json.value

    # 请求体描述
    body_description: str = ""


def req_meta(**kwargs):
    """
    用于标记请求的缺省信息
    本装饰器支持装饰在方法上或者请求类上
    :param kwargs: 传入RequestMethodMeta+OpenAPIOperationMeta的值
    :return:
    """
    from golive_django_openapi.openapi.openapi_gen import OpenAPIOperationMeta

    def cls_outer(cls_or_func):

        def func_outer(func):
            func.req_meta = RequestMethodMeta(**kwargs)
            func.operation_meta = OpenAPIOperationMeta(**kwargs)
            return func

        if safe_issubclass(cls_or_func, BaseOpenAPIHandler):
            for hmn in cls_or_func.http_method_names:
                method = getattr(cls_or_func, hmn, None)
                if not method:
                    continue
                if getattr(method, "req_meta", None) or getattr(method, "operation_meta", None):
                    continue  # 保证方法上的装饰器优先级高于类上的
                func_outer(method)
            return cls_or_func
        elif isinstance(cls_or_func, types.FunctionType):
            return func_outer(cls_or_func)
        else:
            assert 0, f"you may decorate req_meta to something that can't set request metas: {cls_or_func}"

    return cls_outer


class ResponseMethodMeta(pdm.pdm):
    """正常返回的元信息"""

    # 状态码
    status_code: int = 200
    # 状态码解释
    status_code_description: str = "success"
    # 类型
    content_type: str = pdm.MediaTypes.application__json.value


def resp_meta(**kwargs):
    """
    用于标记正常返回的缺省信息
    :param kwargs: 传入ResponseMethodMeta的值
    :return:
    """
    def outer(func):
        func.resp_meta = ResponseMethodMeta(**kwargs)
        return func
    return outer


class BaseOpenAPIHandler(View, SelfCollectingModel):
    """基础openapi入口"""

    def collecting(cls, model):
        if cls is BaseOpenAPIHandler:
            return
        if model.URL_POSTFIX:
            assert model.URL_POSTFIX.strip()[0] != "/"
        module_prefix = [i for i in cls.MODULE_PREFIX.split(".") if i]
        split_path = [
            i for i in model.__module__.split(".") if i
        ]
        if {"__init__"}.intersection(split_path):
            return
        split_path = split_path[len(module_prefix):]
        if altered_pf := model.URL_POSTFIX.removesuffix("/"):
            split_path.append(altered_pf)
        route = str("/".join(split_path))
        if cls.COLLECTED_DICT.get(route, None) is not None and\
                cls.COLLECTED_DICT[route] is not model:
            assert 0, f"duplicated {route=} with {cls.COLLECTED_DICT[route]} and {model}"
        cls.COLLECTED_DICT[route] = model
        cls.COLLECTED.append(
            (route, model)
        )
        cls.urlpatterns.append(
            as_django_path(route, model.as_view())
        )

    @classmethod
    def resolve_requirement(cls):
        return

    NEED_COLLECT = False

    COLLECTED = []

    COLLECTED_DICT: dict[str, typing.Any] = dict()

    # 配置openapi入口
    # TODO 在子类也即api入口处配置该项，以便产生openapi文档
    #      请注意这里配置paths和components会被忽略
    #      使用.construct方法构建一个暂时不校验的openapi对象，文档输出的时候会自动补全接口信息并校验
    OPENAPI_ENTRY = openapi_models.OpenAPI.construct(
        openapi="3.0.0",
        info=openapi_models.Info(
            title="OpenAPI接口文档",
            version="0.0.1"
        ),
    )

    # 默认可用的请求方法
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]

    # 输出的openapi地址
    OPENAPI_PATH = "openapi.json"

    # 输出的openapi的完整可访问地址
    OPENAPI_ABSOLUTE_PATH = None

    # REDOC文档
    OPENAPI_REDOC_PREFIX = "redoc"

    # json序列化缺省参数
    RESPONSE_JSON_ENSURE_ASCII = False

    # json序列化缺省参数
    RESPONSE_JSON_INDENT = False

    @classmethod
    def gen_openapi(cls):
        """添加一个openapi文档输出接口"""

        class OpenAPIHandler(cls):
            NEED_COLLECT = False

            def get(self) -> HttpResponse:
                from golive_django_openapi.openapi.openapi_gen import OpenAPIDoc
                doc = OpenAPIDoc(cls)
                return HttpResponse(doc.json, content_type=pdm.MediaTypes.application__json.value)

        getattr(cls, "urlpatterns", []).append(as_django_path(cls.OPENAPI_PATH, OpenAPIHandler.as_view()))

    @classmethod
    def gen_redoc(cls):
        """添加一个redoc接口"""

        class ReDOCHandler(cls):
            NEED_COLLECT = False

            def get(self) -> HttpResponse:
                from golive_django_openapi.openapi.openapi_gen import OpenAPIDoc
                if not self.OPENAPI_ABSOLUTE_PATH:
                    return HttpResponse(
                        f"{cls} misconfigured: redoc not working since {self.OPENAPI_ABSOLUTE_PATH=} is unset",
                        status=500
                    )
                return HttpResponse(OpenAPIDoc.redoc(self.OPENAPI_ABSOLUTE_PATH))

        getattr(cls, "urlpatterns", []).append(as_django_path(cls.OPENAPI_REDOC_PREFIX, ReDOCHandler.as_view()))

    @classmethod
    def gen_meta(cls):
        for hmn in cls.http_method_names:
            the_method = getattr(cls, hmn, None)
            if not the_method:
                continue
            if not getattr(the_method, "operation_meta", None):
                docstring = getattr(the_method, "__doc__", "")
                the_method.operation_meta = OpenAPIOperationMeta(description=docstring)
            if not getattr(the_method, "req_meta", None):
                the_method.req_meta = RequestMethodMeta()
            if not getattr(the_method, "resp_meta", None):
                the_method.resp_meta = ResponseMethodMeta()

    @classmethod
    def gen_validators(cls) -> typing.Dict[str, RequestMethodValidator]:
        """
        创建当前类定义的每个方法的校验，并且把校验结构体拼装好放在各自的方法里，以缓存数据
        :return:
        """
        ret = {}
        for hmn in cls.http_method_names:
            the_method = getattr(cls, hmn, None)
            if not the_method:
                continue
            if not getattr(the_method, "validator", None):
                annotations = typing.get_type_hints(the_method)
                if "return" in annotations.keys():
                    # return是保留关键字，无法在引用名中使用
                    annotations = copy.deepcopy(annotations)
                    annotations["ret"] = annotations.pop("return")
                for k, annotation in annotations.items():
                    if safe_issubclass(annotation, (HttpResponse,)):
                        pass
                    elif not safe_issubclass(annotation, pdm.pdm):
                        annotations[k] = create_pdm({"__root__": annotation}, arbitrary_types_allowed=True)
                try:
                    the_method.validator = RequestMethodValidator(
                        method_name=hmn,
                        method=the_method,
                        **annotations
                    )
                except ValidationError as e:
                    cls.logger.error(f"========= error raised at {cls} =========")
                    raise e
            ret[hmn] = the_method.validator
        return ret

    def __init__(self, **kwargs):

        super(BaseOpenAPIHandler, self).__init__(**kwargs)

        # 实际传给请求方法的参数实例
        self.validators_to_pass_to_request = {}

        # 本次请求具体使用的方法引用
        # 在dispatch之后填充
        self.handler: typing.Optional[typing.Callable] = None

        # 最终返回的响应对象
        self.response = HttpResponse()

        # 提示信息
        self.resp_msg = ""

    def exception_handler(self,
                          e: Exception,
                          resp_validation_failure: bool = False):
        """
        错误处理
        :param e:
        :param resp_validation_failure: 当前异常是否为请求返回时候的校验失败
        :return:
        """
        error_resp_outer = pdm.BaseJsonRespPDM()

        if isinstance(e, ValidationError):
            error_resp_outer.msg = f"参数错误： {str(e)}"
            # 增加一个便于调试用的错误信息
            error_resp_outer.msg_array = error_resp_outer.msg.split(os.linesep)
            self.response.status_code = 400
            if resp_validation_failure:
                self.response.status_code = 500

        elif isinstance(e, json.JSONDecodeError):
            error_resp_outer.msg = f"json解析失败: {str(e)}"
            self.response.status_code = 400

        elif isinstance(e, IntegrityError):
            error_resp_outer.msg = f"数据一致性错误：{str(e)}"
            self.response.status_code = 400

        elif isinstance(e, OpenAPIException):
            error_resp_outer.msg = f"{e.__doc__}：{str(e)}"
            self.response.status_code = e.status_code

        else:
            error_resp_outer.msg = f"未捕捉的错误：{e.__doc__}：{str(e)}"
            # 增加一个便于调试用的错误信息
            error_resp_outer.msg_array = error_resp_outer.msg.split(os.linesep)
            self.response.status_code = 500
        self.logger.error(traceback.format_exc())
        r = pdm.BaseJsonRespPDM(**{
            **error_resp_outer.dict(),
        }).dict()
        r = json.dumps(
            r,
            ensure_ascii=self.RESPONSE_JSON_ENSURE_ASCII,
            indent=self.RESPONSE_JSON_INDENT
        )
        self.response.content = r
        return self.response

    def run_before_resp(self, k):
        a = getattr(self.handler.validator, k, None)
        if not a:
            return
        b = getattr(a, "before_resp", None)
        if not b:
            return
        self.validators_to_pass_to_request[k].before_resp(self)

    def process_resp(self, resp_type, ret_content):
        """
        处理返回数据的校验
        :param resp_type: 接口返回类型定义
        :param ret_content: 接口返回对象
        :return:
        """
        if resp_type is HttpResponse and isinstance(ret_content, HttpResponse):
            # 兼容一下特殊情况需要直接返回django http response对象
            return ret_content
        if resp_type is not None:
            # 进行预处理
            self.run_before_resp("querystring")  # 暂时只处理querystring
            try:
                ret_content = resp_type.make_resp(self, ret_content)
                r = ret_content.json_dict()
            except ValidationError as e:
                raise Exception(f"""
======================================================
validation error when making response: 
{e}

{self.__class__}.{self.handler}
{resp_type=}
{ret_content=}
======================================================
""")

            # class ConstructedOuter(pdm.pdm):
            #     __root__: resp_type
            #
            # r = ConstructedOuter(__root__=ret_content).json_dict()
            # r = pop_root(r)
        else:
            r = None
        r = json.dumps(
            r,
            ensure_ascii=self.RESPONSE_JSON_ENSURE_ASCII,
            indent=self.RESPONSE_JSON_INDENT
        )
        self.response.content = r
        self.response.headers["content-type"] = pdm.MediaTypes.application__json.value
        return self.response

    def update_resp_with_method_resp_meta(self, handler):
        i_resp_meta = getattr(handler, "resp_meta", None)
        if not i_resp_meta:
            i_resp_meta = ResponseMethodMeta()
        self.response.status_code = i_resp_meta.status_code
        self.response.headers["Content-Type"] = i_resp_meta.content_type

    def body_data(self, method):
        """根据接口元信息返回body的数据"""
        rm: RequestMethodMeta = method.req_meta
        if rm.body_media_type == pdm.MediaTypes.application__json.value:
            return json.loads(self.request.body)
        elif rm.body_media_type == pdm.MediaTypes.multipart__form_data.value:
            return self.request.POST.dict()
        else:
            assert 0, f"unsupported request body media type: {rm.body_media_type}"

    def dispatch(self, request, *args, **kwargs):
        """分发请求，校验输入输出"""
        if request.method.lower() not in self.http_method_names:
            return self.http_method_not_allowed(request, *args, **kwargs)
        self.handler = getattr(self, request.method.lower(), None)
        if not self.handler:
            return self.http_method_not_allowed(request, *args, **kwargs)
        try:
            self.update_resp_with_method_resp_meta(self.handler)
            self.gen_meta()
            self.gen_validators()
            validator = self.handler.validator
            if validator.querystring:
                self.validators_to_pass_to_request["querystring"] = validator.querystring(**self.request.GET.dict())
            if validator.body:
                self.validators_to_pass_to_request["body"] = validator.body(**self.body_data(self.handler))
            if validator.headers:
                self.validators_to_pass_to_request["headers"] = validator.headers(**self.request.headers)
            r = self.handler(**self.validators_to_pass_to_request)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            return self.exception_handler(e)
        try:
            return self.process_resp(validator.ret, r)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            return self.exception_handler(e, resp_validation_failure=True)

    @classmethod
    def ensure_first(cls, queryset):
        """
        返回查询集的第一个实例，如果不存在，就报404
        :return:
        """
        assert isinstance(queryset, QuerySet),\
            f"{queryset=} must be a django model query set, not {type(queryset)=}"
        r = queryset.first()
        if r is None:
            target_type_name = queryset.model.__doc__
            raise APINotFound(f"找不到{target_type_name}")
        return r

    @property
    def is_mobile(self) -> bool:
        """当前请求是否从移动设备发出"""
        ua = self.request.headers.get("User-Agent", None)
        if not ua or not isinstance(ua, str):
            return False
        if re.compile(
                r"(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|"
                r"BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|"
                r"BrowserNG|WebOS|Symbian|Windows Phone|MEIZU)").findall(ua):
            return True
        return False
