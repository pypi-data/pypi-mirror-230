# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "JWTException",
    "JWTExpired",
    "DefaultJwt"
]

import uuid

import jwt
from django.conf import settings

from .dt_utils import *
from .ensured_dict import *
from .schema_utils import *


class JWTException(Exception):

    pass


class JWTExpired(JWTException):
    """jwt过期"""

    pass


class DefaultJwt(EnsuredDict):
    """默认的jwt数据结构"""

    # jwt前缀
    JWT_PREFIX = "Bearer "

    # 固定登陆点
    # location_id被配置为固定登陆点，即不会检查redis中登陆点的排他性
    FIXED_LOCATIONS = (
        # 供测试用的固定位置
        (FIXED_LOCATION_PYTEST := "PYTEST"),
        # 企业微信
        (FIXED_LOCATION_WECOM := "WECOM"),
        # 钉钉手机客户端内嵌页面打开
        (FIXED_LOCATION_DINGTALK_MOBILE_INNER := "DINGTALK_MOBILE_INNER"),
    )

    username = EDV()
    timestamp = EDV(lambda: dt_now().timestamp())
    location_id = EDV(lambda: uuid.uuid4().hex)  # 用于标记一个token的id，即只能允许一个token在线

    def to_token(self):
        r = jwt.encode(
            self,
            key=settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        return self.JWT_PREFIX + r

    def from_token(self, token):
        token = token[len(self.JWT_PREFIX):]
        r = jwt.decode(
            token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        self.update(Schema({
            "username": scm_unempty_str,
            "timestamp": scm_num,
            scm_optional("location_id", default=""): scm_str,
        }).validate(r))

    def check(self, reserved_location_id: str = None):
        """
        检查是否过期
        TODO 不会检测username指定的用户是否存在！
        """
        sec = dt_now().timestamp() - self["timestamp"]
        if sec > settings.JWT_EXPIRE_SEC:
            raise JWTExpired
        if isinstance(reserved_location_id, bytes):
            reserved_location_id = reserved_location_id.decode("utf-8")
        if reserved_location_id \
                and self["location_id"] != reserved_location_id \
                and self["location_id"] not in self.FIXED_LOCATIONS \
                and reserved_location_id not in self.FIXED_LOCATIONS:
            raise JWTExpired

    def if_need_renew(self):
        """检查当前是否有必要刷新token"""
        sec = dt_now().timestamp() - self["timestamp"]
        return sec > settings.JWT_RENEW_SEC

    @classmethod
    def generate_jwt(cls, username: str, location_id: str = None) -> "DefaultJwt":
        r = cls()
        r["username"] = username
        if location_id:
            r["location_id"] = location_id
        return r
