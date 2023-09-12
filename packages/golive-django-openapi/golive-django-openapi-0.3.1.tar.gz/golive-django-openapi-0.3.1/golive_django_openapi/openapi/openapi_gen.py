# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "OpenAPIOperationMeta",
    "OpenAPISchemaMeta",
    "schema_meta",
    "openapi_models",
    "OpenAPIDoc",
]

import json
from typing import Optional, Dict, List, Any, Tuple, Type, Set, Union
from enum import Enum

from pydantic import BaseModel
from pydantic.schema import get_model_name_map, field_schema, model_schema, get_flat_models_from_models, model_process_schema
from pydantic.fields import Undefined, FieldInfo, Field
from django.http.response import HttpResponse
# ======================================================================
# 注意事项：
# 除了models和编码器，凡是涉及openapi渲染的具体逻辑，不要从fastapi引用。
import fastapi.openapi.constants
from fastapi.openapi import models as openapi_models
from fastapi.encoders import jsonable_encoder
# ======================================================================

from golive_django_openapi.utils.cls_utils import *


class OpenAPIOperationMeta(BaseModel):
    """
    每个请求方式的一部分可配置参数
    https://openapi.apifox.cn/#operation-%E5%AF%B9%E8%B1%A1
    """
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    externalDocs: Optional[openapi_models.ExternalDocumentation] = None
    operationId: Optional[str] = None
    deprecated: Optional[bool] = None
    security: Optional[List[Dict[str, List[str]]]] = None


class OpenAPISchemaMeta(BaseModel):
    """
    字段元信息
    请注意，部分字段元信息已经由pydantic的ModelField提供了，这里只增加部分未提供但是openapi有必要的字段
    """
    description: str | None
    deprecated: bool = False


# 标记的schema meta信息在结构里的键名
EXTRA_SCHEMA_META_KEY = "schema_meta"


def schema_meta(
        target: Type | FieldInfo | Tuple[Type, FieldInfo] | Tuple[Type, Any] | Undefined = Undefined,
        description: str = None,
        **kwargs) -> Any:
    """
    给pydantic的field标记字段的元信息
    :param target:
    :param description: 字段说明，用于展示在openapi文档上
    :param kwargs:
    :return:
    """
    # import warnings
    # warnings.warn("DO NOT USE IT ANY MORE: please use pydantic.Field() instead.", DeprecationWarning)

    scm_meta = OpenAPISchemaMeta(description=description, **kwargs)

    def set_schema_meta(t):
        t.extra[EXTRA_SCHEMA_META_KEY] = scm_meta

    if isinstance(target, FieldInfo):
        set_schema_meta(target)
        return target
    if isinstance(target, tuple):
        assert len(target) == 2, "target should be a tuple containing 2 items."
        if isinstance(target[1], FieldInfo):
            set_schema_meta(target[1])
            return target
        else:
            target = (target[0], Field(target[1]))
            set_schema_meta(target[1])
            return target
    if target is Undefined:
        return Undefined
    # at last, suppose target is Type
    target = (target, Field())
    set_schema_meta(target[1])
    return target


def recursive_prepare(d):
    """
    递归处理一些额外事项
    1弹出schema_meta(EXTRA_SCHEMA_META_KEY)，这些meta被包裹在dict里，而外层才是openapi标准规定的位置
    2删除definitions，全部输出的组件都已经放到components结构下了，不知道为什么pydantic还是会默认放一个到definitions里
    :param d:
    :return:
    """
    if isinstance(d, dict):
        d.pop("definitions", None)
        d.update(d.pop(EXTRA_SCHEMA_META_KEY, {}))
        for k, v in d.items():
            d[k] = recursive_prepare(v)
        return d
    elif isinstance(d, (list, tuple, set)):
        r = []
        for item in d:
            r.append(recursive_prepare(item))
        return r
    else:
        return d


