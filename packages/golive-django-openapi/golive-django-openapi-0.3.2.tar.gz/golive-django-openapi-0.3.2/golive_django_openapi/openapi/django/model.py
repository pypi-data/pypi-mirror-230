# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ModelPDMMixin",
]

from enum import StrEnum

from django.apps import apps

from golive_django_openapi.utils.cls_utils import *
from .model_pdm_meta.getter import *
from .model_pdm_meta.setter import *
from .model_pdm_meta.config import BaseModelPDMConfig
from .model_pdm_meta.prop_plugins import BasePropPlugin


# getter model pdm的前缀
MODEL_PDM_GETTER_PREFIX = "Getter"
# setter model pdm的前缀
MODEL_PDM_SETTER_PREFIX = "Setter"


class ModelPDMMixin:
    """
    用于混入一个普通的django model的基类，从而改造其子类，
    成为支持支持ModelPDM的django model
    """

    # ========================================
    # 用户需要在子类的这里配置config
    # 例如：
    #
    # class Getter(BaseModelPDMConfig):
    #     column_include = ....
    #
    # class GetterListSimple(BaseModelPDMConfig):
    #     column_include = ....
    #
    # ========================================

    # 标记当前model是否已经初始化，防止多次初始化
    MODEL_PDM_INITIALIZED: bool = False

    # 当前model的全部getter
    ALL_GETTERS = []

    # 当前model的全部setter
    ALL_SETTERS = []

    # 当前model的全部getter的枚举类型
    ALL_GETTERS_ENUM = None

    # 当前model是否允许缺省getter
    # 如果有任何一个getter的switch_flag为空文本（即默认值），那么该getter就是缺省getter
    GETTER_SWITCH_ALLOW_DEFAULT = False

    @classmethod
    def collect(cls):
        """
        在顶层的django model类中跑本方法，找到所有django model，注册并启用所有pdm
        必须在getter setter被使用之前跑本方法以初始化
        """
        for model in apps.get_models():
            if model._meta.abstract:
                continue
            if not safe_issubclass(model, cls):
                continue
            if model.MODEL_PDM_INITIALIZED:
                continue
            # 查找并运行model中的prop插件
            for i in dir(model):
                if i.startswith("_"):
                    continue
                target = getattr(model, i)
                if isinstance(target, BasePropPlugin):
                    target.build(model)

            # 用于检测是否有重复的switch flag
            getter_switch_flags = set()
            setter_switch_flags = set()
            # 重复赋值防止引用到父类
            setattr(model, "ALL_GETTERS", [])
            setattr(model, "ALL_SETTERS", [])
            # 初始化ModelPDM
            for i in dir(model):
                if i.startswith("_"):
                    continue
                target = getattr(model, i)
                if i.startswith(MODEL_PDM_SETTER_PREFIX):
                    assert safe_issubclass(target, (object, BaseModelPDMConfig))
                    model_pdm = ModelPDMMetaSetter.init_config(model, target)
                    # verify
                    assert model_pdm._meta.switch_flag not in setter_switch_flags, \
                        f"duplicated setter switch flag in {model}: {model_pdm._meta.switch_flag} (in {target})"
                    setter_switch_flags.add(model_pdm._meta.switch_flag)
                    # append
                    setattr(model, i, model_pdm)
                    model.ALL_SETTERS.append(model_pdm)
                elif i.startswith(MODEL_PDM_GETTER_PREFIX):
                    assert safe_issubclass(target, (object, BaseModelPDMConfig))
                    model_pdm = ModelPDMMetaGetter.init_config(model, target)
                    # verify
                    assert model_pdm._meta.switch_flag not in getter_switch_flags, \
                        f"duplicated getter switch flag in {model}: {model_pdm._meta.switch_flag} (in {target})"
                    getter_switch_flags.add(model_pdm._meta.switch_flag)
                    # append
                    setattr(model, i, model_pdm)
                    model.ALL_GETTERS.append(model_pdm)
                else:
                    continue

            # 配置当前model的全部getter的枚举，以及检查是否有缺省getter
            all_getters_flags = [i._meta.switch_flag for i in model.ALL_GETTERS]
            model.ALL_GETTERS_ENUM = StrEnum(f"{model.__name__}__getter_switch_enum", " ".join(all_getters_flags))
            if "" in all_getters_flags:
                model.GETTER_SWITCH_ALLOW_DEFAULT = True
            # 确认初始化完毕
            model.MODEL_PDM_INITIALIZED = True
