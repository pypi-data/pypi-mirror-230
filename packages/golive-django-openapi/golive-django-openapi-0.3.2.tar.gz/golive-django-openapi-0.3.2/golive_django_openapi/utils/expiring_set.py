# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "ExpiringSet",
]

from apscheduler.schedulers.background import BackgroundScheduler

from .dt_utils import *
from .logger_utils import *


class BaseExpiringSet(metaclass=LoggerMixin):

    def __init__(self, expiring_seconds: int = 3, **kwargs):

        # 过期时间（秒）
        self.expiring_seconds = expiring_seconds

    def add(self, data):
        raise NotImplementedError

    def delete(self, data):
        raise NotImplementedError

    def has(self, data):
        raise NotImplementedError


class ExpiringSet(BaseExpiringSet):
    """一个无redis版本"""

    def __init__(self, clear_interval_hours: int = 1, **kwargs):

        super(ExpiringSet, self).__init__(**kwargs)

        # 数据
        self.data = dict()

        # 定时清理
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.clean, "interval", hours=clear_interval_hours)
        self.scheduler.start()

    def add(self, data: str, only_not_existed: bool = False) -> bool:
        """
        :param data:
        :param only_not_existed: 只有不存在的时候才添加
        :return: bool, 表示最终是否增加了一条数据
        """
        now = arrow.now()
        if only_not_existed and self._has(now, data):
            return False
        self.data[data] = now.datetime.timestamp()
        self.logger.info(f"* added {data} at {self.data[data]}")
        return True

    def delete(self, data: str):
        try:
            del self.data[data]
        except:
            pass

    def _has(self, now, data: str):
        t = self.data.get(data, None)
        return t and now.datetime.timestamp() - t <= self.expiring_seconds

    def has(self, data: str):
        return self._has(arrow.now(), data)

    def all(self) -> set:
        ts_now = arrow.now().datetime.timestamp()
        return {data for data, ts in self.data.items() if ts_now - ts <= self.expiring_seconds}

    def clean(self):
        self.data = dict()

    def stop_clean(self):
        self.scheduler.shutdown()

    def __del__(self):
        self.stop_clean()