class OpenAPIDoc:
    """生成openapi接口文档"""

    # 定义components.schema中对象被引用时的前缀
    COMPONENTS_SCHEMA_PREFIX = fastapi.openapi.constants.REF_PREFIX

    # pydantic生成schema的参考model模板入口
    COMPONENTS_SCHEMA_TEMPLATE = COMPONENTS_SCHEMA_PREFIX + "{model}"

    @classmethod
    def get_model_definitions(
            cls,
            flat_models: Set[Union[Type[BaseModel], Type[Enum]]],
            model_name_map: Dict[Union[Type[BaseModel], Type[Enum]], str],
    ) -> Dict[str, Any]:
        """from fastapi.utils.get_model_definitions"""
        definitions: Dict[str, Dict[str, Any]] = {}
        for model in flat_models:
            m_schema, m_definitions, m_nested_models = model_process_schema(
                model, model_name_map=model_name_map, ref_prefix=cls.COMPONENTS_SCHEMA_PREFIX
            )
            definitions.update(m_definitions)
            model_name = model_name_map[model]
            if "description" in m_schema:
                m_schema["description"] = m_schema["description"].split("\f")[0]
            definitions[model_name] = m_schema
        return definitions

    def __init__(self, base_openapi_handler):
        assert (openapi_entry := getattr(base_openapi_handler, "OPENAPI_ENTRY", None)), "no openapi entry configured!"
        assert isinstance(openapi_entry, openapi_models.OpenAPI), "'OPENAPI_ENTRY' is not an instance of OpenAPI!"
        self.base_handler = base_openapi_handler
        self.named_models = self.get_named_models()
        self.model_model_name_dict = get_model_name_map(self.named_models)
        self.components = openapi_models.Components()
        self.gen_components_schema()
        self.paths = dict()
        self.gen_paths()
        self.openapi = openapi_models.OpenAPI(
            **{
                **openapi_entry.dict(),
                "paths": self.paths,
                "components": self.components
            }
        )

    def get_named_models(self) -> set[type[BaseModel]]:
        """返回全部静态定义+动态定义并且非匿名的pydantic model"""
        origin_models = []
        for _, handler in self.base_handler.COLLECTED:
            for http_method_name, validator_of_the_method in handler.gen_validators().items():
                origin_models.extend(validator_of_the_method.all_models())
        return get_flat_models_from_models(origin_models)

    def gen_components_schema(self):
        """
        在schema项里生成对象
        """
        definitions = self.get_model_definitions(flat_models=self.named_models, model_name_map=self.model_model_name_dict)
        if definitions:
            self.components.schemas = {k: definitions[k] for k in sorted(definitions)}

    def gen_parameters(self, model: BaseModel, in_: openapi_models.ParameterInType) -> list[openapi_models.Parameter]:
        """from fastapi.openapi.utils.get_openapi_operation_parameters"""
        parameters = []
        model_values = getattr(model, "__fields__", dict()).values()
        for param in model_values:
            field_info = param.field_info
            the_schema = field_schema(
                    param, model_name_map=self.model_model_name_dict,
                    ref_prefix=self.COMPONENTS_SCHEMA_PREFIX, ref_template=self.COMPONENTS_SCHEMA_TEMPLATE
                )[0]
            parameter = {
                "name": param.alias,
                "in": in_,
                "required": param.required,
                "schema": the_schema,
            }
            if field_info.description:
                parameter["description"] = field_info.description
            parameters.append(parameter)
        return parameters

    def gen_responses(self, resp_meta, validator) -> dict[str, openapi_models.Response]:
        ret_field = validator.ret
        resp = None
        if ret_field and safe_issubclass(ret_field, HttpResponse):
            # 针对返回特定django.HttpResponse的情况处理一下
            resp = openapi_models.Response(
                description=resp_meta.status_code_description,
                content={resp_meta.content_type: openapi_models.MediaType(
                    **{
                        "schema": openapi_models.Schema(
                            title="anonymous http response",
                            type="normal http response"
                        )
                    }
                )}
            )
        elif ret_field:
            ret_schema = model_schema(
                ret_field, ref_prefix=self.COMPONENTS_SCHEMA_PREFIX, ref_template=self.COMPONENTS_SCHEMA_TEMPLATE)
            resp = openapi_models.Response(
                description=resp_meta.status_code_description,
                content={resp_meta.content_type: openapi_models.MediaType(
                    **{
                        "schema": ret_schema
                    }
                )}
            )
        return {str(resp_meta.status_code): resp}

    def gen_request_body(self, req_meta, validator) -> openapi_models.RequestBody | None:
        body_field = validator.body
        if not body_field:
            return
        body_schema = model_schema(
            body_field, ref_prefix=self.COMPONENTS_SCHEMA_PREFIX, ref_template=self.COMPONENTS_SCHEMA_TEMPLATE)
        request_media_content: Dict[str, Any] = {"schema": body_schema}
        ret = openapi_models.RequestBody(
            description=req_meta.body_description,
            content={req_meta.body_media_type: openapi_models.MediaType(**request_media_content)}
        )
        return ret

    @classmethod
    def gen_operation_id(cls, url: str, handler_method_name: str) -> str:
        """生成请求操作id"""
        return "_".join([*url.split("/")]) + f"__{handler_method_name}"

    @classmethod
    def allow_request_body(cls, hmn: str) -> bool:
        """判断是否允许请求体"""
        if hmn.lower() in ("get", "options"):
            return False
        return True

    def gen_operation(self, url: str, handler_method_name: str, method) -> openapi_models.Operation:
        """
        https://openapi.apifox.cn/#operation-%E5%AF%B9%E8%B1%A1
        :return:
        """
        op_meta = getattr(method, "operation_meta")
        req_meta = getattr(method, "req_meta")
        resp_meta = getattr(method, "resp_meta")
        if not op_meta.description:
            op_meta.description = getattr(method, "__doc__", "")
        op = openapi_models.Operation(**{
            "operationId": self.gen_operation_id(url, handler_method_name),
            "parameters": [
                *self.gen_parameters(method.validator.querystring, openapi_models.ParameterInType.query),
                *self.gen_parameters(method.validator.headers, openapi_models.ParameterInType.header),
            ],
            "requestBody": self.gen_request_body(req_meta, method.validator) if self.allow_request_body(handler_method_name) else None,
            "responses": self.gen_responses(resp_meta, method.validator),
            **op_meta.dict()
        })
        return op

    def gen_path_item(self, url: str, handler) -> openapi_models.PathItem:
        """
        https://openapi.apifox.cn/#path-item-%E5%AF%B9%E8%B1%A1
        :param url:
        :param handler:
        :return:
        """
        pi = openapi_models.PathItem()
        for hmn in handler.http_method_names:
            method = getattr(handler, hmn, None)
            if method:
                setattr(pi, hmn, self.gen_operation(url, hmn, method))
        return pi

    def gen_paths(self):
        """生成url"""
        for url, handler in self.base_handler.COLLECTED:
            handler.gen_meta()
            handler.gen_validators()
            if not url.startswith("/"):
                url = "/" + url
            self.paths[url] = self.gen_path_item(url, handler)

    @property
    def json(self) -> Any:
        """输出openapi的json文档"""
        r = jsonable_encoder(self.openapi, by_alias=True, exclude_none=True, sqlalchemy_safe=False)
        r = recursive_prepare(r)
        return json.dumps(r, ensure_ascii=False, indent=4)

    @classmethod
    def redoc(cls, openapi_json_absolute_url: str) -> str:
        """输出一个用于渲染展示redoc的页面"""
        return """
<!DOCTYPE html>
<html>
  <head>
    <title>Redoc</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <!--
    Redoc doesn't change outer page styles
    -->
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='URL_TO_REPLACE'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
""".replace("URL_TO_REPLACE", openapi_json_absolute_url)
