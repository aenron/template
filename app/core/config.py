"""
应用配置管理
"""
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目基本信息
    PROJECT_NAME: str = "FastAPI接口项目"
    PROJECT_DESCRIPTION: str = "基于FastAPI的高性能RESTful API服务"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥长度"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY长度必须至少32个字符")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """验证数据库URL格式"""
        if not v.startswith(("sqlite://", "postgresql://", "mysql://")):
            raise ValueError("不支持的数据库类型")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings() 