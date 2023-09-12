# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "safe_issubclass"
]


def safe_issubclass(cls, cls_info):
    """一个不会报错的sisubclass"""
    try:
        return issubclass(cls, cls_info)
    except TypeError:
        return False
