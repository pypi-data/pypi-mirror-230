from __future__ import annotations
from django.http import JsonResponse
from django.utils.translation import gettext as _
from knifes.jsons import JSONEncoder
from typing import Optional
from enum import Enum


class BaseErrorEnum(Enum):
    """
    error code is negative number
    """
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg

    @classmethod
    def get_by_code(cls, code) -> Optional[BaseErrorEnum]:
        return next(filter(lambda x: x.code == code, cls.__members__.values()), None)


class ApiResponse:
    def __init__(self, code, *, msg=None, data=None):
        self.code = code
        self.succ = (code == 200)
        self.msg = msg
        self.data = data

    @classmethod
    def success(cls, data=None):
        return JsonResponse(ApiResponse(200, data=data), encoder=JSONEncoder, safe=False)

    @classmethod
    def failure(cls, msg, code=400):
        return JsonResponse(ApiResponse(code, msg=msg), encoder=JSONEncoder, safe=False)

    @classmethod
    def error(cls, error_enum: BaseErrorEnum):
        return JsonResponse(ApiResponse(error_enum.code, msg=error_enum.msg), encoder=JSONEncoder, safe=False)

    @classmethod
    def missing_param(cls, msg=_('缺少参数')):
        return cls.failure(msg)

    @classmethod
    def unauthorized(cls, msg=_('请先登录')):
        return cls.failure(msg, code=401)

    @classmethod
    def token_invalid(cls, msg=_('请先登录')):  # TODO 废弃
        return cls.failure(msg, code=300)

