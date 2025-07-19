"""
主应用测试
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_docs_available():
    """测试API文档是否可用"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available():
    """测试ReDoc文档是否可用"""
    response = client.get("/redoc")
    assert response.status_code == 200 