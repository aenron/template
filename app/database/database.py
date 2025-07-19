"""
数据库连接和会话管理
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.logging import logger

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,  # 在调试模式下显示SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖注入函数
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        logger.debug("数据库会话已创建")
        yield db
    except Exception as e:
        logger.error("数据库会话异常", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("数据库会话已关闭")


def create_tables() -> None:
    """创建数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error("数据库表创建失败", error=str(e))
        raise


def drop_tables() -> None:
    """删除数据库表"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("数据库表删除成功")
    except Exception as e:
        logger.error("数据库表删除失败", error=str(e))
        raise 