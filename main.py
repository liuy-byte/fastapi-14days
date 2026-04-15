"""FastAPI 14 天系统学习 — 主应用文件"""

import time
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, status

from models import (
    Image,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    Order,
    OrderCreate,
    OrderItem,
    Product,
    ProductCreate,
    UserCreate,
    UserPublic,
)

app = FastAPI(title="FastAPI 14 Days")

# ========== Day 1: 基础接口 ==========

ITEMS_OLD = [
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


# ========== Day 2: 路径参数 + 查询参数 ==========

ITEMS_DB: list[dict] = []
item_counter = 10


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """根据 ID 获取指定商品"""
    for item in ITEMS_DB:
        if item["id"] == item_id:
            return ItemResponse(**item)
    for item in ITEMS_OLD:
        if item["id"] == item_id:
            return ItemResponse(id=item["id"], name=item["name"], price=item["price"], created_at=0)
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/items")
def list_items(
    skip: Annotated[int, Query(ge=0, description="跳过的条数")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="返回条数")] = 10,
    category: str | None = None,
    sort_by: str | None = None,
    order: str | None = "asc",
):
    """分页列表接口，支持筛选和排序"""
    filtered = ITEMS_OLD if category is None else [i for i in ITEMS_OLD if i["category"] == category]
    if sort_by and sort_by in ("price", "name"):
        filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"total": len(filtered), "skip": skip, "limit": limit, "items": filtered[skip : skip + limit]}


@app.get("/users/{user_id}/profile")
def get_user_profile(
    user_id: Annotated[int, Path(ge=1, description="用户ID")],
):
    return {"user_id": user_id, "username": f"user_{user_id}", "bio": f"This is user {user_id}'s profile"}


# ========== Day 3: 请求体 + Pydantic 模型 ==========

PRODUCTS_DB: list[dict] = []
product_id_counter = 0


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate) -> Product:
    global product_id_counter
    product_id_counter += 1
    item = {"id": product_id_counter, **product.model_dump()}
    PRODUCTS_DB.append(item)
    return Product(**item)


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate) -> Order:
    global product_id_counter
    product_id_counter += 1
    total = sum(it.quantity * 100.0 for it in order.items)
    return Order(id=product_id_counter, customer_name=order.customer_name, items=order.items, total_price=total)


# ========== Day 4: 响应模型 + 输入输出分离 ==========

USERS_DB: dict[str, dict] = {}


@app.post("/users", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """注册用户——响应不包含密码"""
    USERS_DB[user.email] = {
        "email": user.email,
        "hashed_password": f"hashed_{user.password}",
        "full_name": user.full_name,
    }
    return UserPublic(email=user.email, full_name=user.full_name)


@app.get("/users/{email}", response_model=UserPublic)
def get_user(email: str):
    """获取用户信息——响应不包含密码"""
    if email not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    db_user = USERS_DB[email]
    return UserPublic(email=db_user["email"], full_name=db_user["full_name"])


@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    """创建商品——返回包含 id 和 created_at"""
    global item_counter
    item_counter += 1
    new_item = {"id": item_counter, "name": item.name, "price": item.price, "created_at": time.time()}
    ITEMS_DB.append(new_item)
    return ItemResponse(**new_item)


@app.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate):
    """部分更新商品"""
    for item in ITEMS_DB:
        if item["id"] == item_id:
            item.update(item_update.model_dump(exclude_unset=True))
            return ItemResponse(**item)
    raise HTTPException(status_code=404, detail="Item not found")
