from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr, root_validator
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from src.domain.entity.orderentity import CurrencyType, Order

class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    SUPPORT = 'SUPPORT'
    EDITOR = 'EDITOR'
    CUSTOMER = 'CUSTOMER'
    EXECUTOR = 'EXECUTOR'

class UserPrivate(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    nickname: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password_hash: str
    specification: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rub_balance: float = Field(default=0.0, ge=0, description="Баланс в рублях")
    tf_balance: float = Field(default=0.0, ge=0, description="Баланс в TF валюте")
    is_premium: bool = Field(default=False, description="Премиум статус")
    jwt_token: Optional[str] = None
    email_verified: bool = False
    last_login: Optional[datetime] = None
    customer_rating: float = Field(default=0.0, ge=0, le=5)
    executor_rating: float = Field(default=0.0, ge=0, le=5)
    done_count: int = Field(default=0, ge=0)
    taken_count: int = Field(default=0, ge=0)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    phone_verified: bool = False
    admin_verified: bool = False
    role: UserRole = UserRole.CUSTOMER

    @property
    def balance(self) -> float:
        return float(self.rub_balance or 0.0)

    @balance.setter
    def balance(self, value: float) -> None:
        self.rub_balance = float(value or 0.0)

    def get_balance(self, currency: "CurrencyType") -> float:
        if currency == CurrencyType.TF:
            return float(self.tf_balance or 0.0)
        return float(self.rub_balance or 0.0)

    def set_balance(self, currency: "CurrencyType", value: float) -> None:
        amount = float(value or 0.0)
        if currency == CurrencyType.TF:
            self.tf_balance = amount
        else:
            self.rub_balance = amount

class UserExecutor(BaseModel):
    id: int
    name: str
    nickname: str
    specification: str
    description: str
    executor_rating: float
    done_count: int
    is_premium: bool
    created_at: datetime

class UserCustomer(BaseModel):
    id: int
    name: str
    nickname: str
    customer_rating: float
    done_count: int
    is_premium: bool
    created_at: datetime

class UserRegistrationDto(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    nickname: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(min_length=8, max_length=100)
    specification: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=500)
    phone: str = Field(default="", max_length=20)

class UserLoginDto(BaseModel):
    nickname: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class User(UserPrivate):
    """Backward-compatible alias for legacy tests with relaxed requirements."""
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr | None = None
    password_hash: str | None = None
    hashed_password: str | None = None

    @root_validator(pre=True)
    def _legacy_defaults(cls, values: dict) -> dict:
        balance = values.pop("balance", None)
        if balance is not None:
            values.setdefault("rub_balance", balance)
        password_hash = values.get("password_hash") or values.get("hashed_password")
        if password_hash is None:
            values["password_hash"] = ""
            values["hashed_password"] = ""
        else:
            values["password_hash"] = password_hash
            values["hashed_password"] = password_hash
        return values