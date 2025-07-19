"""
依赖注入模块 - 用户认证和权限验证
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.security import verify_token
from app.core.logging import logger

# OAuth2密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", scheme_name="JWT")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户

    Args:
        db: 数据库会话
        token: JWT访问令牌

    Returns:
        当前用户对象

    Raises:
        HTTPException: 认证失败
    """
    try:
        # 验证令牌
        payload = verify_token(token, "access")
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"获取当前用户成功: {username}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        当前活跃用户

    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        logger.warning(f"用户未激活: {current_user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活")
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前超级用户

    Args:
        current_user: 当前用户

    Returns:
        当前超级用户

    Raises:
        HTTPException: 权限不足
    """
    if not current_user.is_superuser:
        logger.warning(f"权限不足: {current_user.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    获取可选的当前用户（不强制要求认证）

    Args:
        db: 数据库会话
        token: 可选的JWT访问令牌

    Returns:
        当前用户对象或None
    """
    if token is None:
        return None

    try:
        payload = verify_token(token, "access")
        username: str = payload.get("sub")

        if username is None:
            return None

        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.is_active:
            return None

        logger.debug(f"获取可选当前用户成功: {username}")
        return user

    except Exception as e:
        logger.debug(f"获取可选当前用户失败: {str(e)}")
        return None


def get_user_by_username(username: str, db: Session = Depends(get_db)) -> Optional[User]:
    """
    根据用户名获取用户

    Args:
        username: 用户名
        db: 数据库会话

    Returns:
        用户对象或None
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(email: str, db: Session = Depends(get_db)) -> Optional[User]:
    """
    根据邮箱获取用户

    Args:
        email: 邮箱地址
        db: 数据库会话

    Returns:
        用户对象或None
    """
    return db.query(User).filter(User.email == email).first()


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)) -> Optional[User]:
    """
    用户认证

    Args:
        username: 用户名
        password: 密码
        db: 数据库会话

    Returns:
        认证成功的用户对象或None
    """
    from app.core.security import verify_password

    user = get_user_by_username(username, db)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    logger.debug(f"用户认证成功: {username}")
    return user
