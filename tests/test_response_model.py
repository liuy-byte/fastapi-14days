"""Day 4: 响应模型 + 输入输出分离"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_user_returns_public_fields():
    """注册用户不应该返回密码哈希"""
    response = client.post(
        "/users",
        json={
            "email": "alice@example.com",
            "password": "secret123",
            "full_name": "Alice",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice"
    assert "hashed_password" not in data
    assert "password" not in data


def test_create_user_missing_email():
    """缺少邮箱应该被拒绝"""
    response = client.post(
        "/users",
        json={"password": "secret123"},
    )
    assert response.status_code == 422


def test_create_user_invalid_email():
    """无效邮箱格式应该被拒绝"""
    response = client.post(
        "/users",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert response.status_code == 422


def test_create_user_password_too_short():
    """密码太短应该被拒绝"""
    response = client.post(
        "/users",
        json={"email": "bob@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_get_user_returns_public_fields():
    """获取用户信息不应该返回密码"""
    # 先注册
    client.post(
        "/users",
        json={"email": "charlie@example.com", "password": "securepass"},
    )
    # 再获取
    response = client.get("/users/charlie@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "hashed_password" not in data
    assert "password" not in data


def test_item_create_and_read():
    """创建和读取商品，验证输入输出模型分离"""
    create_resp = client.post(
        "/items",
        json={"name": "机械键盘", "price": 599.0},
    )
    assert create_resp.status_code == 201
    item = create_resp.json()
    assert "id" in item
    assert "created_at" in item

    get_resp = client.get(f"/items/{item['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "机械键盘"


def test_item_update_partial():
    """部分更新商品"""
    # 创建
    create_resp = client.post(
        "/items",
        json={"name": "鼠标", "price": 99.0},
    )
    item = create_resp.json()

    # 部分更新（只改价格）
    update_resp = client.patch(f"/items/{item['id']}", json={"price": 79.0})
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["price"] == 79.0
    assert data["name"] == "鼠标"
