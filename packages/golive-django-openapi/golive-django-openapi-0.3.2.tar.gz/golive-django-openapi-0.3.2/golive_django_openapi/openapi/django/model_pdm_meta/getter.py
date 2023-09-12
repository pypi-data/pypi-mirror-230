# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ModelPDMMetaGetter",
]

from typing import Type, get_type_hints

from pydantic import PrivateAttr, Field

from .base import *
from golive_django_openapi.openapi.models.base import pdm
from ..model_pdm import BaseModelPDMGetter
from ...openapi_gen import schema_meta


class ModelPDMMetaGetter(BaseModelPDMMeta):

    base_pdm: Type[pdm] = Field(BaseModelPDMGetter)

    _prop_method_regex: str = PrivateAttr(r"^(?!set_)(.+?)$")

    def get_prop_validator(self, prop):
        doc = prop.__doc__ if prop.__doc__ else ""
        calced_annotations = get_type_hints(prop)
        assert "return" in calced_annotations, f"no return annotation was found for {prop} in {self.__class__}"
        t = calced_annotations["return"]
        return schema_meta(t, description=doc)

    @classmethod
    def get_pdm_model_name(cls, model, *args):
        return super().get_pdm_model_name(model, *args) + "_GETTER"
