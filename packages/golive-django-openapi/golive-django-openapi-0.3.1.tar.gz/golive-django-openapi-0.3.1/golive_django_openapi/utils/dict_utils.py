# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "unpack_nested_dict"
]

from typing import Dict, DefaultDict, Union, Tuple


def unpack_nested_dict(d: Union[Dict, DefaultDict], n: int = 2):
    """
    解开嵌套的字典
    :param d:
    :param n: 返回的字段数，2表示只返回最外层字典的key-value
    :return:
    """
    assert n >= 2
    if n == 2:
        yield from tuple(d.items())
        return
    for k in d.keys():
        for deeper in unpack_nested_dict(d[k], n - 1):
            yield k, *deeper
