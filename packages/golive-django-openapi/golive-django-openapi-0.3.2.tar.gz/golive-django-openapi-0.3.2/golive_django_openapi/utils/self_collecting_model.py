# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "SelfCollectingModel",
    "StaticSelfCollectingModel",
    "SelfCollectingModelMeta"
]

import os
import copy
import importlib
from glob import glob
from pathlib import Path
from typing import Union, Callable, List, Optional, Type, Tuple


class SelfCollectingModelMeta(type):

    def __init__(cls, name, bases, attrs):

        # 是否需要被父类收集
        need_collect: bool = attrs.get("NEED_COLLECT", True)

        super().__init__(name, bases, attrs)

        # 记录父类的引用
        # TODO 实际只会记录最后一个父类
        cls.BASE_CLASS = None
        if bases:
            cls.BASE_CLASS = bases[-1]

        # 把当前类存入全部子类的list中
        # TODO 暂时不支持ALL_SUB_CLASSES的重载
        # 重载ALL_SUB_CLASSES后的子类将无法传递给上层的父类
        if cls.ALL_SUB_CLASSES is not None \
                and isinstance(cls.ALL_SUB_CLASSES, list):
            if cls not in cls.ALL_SUB_CLASSES:
                cls.ALL_SUB_CLASSES.append(cls)

        # 最后运行meta method对类进行一些后续的操作
        meta_method = getattr(cls, "meta_method", None)
        if meta_method:
            meta_method(cls)

        if need_collect and cls.BASE_CLASS:
            cls.collecting(cls.BASE_CLASS, cls)

    def __str__(cls):
        s = cls.BASE_CLASS.__doc__
        return f"<{s} '{cls.__module__}.{cls.__name__}'>"


class StaticSelfCollectingModel:
    """子类自收集模型"""

    # 需要索引的路径
    # TODO 路径必须是绝对路径
    PATH_TO_IMPORT: Union[str, List[str], Callable] = None

    # 执行import时文件相对路径的前缀
    RELATIVE_IMPORT_TOP_PATH_PREFIX: str = None

    # 收集到的子类
    # TODO 使用@cls.need_collect()去收集需要的子类
    COLLECTED: [Type["SelfCollectingModel"]] = []

    # 全部子类
    # TODO 这个地方需要放一个全局list的引用，用以存放全部子类，如果为None则不会收集
    # 请注意这个和COLLECTED的区别，COLLECTED是收集业务所需的子类，这个是误差别的记录全部子类
    # TODO 虽然这个和COLLECTED无关，但如果不运行cls.collect仍然会影响ALL_SUB_CLASSES内的子类
    ALL_SUB_CLASSES = None

    # 一个预处理的函数，仅接受一个参数，即正在初始化的类
    meta_method: Optional[Callable] = None

    # 如果一个模块import失败，是否继续import下一个模块而不抛出异常
    FAIL_CONTINUE: bool = False

    # 依赖
    REQUIRE: Tuple = None

    @classmethod
    def __repr__(cls):
        return f"<{cls.__doc__}>"

    @classmethod
    def echo(cls, *args, **kwargs):
        echo = getattr(getattr(cls, "logger", None), "info", None)
        if not echo:
            echo = print
        return echo(*args, **kwargs)

    def collecting(cls, model):
        """
        :param cls: 父类
        :param model: 子类
        """
        assert issubclass(model, cls)
        if model not in cls.COLLECTED and model != cls:
            cls.COLLECTED.append(model)

    @classmethod
    def process(cls, collected=None, **kwargs):
        if not collected:
            collected = cls.COLLECTED
        proceed = []
        all_run = lambda x: all([id(ii) in proceed for ii in x.REQUIRE])
        runnable = lambda x: x.process is not cls.process or collected is not cls.COLLECTED
        to_process = copy.copy(collected)
        while to_process:
            i = to_process.pop(0)
            id_of_i = id(i)
            if id_of_i in proceed:
                continue
            if all_run(i) and runnable(i):
                cls.echo(f"{cls}: processing {i} ...")
                i.process(collected, **kwargs)
                proceed.append(id_of_i)
            else:
                to_process.append(i)

    @classmethod
    def need_collect(cls):
        """装饰需要收集的子类"""
        # TODO 这个方法仅用于静态收集，如果是动态收集的model，不需要调用本方法

        def inner(model):
            # 只能检测子类，并不能检测直接子类
            assert issubclass(model, cls)
            if model not in cls.COLLECTED:
                cls.COLLECTED.append(model)
            return model

        return inner

    @classmethod
    def collect(cls):
        """通过文件目录路径，import相应的module"""
        cls.echo(f"collecting modules for {cls} ...")
        if callable(cls.PATH_TO_IMPORT):
            dirs = cls.PATH_TO_IMPORT()
        else:
            dirs = cls.PATH_TO_IMPORT
        if isinstance(dirs, str):
            dirs = [dirs]
        elif isinstance(dirs, (tuple, list)):
            pass
        else:
            assert 0
        module_dirs = []
        for the_dir in dirs:
            module_dirs += glob(
                str(Path(the_dir) / "**.py"),
                recursive=True
            )
            module_dirs += glob(
                str(Path(the_dir) / f"**{os.sep}**.py"),
                recursive=True
            )
        for module_dir in module_dirs:
            relative_path = module_dir[len(cls.RELATIVE_IMPORT_TOP_PATH_PREFIX):]
            if "-" in relative_path:
                continue
            py_file_dot_split = [i for i in relative_path.split(os.sep) if i]
            py_file_path_for_importing = ".".join(py_file_dot_split)[:-3]
            try:
                importlib.import_module(f"{py_file_path_for_importing}")
            except Exception as e:
                cls.echo(f"!!!FAILED TO IMPORT {py_file_path_for_importing}!!!: {e}")
                if not cls.FAIL_CONTINUE:
                    raise e
        cls.resolve_requirement()

    @classmethod
    def resolve_requirement(cls):

        def _rr(s):
            if isinstance(s, str):
                module_name = ".".join(s.split(".")[:-1])
                class_name = s.split(".")[-1]
                s = getattr(importlib.import_module(module_name), class_name)
            elif callable(s) and not issubclass(s, cls):
                s = s()
            elif s and issubclass(s, cls):
                pass
            else:
                assert 0
            return s

        # 把依赖处理为(,...)
        for i in cls.COLLECTED:
            r = i.REQUIRE
            if not r:
                r = ()
            elif isinstance(r, (tuple, list)):
                r = tuple([_rr(ii) for ii in r])
            else:
                r = (_rr(r),)
            i.REQUIRE = r


class SelfCollectingModel(StaticSelfCollectingModel, metaclass=SelfCollectingModelMeta):

    pass
