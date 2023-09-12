# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "PDMJsonField",
]

from django.db.models import JSONField


class PDMJsonField(JSONField):
    """
    支持输入输出的pdm的json field

    TODO 请注意不支持__root__参数，json field的最外层必须是字典（即json的object)
    """

    def __init__(self, pdm=None, **kwargs):
        """
        :param pdm: 配置当前json field使用的pdm
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.pdm = pdm
        if pdm and pdm.__doc__:
            self.help_text = pdm.__doc__

    def _pop_root(self, validated):
        if "__root__" in validated:
            return validated["__root__"]
        return validated

    def validate(self, value, model_instance):
        assert self.pdm, f"no pdm configured for {model_instance}"
        validated = self._pop_root(value.json_dict())
        super().validate(validated, model_instance)

    def get_prep_value(self, value):
        from golive_django_openapi.openapi import pdm
        if self.pdm and isinstance(value, self.pdm):
            prepared_value = value.json_dict()
            prepared_value = self._pop_root(prepared_value)
            return super().get_prep_value(prepared_value)
        if self.pdm and isinstance(value, list):
            value = value.copy()
            for i in range(len(value)):
                if isinstance(value[i], pdm):
                    value[i] = value[i].json_dict()
            return super().get_prep_value(value)
        else:
            return super().get_prep_value(value)

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        if value is None:
            value = {}
        if "__root__" in self.pdm.__annotations__:
            r = self.pdm(__root__=value)
            return r.__root__
        return self.pdm(**value)
