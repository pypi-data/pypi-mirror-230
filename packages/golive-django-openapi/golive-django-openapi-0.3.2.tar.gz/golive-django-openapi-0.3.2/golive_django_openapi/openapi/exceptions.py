# Author: kk.Fang(fkfkbill@gmail.com)

class OpenAPIException(Exception):

    status_code = 500


class APIForbidden(OpenAPIException):
    """禁止操作"""

    status_code = 403


class APIUnauthorized(OpenAPIException):
    """未登录"""

    status_code = 401

    def __init__(self, *args, login_entry: str = "", **kwargs):
        self.login_entry = login_entry


class APIBadRequest(OpenAPIException):
    """请求参数错误"""

    status_code = 400


class APINotFound(OpenAPIException):
    """目标未找到"""

    status_code = 404


class APIServerError(OpenAPIException):
    """服务错误"""

    pass
