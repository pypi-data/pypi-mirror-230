# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "StatusMachineException",
    "NoWayTurnToTarget",
    "StatusMachine",
    "StatusMachineValue",
    "SMV",
]

from enum import StrEnum, Enum
from collections import defaultdict
from typing import Optional, Union, Dict, Tuple, Type, Callable, List, Any

from .pydantic_utils import JSONSerializablePDM

from .logger_utils import *


# 全部带有flag的状态机
EXPORTED_STATUS_MACHINES: Dict[str, Type["StatusMachine"]] = {}

# 缓存生成的状态机pydantic模型
STATUS_MACHINE_ENUM_MODELS: Dict[str, Type[Enum]] = {}


class StatusMachineException(Exception):

    pass


class NoWayTurnToTarget(StatusMachineException):
    """无法跳转到目标状态"""

    pass


class StatusMachineValue:

    def __init__(self,
                 name: str,
                 next_status: Optional[Union["StatusMachineValue", str, Tuple]] = (),
                 extra: dict | list | tuple | JSONSerializablePDM | None = None,
                 **kwargs):
        """
        :param name: 展示名
        :param next_status: 直接下一步状态
        :param extra: 额外信息，可以是任何值。
        :param kwargs:
        """
        self.value: str = None
        self.name = name
        self.next_status: Tuple["StatusMachineValue"] = next_status
        self.extra = extra

    @property
    def next_status_values(self) -> list[str]:
        """next_status字段的文本值"""

        r = []

        def deal_with_single_value(v):
            if isinstance(i, str):
                r.append(i)
            elif isinstance(i, StatusMachineValue):
                r.append(i.value)
            else:
                assert 0, f"bad next_status of {i}"

        for i in self.next_status:
            if isinstance(i, (tuple, list)):
                for j in i:
                    deal_with_single_value(j)
            else:
                deal_with_single_value(i)
        return r

    def to_dict(self, v="value", n="name") -> dict:
        exported_extra = self.extra
        if isinstance(exported_extra, JSONSerializablePDM):
            exported_extra = exported_extra.json_dict()
        return {
            v: self.value,
            n: self.name,
            "extra": exported_extra,
            "next_status": self.next_status_values
        }

    def __str__(self):
        return f"<SMV - {self.value}: {self.name}>"


SMV = StatusMachineValue


class StatusMachineMeta(LoggerMixin):

    def __repr__(cls):
        return f"<{cls.__name__}>"

    def _referring_as(cls, v, n: int):
        """引用次数为"""
        cls._status_referred_time[v][1] = n

    def _referred_up(cls, v):
        """被引用次数加1"""
        cls._status_referred_time[v][0] += 1

    def _check_next(cls, a_list: Dict[str, StatusMachineValue]):
        """
        检查下层依赖
        :param a_list:
        :return:
        """
        for value, smv in a_list.items():
            if not smv.next_status:
                cls._referring_as(smv.value, 0)
                smv.next_status = ()
            elif isinstance(smv.next_status, StatusMachineValue):
                cls._referred_up(smv.next_status.value)
                cls._referring_as(smv.value, 1)
                smv.next_status = (smv.next_status,)
            elif isinstance(smv.next_status, str):
                smv.next_status = (a_list[smv.next_status],)
                cls._referred_up(smv.next_status[0].value)
                cls._referring_as(smv.value, 1)
            elif isinstance(smv.next_status, (tuple, list)):
                r = []
                for i in smv.next_status:
                    if isinstance(i, str):
                        i = a_list[i]
                    elif isinstance(i, StatusMachineValue):
                        pass
                    else:
                        assert 0
                    r.append(i)
                    cls._referred_up(i.value)
                cls._referring_as(smv.value, len(r))
                smv.next_status = tuple(r)

    def __init__(cls, name, bases, attrs: Dict):
        super().__init__(name, bases, attrs)

        # 收集到的状态变更trigger
        cls.STATUS_TRIGGERS = {}

        # 全部的smv dict
        cls.ALL_STATUS_DICT: Dict[str, StatusMachineValue] = {}

        # 每个smv的：[被引用次数，引用别的的次数]
        # TODO 请注意被引用是可以循环的，因此这个数字只统计至少被引用的次数。
        #      统计这个数字的意义是找出谁是头谁是尾
        cls._status_referred_time = defaultdict(lambda: [0, 0])

        # 入口dict
        cls.ENTRIES_DICT: Dict[str, StatusMachineValue] = {}

        # 出口dict
        cls.EXIT_DICT: Dict[str, StatusMachineValue] = {}

        for value, smv in attrs.items():
            if isinstance(smv, StatusMachineValue):
                smv.value = value
                cls.ALL_STATUS_DICT[value] = smv
        cls._check_next(cls.ALL_STATUS_DICT)
        for value, flag in cls._status_referred_time.items():
            if flag[0] == 0:
                cls.ENTRIES_DICT[value] = cls.ALL_STATUS_DICT[value]
            if flag[1] == 0:
                cls.EXIT_DICT[value] = cls.ALL_STATUS_DICT[value]

        # 判断是否需要输出
        if cls.EXPORT_FLAG:
            assert cls.EXPORT_FLAG not in EXPORTED_STATUS_MACHINES.keys(), \
                f"duplicated exported status_machine with {cls.EXPORT_FLAG=}"
            EXPORTED_STATUS_MACHINES[cls.EXPORT_FLAG] = cls

    def __iter__(cls):
        """用于适配django.model.field.choices"""
        yield from cls.all_items()


