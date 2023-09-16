import traceback

from starlette.responses import JSONResponse
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from eai_commons.error.errors import ErrorCodeException, INTERNAL_ERROR


async def err_code_exception_handler(exp: ErrorCodeException):
    """BizException异常处理器"""
    return JSONResponse(
        status_code=exp.code,
        content=exp.error.to_error_body(),
        media_type=JSONResponse.media_type,
    )


async def validation_exception_handler(exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


async def global_exception_handler(exp: Exception):
    if isinstance(exp, ErrorCodeException):
        return await err_code_exception_handler(exp)

    print(traceback.format_exc())
    err_ = ErrorCodeException(code=500, error=INTERNAL_ERROR)
    return JSONResponse(
        status_code=err_.code,
        content=err_.error.to_error_body(),
        media_type=JSONResponse.media_type,
    )


def add_error_handlers(app: FastAPI):
    """
    在创建fast api的app后，可以加上该handler，可以将错误以json格式输出。
    输出json如：
        ``
        {
            "error": {
                "code": "InternalError",
                "message": "内部错误，请联系管理员",
                "details": null
        }
        ``

    Example:
        ``
        from fastapi import FastAPI
        from eai_commons.error.exception_handler import add_error_handlers

        app = FastAPI()
        add_error_handlers(app)
        ``

        ...
    """

    app.add_exception_handler(ErrorCodeException, err_code_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
