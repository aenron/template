"""
异常处理模块
"""
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


class CustomHTTPException(HTTPException):
    """自定义HTTP异常类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class DatabaseException(CustomHTTPException):
    """数据库操作异常"""
    
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(status_code=500, detail=detail, error_code="DATABASE_ERROR")


class ValidationException(CustomHTTPException):
    """数据验证异常"""
    
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")


class AuthenticationException(CustomHTTPException):
    """认证异常"""
    
    def __init__(self, detail: str = "认证失败"):
        super().__init__(status_code=401, detail=detail, error_code="AUTHENTICATION_ERROR")


class AuthorizationException(CustomHTTPException):
    """授权异常"""
    
    def __init__(self, detail: str = "权限不足"):
        super().__init__(status_code=403, detail=detail, error_code="AUTHORIZATION_ERROR")


class NotFoundException(CustomHTTPException):
    """资源未找到异常"""
    
    def __init__(self, detail: str = "资源未找到"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


async def http_exception_handler(request: Request, exc: CustomHTTPException) -> JSONResponse:
    """自定义HTTP异常处理器"""
    logger.error(
        "HTTP异常",
        status_code=exc.status_code,
        detail=exc.detail,
        error_code=exc.error_code,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code or "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器"""
    logger.error(
        "请求验证失败",
        errors=exc.errors(),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求数据验证失败",
                "details": exc.errors(),
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(
        "未处理的异常",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
            }
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    # 注册自定义异常处理器
    app.add_exception_handler(CustomHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # 处理Starlette的HTTPException
    app.add_exception_handler(
        StarletteHTTPException,
        lambda request, exc: http_exception_handler(
            request,
            CustomHTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
                headers=exc.headers,
            )
        ),
    ) 