from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    OPEN = "OPEN"
    WORK = "WORK"
    REVIEW = "REVIEW"
    CLOSE = "CLOSE"

class OrderPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class OrderType(str, Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    NEW = "NEW"

class CurrencyType(str, Enum):
    RUB = "RUB"
    TF = "TF"

class OrderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=250)
    price: int = Field(..., ge=400, le=400000)
    currency: CurrencyType = Field(default=CurrencyType.RUB)
    term: int = Field(..., ge=1, le=30)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[int] = Field(None, ge=1)
    priority: OrderPriority = Field(default=OrderPriority.NORMAL)
    order_type: OrderType = Field(default=OrderType.REGULAR)

    @model_validator(mode="before")
    def ensure_category_source(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("category") and not values.get("category_id"):
            raise ValueError("category or category_id must be provided")
        return values

class OrderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=250)
    price: Optional[int] = Field(None, ge=400, le=400000)
    term: Optional[int] = Field(None, ge=1, le=30)

class OrderResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    currency: CurrencyType
    term: int
    status: OrderStatus
    priority: OrderPriority
    order_type: OrderType
    responses: int
    created_at: datetime
    customer_id: int
    executor_id: Optional[int] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    customer_name: str
    customer_nickname: str

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class OrderRespond(BaseModel):
    message: str
    price: int
