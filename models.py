"""Day 3-8: 数据模型（SQLModel）"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Day 3: 请求体模型
class Image(SQLModel):
    url: str
    alt: Optional[str] = None


class ProductCreate(SQLModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    images: list[Image] = Field(default_factory=list)


class Product(SQLModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    tags: list[str]
    images: list[Image]


class OrderItem(SQLModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderCreate(SQLModel):
    customer_name: str = Field(..., min_length=1)
    items: list[OrderItem] = Field(..., min_length=1)


class Order(SQLModel):
    id: int
    customer_name: str
    items: list[OrderItem]
    total_price: float


# Day 4: 响应模型
class UserCreate(SQLModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserPublic(SQLModel):
    email: EmailStr
    full_name: Optional[str]


class UserInDB(SQLModel):
    email: EmailStr
    hashed_password: str
    full_name: Optional[str]


class ItemCreate(SQLModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class ItemUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, gt=0)


class ItemResponse(SQLModel):
    id: int
    name: str
    price: float
    created_at: float


# Day 8: SQLModel 数据库模型
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(SQLModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False


class TodoPublic(SQLModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
