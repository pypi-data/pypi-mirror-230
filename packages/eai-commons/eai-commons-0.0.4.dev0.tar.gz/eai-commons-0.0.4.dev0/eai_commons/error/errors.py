from http import HTTPStatus
from typing import Optional, Any
from eai_commons.error.base import Error, ErrorCodeException


class BadRequestException(ErrorCodeException):
    """非法请求异常类"""

    def __init__(self, error: Error, details: Any = None):
        self.error = error
        self.code = HTTPStatus.BAD_REQUEST
        if details is not None:
            self.error.details = details
        super(BadRequestException, self).__init__(
            error, HTTPStatus.BAD_REQUEST, details
        )


class ConflictException(ErrorCodeException):
    """冲突异常类"""

    def __init__(self, error: Error):
        self.error = error
        self.code = HTTPStatus.CONFLICT
        super(ConflictException, self).__init__(error, HTTPStatus.CONFLICT)


class ForbiddenException(ErrorCodeException):
    """禁止访问异常类"""

    def __init__(self, error: Error):
        self.error = error
        self.code = HTTPStatus.FORBIDDEN


class GatewayTimeoutException(ErrorCodeException):
    """网关服务繁忙"""

    def __init__(self, error: Error, details: Any = None):
        self.error = error
        self.code = HTTPStatus.GATEWAY_TIMEOUT
        self.details = details


class InternalServerErrorException(ErrorCodeException):
    """内部错误异常类"""

    def __init__(self, error: Error, details: Any = None):
        self.error = error
        self.code = HTTPStatus.INTERNAL_SERVER_ERROR
        if details is not None:
            self.details = details


class NotFoundException(ErrorCodeException):
    """资源不存在异常类"""

    def __init__(self, error: Error):
        self.error = error
        self.code = HTTPStatus.NOT_FOUND
        super(NotFoundException, self).__init__(error, HTTPStatus.NOT_FOUND)


class RateLimitException(ErrorCodeException):
    """服务繁忙"""

    def __init__(self, error: Error, details: Any = None):
        self.error = error
        self.code = HTTPStatus.TOO_MANY_REQUESTS
        self.details = details


class UnauthorizedException(ErrorCodeException):
    """禁止访问异常类"""

    def __init__(self, error: Error):
        self.error = error
        self.code = HTTPStatus.UNAUTHORIZED


# 具体的异常
ACCESS_DENY_ERROR = Error(code="AccessDenyError", message="请求来源非法，不允许访问")
FORBIDDEN_ERROR = Error(code="Forbidden", message="无权限访问/操作")
INTERNAL_ERROR = Error(code="InternalError", message="内部错误，请联系管理员")
INSUFFICIENT_RESOURCES = Error(code="InsufficientResources", message="资源不足")
LLM_TIMEOUT_EXCEPTION = Error(code="LLMTimeoutException", message="LLM请求超时，请稍后重试")
MAX_REQUESTS_QUOTA_EXCEEDED = Error(
    code="MaxRequestsQuotaExceeded", message="超过最大请求次数限制，请联系管理员"
)

UNAUTHORIZED = Error(code="Unauthorized", message="请求未授权/登录")
