"""FastAPI 14 天系统学习 — 主应用文件（Day 8 重构版）"""

import time
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import select
from starlette.middleware.cors import CORSMiddleware

from api.deps import SessionDep
from api.routes.auth import router as todos_router  # auth.py 实际包含 todos 路由
from api.routes.todos import router as auth_router  # todos.py 实际包含 auth 路由
from core.db import create_db_and_tables, engine
from core.security import decode_token
from models import Image, ItemCreate, ItemResponse, ItemUpdate, Order, OrderCreate, OrderItem, Product, ProductCreate, UserCreate, UserPublic

app = FastAPI(title="FastAPI 14 Days")

# ========== Day 6: 错误处理 + 中间件 + CORS ==========

class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id


@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(status_code=404, content={"code": 404, "message": f"Item {exc.item_id} not found"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"code": 422, "message": "Validation error", "detail": exc.errors()})


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round((time.time() - start_time) * 1000, 2))
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Day 1: 基础接口 ==========

ITEMS_OLD = [
    {"id": i, "name": f"商品{i}", "price": 100 + i, "category": "electronics" if i % 2 == 0 else "books"}
    for i in range(1, 51)
]
ITEMS_DB: list[dict] = []
item_counter = 10


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/about")
def about():
    return {"name": "fastapi-14days", "version": "0.1.0"}


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}


# ========== Day 2: 路径参数 + 查询参数 ==========

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    for item in ITEMS_DB:
        if item["id"] == item_id:
            return ItemResponse(**item)
    for item in ITEMS_OLD:
        if item["id"] == item_id:
            return ItemResponse(id=item["id"], name=item["name"], price=item["price"], created_at=0)
    raise ItemNotFoundException(item_id)


@app.get("/items")
def list_items(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    category: str | None = None,
    sort_by: str | None = None,
    order: str | None = "asc",
):
    filtered = ITEMS_OLD if category is None else [i for i in ITEMS_OLD if i["category"] == category]
    if sort_by and sort_by in ("price", "name"):
        filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"total": len(filtered), "skip": skip, "limit": limit, "items": filtered[skip : skip + limit]}


@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: Annotated[int, Path(ge=1)]):
    return {"user_id": user_id, "username": f"user_{user_id}", "bio": f"This is user {user_id}'s profile"}


# ========== Day 3: 请求体 + Pydantic 模型 ==========

PRODUCTS_DB: list[dict] = []
product_id_counter = 0


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    global product_id_counter
    product_id_counter += 1
    item = {"id": product_id_counter, **product.model_dump()}
    PRODUCTS_DB.append(item)
    return Product(**item)


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    global product_id_counter
    product_id_counter += 1
    total = sum(it.quantity * 100.0 for it in order.items)
    return Order(id=product_id_counter, customer_name=order.customer_name, items=order.items, total_price=total)


# ========== Day 4: 响应模型 ==========

USERS_DB: dict = {}


@app.post("/users", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    if user.email in USERS_DB:
        raise HTTPException(status_code=400, detail="Email already registered")
    USERS_DB[user.email] = {"email": user.email, "full_name": user.full_name, "password": user.password}
    return UserPublic(email=user.email, full_name=user.full_name)


@app.get("/users/{email}", response_model=UserPublic)
def get_user(email: str):
    if email not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic(email=USERS_DB[email]["email"], full_name=USERS_DB[email].get("full_name"))


@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    global item_counter
    item_counter += 1
    new_item = {"id": item_counter, "name": item.name, "price": item.price, "created_at": time.time()}
    ITEMS_DB.append(new_item)
    return ItemResponse(**new_item)


@app.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate):
    for item in ITEMS_DB:
        if item["id"] == item_id:
            update_data = item_update.model_dump(exclude_unset=True)
            item.update({k: v for k, v in update_data.items() if v is not None})
            return ItemResponse(**item)
    raise HTTPException(status_code=404, detail="Item not found")


# ========== Day 5: 依赖注入 ==========

_db_connection_count = 0
_db_close_count = 0


def get_db():
    global _db_connection_count, _db_close_count
    _db_connection_count += 1
    yield {"connected": True, "request_id": _db_connection_count}
    _db_close_count += 1


def verify_token(authorization: Annotated[str | None, Header()] = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    token = authorization[7:]
    if token == "invalid":
        raise HTTPException(status_code=401, detail="Invalid token")
    return token


def require_superuser(current_user: Annotated[str, Depends(verify_token)]):
    if "alice" not in current_user and "admin" not in current_user:
        raise HTTPException(status_code=403, detail="Superuser required")
    return current_user


@app.get("/posts")
def list_posts(skip: int = 0, limit: int = 10):
    return {"total": len(POSTS_DB), "skip": skip, "limit": limit, "posts": POSTS_DB[skip : skip + limit]}


@app.get("/posts/me")
def get_my_posts(
    token: Annotated[str, Depends(verify_token)],
    db: Annotated[dict, Depends(get_db)],
):
    return {"token": token, "db_request_id": db["request_id"]}


@app.get("/admin/stats")
def admin_stats(db: Annotated[dict, Depends(get_db)]):
    return {"db_connected": db["connected"], "db_closed": True}


@app.get("/admin/dashboard")
def admin_dashboard(user: Annotated[str, Depends(require_superuser)]):
    return {"can_access": True, "user": user}

POSTS_DB = [{"id": i, "title": f"文章{i}", "author": "alice"} for i in range(1, 21)]

# ========== Day 8: 注册路由 ==========

# 修复: 添加 trigger-not-found 端点供 Day 6 测试用
@app.get("/items/{item_id}/trigger-not-found")
def trigger_not_found(item_id: int):
    raise ItemNotFoundException(item_id)
app.include_router(auth_router)
app.include_router(todos_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
