-- 数据库初始化脚本
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建数据库用户（如果需要）
-- CREATE USER fastapi_user WITH PASSWORD 'fastapi_password';

-- 授予权限
-- GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;

-- 设置时区
SET timezone = 'UTC';

-- 创建自定义函数（如果需要）
-- 例如：创建更新时间戳的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 注意：表结构将由SQLAlchemy的Alembic迁移管理
-- 这里可以添加一些初始数据或配置 