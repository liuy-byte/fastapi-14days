"""Day 3: 请求体 + Pydantic 模型"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_item_with_valid_body():
    """创建商品接口"""
    response = client.post(
        "/products",
        json={
            "name": "无线鼠标",
            "price": 199.0,
            "description": "静音设计",
            "tags": ["外设", "无线"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "无线鼠标"
    assert data["price"] == 199.0
    assert "id" in data


def test_create_item_without_optional_fields():
    """可选字段不传也应该能创建"""
    response = client.post(
        "/products",
        json={"name": "鼠标垫", "price": 29.9},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "鼠标垫"
    assert data["description"] is None


def test_create_item_missing_required_field():
    """缺少必填字段应该被拒绝"""
    response = client.post(
        "/products",
        json={"price": 100.0},
    )
    assert response.status_code == 422


def test_create_item_invalid_price():
    """价格为负数应该被拒绝"""
    response = client.post(
        "/products",
        json={"name": "键盘", "price": -50.0},
    )
    assert response.status_code == 422


def test_create_item_with_nested_images():
    """带嵌套图片列表的商品应该创建成功"""
    response = client.post(
        "/products",
        json={
            "name": "显示器",
            "price": 2999.0,
            "images": [
                {"url": "https://example.com/1.jpg", "alt": "正面"},
                {"url": "https://example.com/2.jpg", "alt": "侧面"},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["images"]) == 2


def test_create_order_with_items():
    """带商品列表的订单"""
    response = client.post(
        "/orders",
        json={
            "customer_name": "张三",
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 3, "quantity": 1},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "张三"
    assert len(data["items"]) == 2
    assert data["total_price"] > 0


def test_create_order_empty_items_rejected():
    """订单商品列表不能为空"""
    response = client.post(
        "/orders",
        json={"customer_name": "李四", "items": []},
    )
    assert response.status_code == 422
