"""Day 5: 依赖注入"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_pagination_dependency_uses_default():
    """分页依赖默认参数"""
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 0
    assert data["limit"] == 10


def test_pagination_dependency_custom_params():
    """分页依赖自定义参数"""
    response = client.get("/posts?skip=5&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 5
    assert data["limit"] == 20


def test_authenticated_endpoint_without_token():
    """未带 token 访问需要认证的接口"""
    response = client.get("/posts/me")
    assert response.status_code == 401


def test_authenticated_endpoint_with_valid_token():
    """带有效 token 访问"""
    response = client.get("/posts/me", headers={"Authorization": "Bearer test-token-alice"})
    assert response.status_code == 200
    data = response.json()
    assert data["token"] == "test-token-alice"


def test_authenticated_endpoint_with_invalid_token():
    """带无效 token 访问"""
    response = client.get("/posts/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


def test_yield_dependency_resources_cleaned_up():
    """yield 依赖在请求结束后会清理资源"""
    response = client.get("/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["db_connected"] is True
    assert data["db_closed"] is True


def test_admin_endpoint_requires_superuser():
    """超级用户接口"""
    response = client.get("/admin/dashboard", headers={"Authorization": "Bearer admin-token"})
    assert response.status_code == 200
    assert response.json()["can_access"] is True


def test_admin_endpoint_rejected_for_normal_user():
    """普通用户不能访问管理员接口"""
    response = client.get("/admin/dashboard", headers={"Authorization": "Bearer normal-user-token"})
    assert response.status_code == 403
