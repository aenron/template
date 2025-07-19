"""
安全模块 - JWT认证和密码加密
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import logger

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌

    Args:
        subject: 令牌主题（通常是用户ID或用户名）
        expires_delta: 过期时间增量

    Returns:
        JWT访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"创建访问令牌成功，用户: {subject}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建访问令牌失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="令牌创建失败")


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌

    Args:
        subject: 令牌主题（通常是用户ID或用户名）
        expires_delta: 过期时间增量

    Returns:
        JWT刷新令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 刷新令牌有效期更长，默认7天
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}

    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"创建刷新令牌成功，用户: {subject}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建刷新令牌失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="刷新令牌创建失败")


def verify_token(token: str, token_type: str = "access") -> dict:
    """
    验证JWT令牌

    Args:
        token: JWT令牌
        token_type: 令牌类型 ("access" 或 "refresh")

    Returns:
        解码后的令牌数据

    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # 验证令牌类型
        if payload.get("type") != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌类型无效")

        # 验证主题
        subject: str = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")

        logger.debug(f"令牌验证成功，用户: {subject}")
        return payload

    except JWTError as e:
        logger.warning(f"JWT令牌验证失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")
    except Exception as e:
        logger.error(f"令牌验证异常: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌验证失败")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 加密密码

    Returns:
        密码是否匹配
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密码验证失败: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值

    Args:
        password: 明文密码

    Returns:
        加密后的密码
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"密码加密失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码加密失败")


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    获取令牌过期时间

    Args:
        token: JWT令牌

    Returns:
        过期时间
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """
    检查令牌是否过期

    Args:
        token: JWT令牌

    Returns:
        是否过期
    """
    exp_time = get_token_expiration(token)
    if exp_time is None:
        return True
    return datetime.utcnow() > exp_time