def status_convert_value(original_status, target_status):
    if isinstance(original_status, (str, type(None))):
        original_value = original_status
    elif isinstance(original_status, StatusMachineValue):
        original_value = original_status.value
    else:
        assert 0
    if isinstance(target_status, str):
        target_value = target_status
    elif isinstance(target_status, StatusMachineValue):
        target_value = target_status.value
    else:
        assert 0
    return original_value, target_value


class StatusMachine(metaclass=StatusMachineMeta):

    # 输出用的唯一标识，用于统一输出到接口以便前端使用
    # 如果不配置此参数，即不会输出到接口
    EXPORT_FLAG: str | None = None

    @classmethod
    def all(cls) -> Tuple[StatusMachineValue]:
        return tuple(cls.ALL_STATUS_DICT.values())

    @classmethod
    def all_items(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple([(smv.value, smv.name) for smv in cls.all()])

    @classmethod
    def all_values(cls) -> Tuple[str]:
        return tuple(cls.ALL_STATUS_DICT.keys())

    @classmethod
    def entries(cls) -> Tuple[StatusMachineValue]:
        return tuple(cls.ENTRIES_DICT.values())

    @classmethod
    def entries_values(cls) -> Tuple[str]:
        return tuple(cls.ENTRIES_DICT.keys())

    @classmethod
    def exits(cls) -> Tuple[StatusMachineValue]:
        return tuple(cls.EXIT_DICT.values())

    @classmethod
    def exits_values(cls) -> Tuple[str]:
        return tuple(cls.EXIT_DICT.keys())

    @classmethod
    def enum(cls):
        """返回当前status_machine的enum"""
        n = f"{cls.__name__}__StrEnum"
        m = STATUS_MACHINE_ENUM_MODELS.get(n, None)
        if not m:
            m = StrEnum(n, {i: i for i in cls.all_values()})
            m.__doc__ = cls.__doc__
            STATUS_MACHINE_ENUM_MODELS[n] = m
        return m

    @classmethod
    def get(cls, v: Optional[Union[str, StatusMachineValue]]) -> Optional[StatusMachineValue]:
        if isinstance(v, StatusMachineValue):
            return v
        return cls.ALL_STATUS_DICT.get(v, None)

    @classmethod
    def get_by_name(cls, name: str):
        reversed_dict = {smv.name: smv for smv in cls.ALL_STATUS_DICT.values()}
        return reversed_dict.get(name, None)

    @classmethod
    def turn(cls,
             original_status: Optional[Union[str, StatusMachineValue]],
             target_status: Union[str, StatusMachineValue], **kwargs) -> Optional[str]:
        """
        操作状态变更
        :param original_status:
        :param target_status:
        :return: 如果状态变更允许，则返回target_status的状态值（str），如果不允许直接抛出异常
        """
        original_status = cls.get(original_status)
        target_status = cls.get(target_status)
        st = status_convert_value(original_status, target_status)
        if original_status and target_status not in cls.get(original_status).next_status:
            raise NoWayTurnToTarget(f"{cls} - {original_status} to {target_status}")
        else:
            cb = cls.STATUS_TRIGGERS.get(st, None)
            if cb:
                cls.logger.info(f"{cls} - {original_status} to {target_status}: {cb}")
                cb(**kwargs)
            else:
                cls.logger.info(f"{cls} - {original_status} to {target_status}: no triggers")
            return target_status.value

    @classmethod
    def generate_all(cls,
                     v="value",
                     n="label",
                     for_all: Optional[Tuple[str, str]] = ("", "全部"),
                     available: Callable = lambda x: True) -> List[Dict[str, Any]]:
        """
        产生一个全部选项的字典
        :param v: 值的键
        :param n: 展示文本的键
        :param for_all: 是否增加一个"全部"
        :param available: 一个cb，接受当前的smv为参数，返回TrueFalse表示是否available
        :return:
        """
        r = [
            {
                **i.to_dict(v=v, n=n),
                "available": True if available(i) else False,
            } for i in cls.all()
        ]
        if for_all:
            _for_all = {v: for_all[0], n: for_all[1]}
            r.insert(0, _for_all)
        return r

    @classmethod
    def as_trigger(
            cls,
            original_status: Optional[StatusMachineValue],
            target_status: StatusMachineValue):
        """修改状态的时候触发"""

        def outer(func):

            cls.STATUS_TRIGGERS[(getattr(original_status, "value", None), target_status.value)] = func
            return func
        return outer

    @classmethod
    def ensure_get_to_dict(cls, v, *args, **kwargs) -> dict:
        """
        执行cls.get并.to_dict，输出一个字典，如果对象不存在，则输出空字典
        :param v:
        :param args:
        :param kwargs:
        :return:
        """
        obj = cls.get(v)
        if not obj:
            return {}
        return obj.to_dict(*args, **kwargs)

    # 下述方法用于适配pydantic
    def __init__(self, v):
        self.v = v

    @classmethod
    def all_items_openapi(cls) -> str:
        r = [f"{v}:{l}" for v, l in cls.all_items()]
        return ", ".join(r)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(
            type="string",
            format=cls.all_items_openapi(),
            description=cls.__doc__,
            enum=cls.all_values()
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field):
        assert v in cls.all_values(), f"{v} is not a status of {cls}, choices are: {cls.all_values()}"
        return v
