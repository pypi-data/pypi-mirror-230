# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "import_next_step_modules",
]

import os
import importlib.util
from pathlib import Path
from glob import glob

from django.conf import settings


def import_next_step_modules(current_locals: dict, module_file):
    """
    导入当前包的下层包
    本方法应当在__init__.py的最后运行
    :param current_locals: 当前包的locals()
    :param module_file: __file__
    :return:
    """
    current_path = str(Path(module_file).resolve().parent)
    _, current_path_short = os.path.split(current_path)
    _, ext = os.path.splitext(current_path)
    if ext and current_path_short.lower() != "__init__.py":
        return
    for filename in glob(str(Path(current_path) / "*")):
        _, short_filename = os.path.split(filename)
        short_filename_without_ext, _ = os.path.splitext(short_filename)
        if short_filename_without_ext.lower() in ("__pycache__", "__init__"):
            continue
        try:
            relative_path = filename[len(settings.BASE_DIR):]
            relative_path, _ = os.path.splitext(relative_path)
            py_file_dot_split = [i for i in relative_path.split(os.sep) if i]
            py_file_path_for_importing = ".".join(py_file_dot_split)
            current_locals[short_filename_without_ext] = importlib.import_module(f"{py_file_path_for_importing}")
        except:
            pass
