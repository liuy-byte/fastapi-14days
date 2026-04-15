"""Day 6: 错误处理 + 中间件 + CORS"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_custom_exception_handler():
    """自定义异常被全局处理器捕获"""
    response = client.get("/items/999/trigger-not-found")
    assert response.status_code == 404
    data = response.json()
    assert "code" in data
    assert "message" in data


def test_validation_error_returns_unified_format():
    """校验错误返回统一格式"""
    response = client.post("/items", json={"name": "", "price": -1})
    assert response.status_code == 422
    data = response.json()
    assert "code" in data


def test_timing_middleware_adds_header():
    """中间件添加了处理时间 header"""
    response = client.get("/items")
    assert "X-Process-Time" in response.headers


def test_cors_headers_present():
    """CORS 预检请求正常"""
    response = client.options(
        "/items",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in {k.lower() for k in response.headers}


def test_cors_allow_origin_in_response():
    """CORS allow-origin 在响应中"""
    response = client.get("/items", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in {k.lower() for k in response.headers}
