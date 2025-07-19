"""
用户数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    full_name = Column(String(100), nullable=True, comment="全名")
    
    # 密码相关
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级用户")
    
    # 额外信息
    avatar = Column(String(255), nullable=True, comment="头像URL")
    bio = Column(Text, nullable=True, comment="个人简介")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return self.is_active
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "avatar": self.avatar,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        } 