"""Day 7: JWT 认证"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_login_success():
    """登录成功返回 JWT"""
    # 先注册
    client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    # 再登录
    response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """密码错误"""
    response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_user_not_found():
    """用户不存在"""
    response = client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "secret123"},
    )
    assert response.status_code == 401


def test_protected_endpoint_with_token():
    """带 token 访问受保护接口"""
    # 先注册
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "password123"},
    )
    # 登录获取 token
    login_resp = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "password123"},
    )
    token = login_resp.json()["access_token"]

    # 用 token 访问
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "bob@example.com"


def test_protected_endpoint_without_token():
    """不带 token 访问受保护接口"""
    response = client.get("/auth/me")
    assert response.status_code == 401
