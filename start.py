#!/usr/bin/env python3
"""
FastAPI 项目启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要 Python 3.8 或更高版本")
        sys.exit(1)
    print(f"✅ Python 版本: {sys.version}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ 核心依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)

def setup_environment():
    """设置环境"""
    # 检查.env文件
    if not Path(".env").exists():
        if Path("env.example").exists():
            print("📝 创建 .env 文件...")
            os.system("cp env.example .env")
            print("✅ .env 文件已创建，请根据需要修改配置")
        else:
            print("⚠️  未找到环境配置文件")

def start_server():
    """启动服务器"""
    print("🚀 启动 FastAPI 服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API 文档: http://localhost:8000/docs")
    print("📖 ReDoc 文档: http://localhost:8000/redoc")
    print("💚 健康检查: http://localhost:8000/health")
    print("=" * 50)
    
    try:
        # 使用 uvicorn 启动服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

def main():
    """主函数"""
    print("=" * 50)
    print("🎯 FastAPI 接口项目启动器")
    print("=" * 50)
    
    # 检查环境
    check_python_version()
    check_dependencies()
    setup_environment()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 