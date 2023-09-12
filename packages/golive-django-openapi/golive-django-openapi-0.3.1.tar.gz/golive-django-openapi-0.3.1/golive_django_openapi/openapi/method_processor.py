# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "BaseOpenAPIMethodProcessor",
    "DeleteProcessor",
]

from typing import Type, Callable, Optional, Any

from django.db.models import Model

from .models import pdm
from .models.shortcuts import qm, build_query


class BaseOpenAPIMethodProcessor(pdm):
    """接口请求方法生成器"""

    # 需要附加到生成出来的方法上的装饰器，支持单个或者列表
    decorator: tuple[Callable, ...] | Callable = ()

    def decorate(self, the_method):
        if not self.decorator:
            return the_method
        if not isinstance(self.decorator, tuple):
            self.decorator = (self.decorator,)
        for d in self.decorator:
            the_method = d(the_method)
        return the_method

    def build(self,
              method_name: str) -> Callable:
        raise NotImplementedError


class PostProcessor(BaseOpenAPIMethodProcessor):

    ModelPDM: Type[pdm]

    def build(self,
              method_name: str) -> Callable:
        myself = self

        def post(itself, body: myself.ModelPDM):
            with myself.ModelPDM._django_model() as new_record:
                body.to_record(new_record)

        post.__doc__ = self.ModelPDM._django_model.__doc__
        return self.decorate(post)


class PatchProcessor(BaseOpenAPIMethodProcessor):

    ModelPDM: Type[pdm]

    # 查询的字段
    QueryKey: str = "id"

    def build(self,
              method_name: str) -> Callable:
        body_annotation = qm(
            query=build_query({self.QueryKey: int | str}),
            modify=self.ModelPDM
        )

        myself = self

        def patch(itself, body: body_annotation):
            with itself.ensure_first(myself.ModelPDM._django_model().filter(**body.query.dict())) as existed_record:
                body.to_record(existed_record)

        patch.__doc__ = self.ModelPDM._django_model.__doc__
        return self.decorate(patch)


class DeleteProcessor(BaseOpenAPIMethodProcessor):

    Model: Type[Model]

    # 查询的字段
    QueryKey: str = "id"
    # 字段类型，通常是int，个别情况是str，需要看表如何定义
    QueryKeyType: Type[Any] = int

    def build(self,
              method_name: str) -> Callable:
        body_annotation = qm(
            query=build_query({
                self.QueryKey: Optional[self.QueryKeyType],
                self.QueryKey + "__in": Optional[list[self.QueryKeyType]]
            }, at_least_one=True),
        )

        myself = self

        def delete(itself, body: body_annotation):
            the_model = myself.Model
            the_model.bulk_delete(the_model.filter(**body.query.dict()))

        delete.__doc__ = f"删除：{self.Model.__doc__}"
        return self.decorate(delete)
