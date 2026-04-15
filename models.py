"""Day 3-4: Pydantic 数据模型"""

from pydantic import BaseModel, EmailStr, Field


# Day 3: 请求体模型
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


# Day 4: 响应模型
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class UserPublic(BaseModel):
    email: EmailStr
    full_name: str | None
    model_config = {"from_attributes": True}


class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    full_name: str | None


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price: float | None = Field(default=None, gt=0)


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    created_at: float
