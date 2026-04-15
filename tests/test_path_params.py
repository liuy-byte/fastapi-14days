"""Day 2: 路径参数 + 查询参数"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_item_by_id_returns_correct_item():
    """根据 ID 获取指定商品"""
    response = client.get("/items/42")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert "name" in data
    assert "price" in data


def test_item_by_invalid_id_type_rejects():
    """传入字符串 ID 应该被拒绝"""
    response = client.get("/items/abc")
    assert response.status_code == 422


def test_items_list_with_default_pagination():
    """默认分页返回前10条"""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "items" in data
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) <= 10


def test_items_list_with_custom_skip_limit():
    """自定义 skip 和 limit"""
    response = client.get("/items?skip=5&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 5
    assert data["limit"] == 20


def test_items_list_limit_capped_at_100():
    """limit 最大只能 100"""
    response = client.get("/items?limit=200")
    assert response.status_code == 422


def test_items_list_skip_must_be_non_negative():
    """skip 不能为负数"""
    response = client.get("/items?skip=-1")
    assert response.status_code == 422


def test_items_list_with_category_filter():
    """按分类筛选"""
    response = client.get("/items?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_user_profile_by_id():
    """根据用户 ID 获取个人主页"""
    response = client.get("/users/123/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 123
    assert "username" in data


def test_user_profile_negative_id_rejected():
    """用户 ID 不能为负数"""
    response = client.get("/users/-1/profile")
    assert response.status_code == 422


def test_items_list_with_sorting():
    """排序参数"""
    response = client.get("/items?sort_by=price&order=asc")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
