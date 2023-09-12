# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "CronTriggerEx",
]

from apscheduler.triggers.cron import CronTrigger


class CronTriggerEx(CronTrigger):

    def __eq__(self, other):
        assert isinstance(other, CronTrigger)
        self_dict = {i.name: i for i in self.fields}
        other_dict = {i.name: i for i in other.fields}
        both_keys = set(list(self_dict.keys()) + list(other_dict.keys()))
        for k in both_keys:
            if self_dict.get(k, None) != other_dict.get(k, None):
                return False
        return True
