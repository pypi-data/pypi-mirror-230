# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ModelPDMMetaSetter"
]

from typing import Type, get_type_hints

from pydantic import PrivateAttr, Field

from .base import *
from golive_django_openapi.openapi.models.base import pdm
from ..model_pdm import BaseModelPDMSetter
from ...openapi_gen import schema_meta


class ModelPDMMetaSetter(BaseModelPDMMeta):

    base_pdm: Type[pdm] = Field(BaseModelPDMSetter)

    _prop_method_regex: str = PrivateAttr(r"^set_(.+?)$")

    def get_prop_validator(self, prop):
        doc = prop.__doc__ if prop.__doc__ else ""
        calced_annotations = get_type_hints(prop)
        calced_annotations.pop("return", None)
        assert len(calced_annotations.keys()) == 1, f"got multiple/no input annotations in {prop}"
        t = list(calced_annotations.values())[0]
        return schema_meta(t, description=doc)

    @classmethod
    def get_pdm_model_name(cls, model, *args):
        return super().get_pdm_model_name(model, *args) + "_SETTER"
