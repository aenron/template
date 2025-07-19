"""
认证相关API端点
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, Token, TokenRefresh, TokenResponse, UserResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AuthenticationException
from app.core.security import create_access_token, create_refresh_token, verify_token, get_password_hash
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    authenticate_user,
    get_user_by_username,
    get_user_by_email,
)

# 创建路由器
router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    """
    用户登录

    Args:
        form_data: 登录表单数据
        db: 数据库会话

    Returns:
        访问令牌和刷新令牌

    Raises:
        AuthenticationException: 登录失败
    """
    try:
        # 认证用户
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise AuthenticationException("用户名或密码错误")

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()

        # 创建访问令牌和刷新令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.username, access_token_expires)
        refresh_token = create_refresh_token(user.username)

        logger.info(f"用户登录成功，用户名: {user.username}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败，用户名: {form_data.username}, 错误: {str(e)}")
        raise AuthenticationException("登录失败")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    用户注册

    Args:
        user_data: 用户注册数据
        db: 数据库会话

    Returns:
        注册的用户信息

    Raises:
        AuthenticationException: 注册失败
    """
    try:
        # 检查用户名是否已存在
        existing_user = get_user_by_username(user_data.username, db)
        if existing_user:
            raise AuthenticationException("用户名已存在")

        # 检查邮箱是否已存在
        existing_email = get_user_by_email(user_data.email, db)
        if existing_email:
            raise AuthenticationException("邮箱已存在")

        # 加密密码
        hashed_password = get_password_hash(user_data.password)

        # 创建新用户
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            avatar=user_data.avatar,
            bio=user_data.bio,
            hashed_password=hashed_password,
            is_active=True,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"用户注册成功，用户名: {user_data.username}")
        return db_user
    except AuthenticationException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"用户注册失败，用户名: {user_data.username}, 错误: {str(e)}")
        raise AuthenticationException("注册失败")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """
    获取当前用户信息

    Args:
        current_user: 当前活跃用户

    Returns:
        当前用户信息
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: TokenRefresh, db: Session = Depends(get_db)) -> TokenResponse:
    """
    刷新访问令牌

    Args:
        refresh_data: 刷新令牌数据
        db: 数据库会话

    Returns:
        新的访问令牌和刷新令牌

    Raises:
        AuthenticationException: 刷新失败
    """
    try:
        # 验证刷新令牌
        payload = verify_token(refresh_data.refresh_token, "refresh")
        username: str = payload.get("sub")

        if username is None:
            raise AuthenticationException("无效的刷新令牌")

        # 查找用户
        user = get_user_by_username(username, db)
        if user is None or not user.is_active:
            raise AuthenticationException("用户不存在或未激活")

        # 创建新的访问令牌和刷新令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.username, access_token_expires)
        new_refresh_token = create_refresh_token(user.username)

        logger.info(f"令牌刷新成功，用户名: {username}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        raise AuthenticationException("令牌刷新失败")


@router.post("/logout")
async def logout() -> dict:
    """
    用户登出

    Returns:
        登出结果
    """
    # 注意：实际应用中可能需要将令牌加入黑名单
    logger.info("用户登出成功")
    return {"message": "登出成功"}
