# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "Privilege",
    "PrivilegeType",
    "PT",
    "BasePermission"
]

from typing import Tuple, Union, Optional, Dict, List

from .logger_utils import *
from .status_machine import *


class PrivilegeTypeValue(StatusMachineValue):

    def __add__(self, other):
        return self, other

    def __str__(self):
        return f"<PrivilegeTypeValue - {self.value}: {self.name}>"


class PrivilegeType(StatusMachine):
    # 按照前后端归类
    backend = PrivilegeTypeValue("后端特权")
    frontend = PrivilegeTypeValue("前端特权")


PT = PrivilegeType


class Privilege:
    """一个特权"""

    def __init__(self,
                 title: str,
                 privilege_type: Union[PrivilegeTypeValue, Tuple[PrivilegeTypeValue]],
                 require: Optional[Union["Privilege", Tuple["Privilege"]]] = None,
                 group_tree: Optional[Union[Tuple[str, ...], Tuple[Tuple[str, ...], ...]]] = (),
                 description: str = "",
                 extra: Optional[Union[dict, list, tuple]] = None,
                 **kwargs):
        """
        :param title: 中文名
        :param privilege_type: 特权类型，参见PrivilegeType
        :param require: 依赖的权限
        :param group_tree: 分组树，形如：("group-a", "group-b", ...)或者多重树形(("group-a", "group-b"), ...)
        :param description: 描述
        """
        self.name: str = kwargs.get("name", None)  # 特权的唯一标识
        self.title = title
        self.description = description
        self.privilege_type: Tuple["PrivilegeTypeValue"] = tuple()
        self.require: Tuple["Privilege"] = require  # 需要在后面进行依赖处理
        self.extra = extra
        # 单类或者多类树都转为多类树
        if isinstance(group_tree, tuple) and len(group_tree) > 0 and isinstance(group_tree[0], tuple):
            self.group_tree = group_tree
        elif isinstance(group_tree, tuple) and len(group_tree) > 0 and isinstance(group_tree[0], str):
            self.group_tree = (group_tree,)
        elif isinstance(group_tree, tuple) and not group_tree or group_tree is None:
            self.group_tree = ()
        else:
            assert 0

        if isinstance(privilege_type, PrivilegeTypeValue):
            self.privilege_type = (privilege_type,)
        elif isinstance(privilege_type, tuple):
            self.privilege_type = privilege_type
        else:
            assert 0

    def to_dict(self) -> dict:
        deduplicated_names = [f"{self.name}:{'-'.join(i)}" for i in self.group_tree]
        return {
            "title": self.title,
            "name": self.name,
            "deduplicated_names": deduplicated_names,
            "privilege_type": [i.value for i in self.privilege_type],
            "description": self.description
        }

    def __str__(self):
        return f"<Privilege - {self.name}: {self.title}>"


class BasePermissionMeta(LoggerMixin):
    """基础权限基类"""

    @staticmethod
    def _check_require(a_list: Dict[str, Privilege]):
        """
        检查依赖
        :param a_list:
        :return:
        """
        for privilege in a_list.values():
            if not privilege.require:
                privilege.require = ()
            elif isinstance(privilege.require, Privilege):
                privilege.require = (privilege.require,)
            elif isinstance(privilege.require, str):
                privilege.require = (a_list[privilege.require],)
            elif isinstance(privilege.require, (tuple, list)):
                r = []
                for i in privilege.require:
                    if isinstance(i, str):
                        i = a_list[i]
                    elif isinstance(i, Privilege):
                        pass
                    else:
                        assert 0
                    r.append(i)
                privilege.require = tuple(r)

    def __init__(cls, name, bases, attrs: Dict):
        super().__init__(name, bases, attrs)

        # 全部的privilege dict
        cls.ALL_PRIVILEGE_DICT: Dict[str, Privilege] = {}

        for a_name, p in attrs.items():
            if isinstance(p, Privilege):
                p.name = a_name
                cls.ALL_PRIVILEGE_DICT[a_name] = p
        cls._check_require(cls.ALL_PRIVILEGE_DICT)


class BasePermission(metaclass=BasePermissionMeta):
    """基础权限模块"""

    @classmethod
    def all(cls) -> Tuple[Privilege]:
        return tuple(cls.ALL_PRIVILEGE_DICT.values())

    @classmethod
    def all_names(cls) -> Tuple[str]:
        return tuple(cls.ALL_PRIVILEGE_DICT.keys())

    @classmethod
    def get(cls, v: Optional[Union[str, Privilege]]) -> Optional[Privilege]:
        if isinstance(v, Privilege):
            return v
        return cls.ALL_PRIVILEGE_DICT.get(v, None)

    @classmethod
    def generate_tree(cls,
                      privileges: Optional[Union[List["Privilege"], Tuple["Privilege"]]] = None,
                      to_dict: bool = True):
        """
        产生一个用于前端渲染的树
        :param privileges:
        :param to_dict: 是否直接将部门对象转为字典
        :return:
        """

        def generate_name(title: str):
            return f"group-{title}"

        def generate_sub_groups(title: str, parent_group=None):
            """
            :param title:
            :param parent_group:
            :return: sub-group, if-already-existed-in-parent
            """
            if parent_group is not None:
                for i in parent_group["sub"]:
                    if i["deduplicated_name"] == generate_name(title):
                        return i, True
            return {
                       "deduplicated_name": generate_name(title),
                       "title": title,
                       "sub": []
                   }, False

        if not privileges:
            privileges = cls.all()

        root_g, _ = generate_sub_groups("全部权限")

        for p in privileges:
            for i, a_group_tree in enumerate(p.group_tree):
                current_group = root_g
                for group_name in a_group_tree:
                    next_group, already_existed = generate_sub_groups(group_name, current_group)
                    if not already_existed:
                        current_group["sub"].append(next_group)
                    current_group = next_group
                deduplicated_p = {
                    **p.to_dict(),
                    "sub": []
                } if to_dict else p
                deduplicated_p["deduplicated_name"] = deduplicated_p["deduplicated_names"][i]
                current_group["sub"].append(deduplicated_p)
        return root_g
