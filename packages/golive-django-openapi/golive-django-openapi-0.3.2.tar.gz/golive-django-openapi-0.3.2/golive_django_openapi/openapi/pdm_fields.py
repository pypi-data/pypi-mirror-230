# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "GreaterThanZeroInt",
    "NonEmptyStr",
    "StrListFromDotSplitStr",
    "IntListFromDotSplitStr",
    "Datetime",
    "Date",
    "Time",
    "OptionalQuery",
    "GitBranchName",
]

from typing import Dict, Any, List, Union
from datetime import datetime, date, time

from golive_django_openapi.utils import const
from golive_django_openapi.utils import dt_utils


class GreaterThanZeroInt(int):
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='integer greater than 0', format='1')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int]) -> int:
        assert value > 0, "integer greater than 0 required"
        return value


class NonEmptyStr(str):
    """非空文本"""
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format='non-empty-str')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int]) -> str:
        assert isinstance(value, str) and len(value) > 0, "non-empty string required"
        return value


class StrListFromDotSplitStr(list):
    """逗号分隔文本转文本列表"""
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format='this,is,an,example')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field) -> List[str] | None:
        if value:
            return [i for i in value.split(",") if i]
        if field.required:
            raise TypeError("a list of string with dot-split required")


class IntListFromDotSplitStr(list):
    """点分隔文本转int列表"""
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format='1,2,123,-1,35')

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field) -> List[int] | None:
        if value:
            return [int(i) for i in value.split(",") if i]
        if field.required:
            raise TypeError("a list of int with dot-split required")


class Datetime(datetime):
    """日期时间"""
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format=const.COMMON_DATETIME_FORMAT)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field) -> datetime | None:
        if value:
            return dt_utils.str_to_dt(value)
        if field.required:
            raise TypeError("datetime required.")


class Date(date):
    """日期"""
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format=const.COMMON_DATE_FORMAT)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field) -> date | None:
        if value:
            return dt_utils.str_to_d(value)
        if field.required:
            raise TypeError("date required.")


class Time(time):
    """时间"""
    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format=const.COMMON_TIME_FORMAT)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field) -> time | None:
        if value:
            return dt_utils.str_to_t(value)
        if field.required:
            raise TypeError("time required.")


class OptionalQuery:
    """空文本/null视为忽略查询"""

    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format="..")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field):
        if value is None or value.strip() == "":
            return field.field_info.default
        return value


# OptionalQuery 最好放在全部或的最后
OptionalQuery = OptionalQuery | None


class GitBranchName(str):
    """git仓库分支名"""

    __slots__ = ()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type=cls.__doc__, format="this_is_a_branch, valid-branch-name")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, bytes, int], field):
        if value is None or value.strip() == "":
            raise ValueError("分支名为空")
        if "." in value:
            raise ValueError("git分支名不允许包含'.'")
        return value
