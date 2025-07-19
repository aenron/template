"""
API v1版本主路由
"""
from fastapi import APIRouter

from app.api.v1.endpoints import users, auth

# 创建API路由器
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"]) 