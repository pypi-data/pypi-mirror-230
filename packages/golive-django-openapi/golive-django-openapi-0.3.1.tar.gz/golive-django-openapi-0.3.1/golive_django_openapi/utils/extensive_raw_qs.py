# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ExtensiveRawQuerySet",
]

from typing import Optional


class ExtensiveRawQuerySet:
    """可扩展的raw查询集"""

    def __init__(self, **kwargs):
        self._init_another_query()

    def _init_another_query(self):
        # 支持分片
        self.offset: Optional[int] = None
        self.limit: Optional[int] = None

    def query(self):
        raise NotImplementedError

    def __iter__(self):
        self._init_another_query()
        return iter(list(self.query()))

    def __getitem__(self, item):
        self.offset = item.start
        self.limit = item.stop - item.start
        return list(self.query())

    def __len__(self):
        self._init_another_query()
        return self.count()

    def count(self):
        # 支持count语句
        raise NotImplementedError
