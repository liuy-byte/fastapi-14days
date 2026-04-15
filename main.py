from typing import Annotated

from fastapi import FastAPI, Path, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI 14 Days")

# 模拟数据
ITEMS = [
    {"id": i, "name": f"商品{i}", "price": 100 + i, "category": "electronics" if i % 2 == 0 else "books"}
    for i in range(1, 51)
]


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/about")
def about():
    return {"name": "fastapi-14days", "version": "0.1.0", "description": "FastAPI 14 天系统学习"}


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}


# Day 2: 路径参数 + 查询参数


@app.get("/items/{item_id}")
def get_item(item_id: Annotated[int, Path(gt=0, description="商品ID")]):
    """根据 ID 获取指定商品"""
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}


@app.get("/items")
def list_items(
    skip: Annotated[int, Query(ge=0, description="跳过的条数")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="返回条数")] = 10,
    category: str | None = None,
    sort_by: str | None = None,
    order: str | None = "asc",
):
    """分页列表接口，支持筛选和排序"""
    filtered = ITEMS if category is None else [i for i in ITEMS if i["category"] == category]

    if sort_by and sort_by in ("price", "name"):
        filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=(order == "desc"))

    total = len(filtered)
    items = filtered[skip : skip + limit]
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@app.get("/users/{user_id}/profile")
def get_user_profile(
    user_id: Annotated[int, Path(ge=1, description="用户ID")],
):
    """获取用户个人主页"""
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "bio": f"This is user {user_id}'s profile",
    }


# Day 3: 请求体 + Pydantic 模型

PRODUCTS_DB: list[dict] = []
product_id_counter = 0


class Image(BaseModel):
    url: str
    alt: str | None = None


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    price: float = Field(..., gt=0, description="商品价格")
    description: str | None = Field(default=None, description="商品描述")
    tags: list[str] = Field(default_factory=list, description="商品标签")
    images: list[Image] = Field(default_factory=list, description="商品图片")


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str | None
    tags: list[str]
    images: list[Image]


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    items: list[OrderItem] = Field(..., min_length=1)


class Order(BaseModel):
    id: int
    customer_name: str
    items: list[OrderItem]
    total_price: float


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate) -> Product:
    """创建商品"""
    global product_id_counter
    product_id_counter += 1
    item = {"id": product_id_counter, **product.model_dump()}
    PRODUCTS_DB.append(item)
    return Product(**item)


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate) -> Order:
    """创建订单"""
    global product_id_counter
    product_id_counter += 1
    total = 0.0
    for it in order.items:
        total += it.quantity * 100.0
    return Order(
        id=product_id_counter,
        customer_name=order.customer_name,
        items=order.items,
        total_price=total,
    )
