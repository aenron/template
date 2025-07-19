"""
JWT认证功能测试
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token, verify_token

client = TestClient(app)


def get_test_db():
    """获取测试数据库会话"""
    # 这里应该使用测试数据库
    from app.database.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    hashed_password = get_password_hash("testpassword")
    user = User(username="testuser", email="test@example.com", hashed_password=hashed_password, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_register_user():
    """测试用户注册"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User",
    }

    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data  # 密码不应该返回


def test_login_user(test_user):
    """测试用户登录"""
    login_data = {"username": "testuser", "password": "testpassword"}

    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_invalid_credentials():
    """测试无效凭据登录"""
    login_data = {"username": "nonexistent", "password": "wrongpassword"}

    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401


def test_get_current_user(test_user):
    """测试获取当前用户"""
    # 先登录获取令牌
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # 使用令牌获取用户信息
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user.username


def test_get_current_user_invalid_token():
    """测试无效令牌获取用户"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


def test_refresh_token(test_user):
    """测试令牌刷新"""
    # 先登录获取令牌
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    refresh_token = login_response.json()["refresh_token"]

    # 刷新令牌
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid():
    """测试无效刷新令牌"""
    refresh_data = {"refresh_token": "invalid_refresh_token"}
    response = client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 401


def test_logout():
    """测试用户登出"""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "登出成功"


def test_protected_endpoint_with_auth(test_user):
    """测试需要认证的端点"""
    # 先登录获取令牌
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # 访问需要认证的端点
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200


def test_protected_endpoint_without_auth():
    """测试未认证访问受保护端点"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 401


def test_superuser_endpoint(test_user):
    """测试超级用户端点"""
    # 先登录获取令牌
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # 尝试访问超级用户端点（普通用户应该被拒绝）
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/users/", json={}, headers=headers)
    assert response.status_code == 403
