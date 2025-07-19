"""
用户相关的Pydantic模式
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """用户基础模式"""

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

    @validator("username")
    def validate_username(cls, v: str) -> str:
        """验证用户名"""
        if len(v) < 3:
            raise ValueError("用户名长度必须至少3个字符")
        if len(v) > 50:
            raise ValueError("用户名长度不能超过50个字符")
        return v

    @validator("full_name")
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """验证全名"""
        if v is not None and len(v) > 100:
            raise ValueError("全名长度不能超过100个字符")
        return v


class UserCreate(UserBase):
    """创建用户模式"""

    password: str

    @validator("password")
    def validate_password(cls, v: str) -> str:
        """验证密码"""
        if len(v) < 6:
            raise ValueError("密码长度必须至少6个字符")
        return v


class UserUpdate(BaseModel):
    """更新用户模式"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    @validator("username")
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """验证用户名"""
        if v is not None:
            if len(v) < 3:
                raise ValueError("用户名长度必须至少3个字符")
            if len(v) > 50:
                raise ValueError("用户名长度不能超过50个字符")
        return v

    @validator("password")
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """验证密码"""
        if v is not None and len(v) < 6:
            raise ValueError("密码长度必须至少6个字符")
        return v


class UserInDB(UserBase):
    """数据库中的用户模式"""

    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """用户响应模式"""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模式"""

    username: str
    password: str


class Token(BaseModel):
    """访问令牌模式"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """刷新令牌模式"""

    refresh_token: str


class TokenResponse(BaseModel):
    """令牌响应模式"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """令牌数据模式"""

    username: Optional[str] = None
    user_id: Optional[int] = None
