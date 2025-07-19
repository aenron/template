"""
FastAPI 项目启动文件
"""
import uvicorn
from app.main import app
from app.core.config import settings
from app.database.database import create_tables

if __name__ == "__main__":
    # 创建数据库表
    create_tables()
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 