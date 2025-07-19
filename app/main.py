"""
FastAPI 应用主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers

# 设置日志
setup_logging()


# 配置中间件
def setup_middleware():
    """配置应用中间件"""
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


# 设置路由
def setup_routes():
    """设置API路由"""
    app.include_router(api_router, prefix=settings.API_V1_STR)


# Lifespan事件处理器
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    setup_middleware()
    setup_routes()
    setup_exception_handlers(app)
    print(f"🚀 {settings.PROJECT_NAME} 启动成功!")

    yield

    # 关闭时执行
    print(f"👋 {settings.PROJECT_NAME} 正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


# 根路径
@app.get("/")
async def root():
    """根路径接口"""
    return {
        "message": f"欢迎使用 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }
