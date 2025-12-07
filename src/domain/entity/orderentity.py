from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    WORK = "WORK"
    REVIEW = "REVIEW"
    CLOSE = "CLOSE"


class OrderType(str, Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    NEW = "NEW"


class CurrencyType(str, Enum):
    RUB = "RUB"
    TF = "TF"


class Order(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=250)
    price: int = Field(ge=400, le=400000)
    currency: CurrencyType = CurrencyType.RUB
    customer_id: int
    executor_id: Optional[int] = None
    responses: int = 0
    term: int = Field(ge=1, le=30)
    status: OrderStatus = OrderStatus.OPEN
    priority: OrderPriority = OrderPriority.NORMAL
    order_type: OrderType = OrderType.REGULAR
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CommissionSettingsEntity(BaseModel):
    id: int = 1
    commission_withdraw: float = 3.0
    commission_customer: float = 10.0
    commission_executor: float = 5.0
    commission_post_order: int = 200
    commission_response_threshold: int = 5000
    commission_response_percent: float = 1.0
