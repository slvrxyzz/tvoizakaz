from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.infrastructure.repositiry.base_repository import Base

# Ensure metadata is reset when module is re-imported in test suites
Base.metadata.clear()


class OrderTypeEnum(str, enum.Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    NEW = "NEW"

class OrderPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class OrderStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    WORK = "WORK"
    REVIEW = "REVIEW"
    CLOSE = "CLOSE"

class CurrencyTypeEnum(str, enum.Enum):
    RUB = "RUB"
    TF = "TF"

class MessageTypeEnum(str, enum.Enum):
    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class UserORM(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    nickname = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    specification = Column(String(200), default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rub_balance = Column(Float, default=0.0)
    tf_balance = Column(Float, default=0.0)
    is_premium = Column(Boolean, default=False)
    is_support = Column(Boolean, default=False)
    is_editor = Column(Boolean, default=False)
    jwt_token = Column(String(500), nullable=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    customer_rating = Column(Float, default=0.0)
    executor_rating = Column(Float, default=0.0)
    done_count = Column(Integer, default=0)
    taken_count = Column(Integer, default=0)
    phone_number = Column(String(20), nullable=True)
    phone_verified = Column(Boolean, default=False)
    admin_verified = Column(Boolean, default=False)
    role = Column(String(20), default="CUSTOMER")
    photo = Column(String(255), nullable=True)

    @property
    def balance(self) -> float:
        value = getattr(self, "rub_balance", 0.0)
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @balance.setter
    def balance(self, value: float) -> None:
        try:
            self.rub_balance = float(value or 0.0)
        except (TypeError, ValueError):
            self.rub_balance = 0.0

    def get_balance(self, currency: "CurrencyTypeEnum") -> float:
        raw = self.tf_balance if currency == CurrencyTypeEnum.TF else self.balance
        try:
            return float(raw or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def set_balance(self, currency: "CurrencyTypeEnum", value: float) -> None:
        target = "tf_balance" if currency == CurrencyTypeEnum.TF else "rub_balance"
        try:
            setattr(self, target, float(value or 0.0))
        except (TypeError, ValueError):
            setattr(self, target, 0.0)

class OrderORM(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    currency = Column(Enum(CurrencyTypeEnum, native_enum=False, length=16), nullable=False, default=CurrencyTypeEnum.RUB)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(OrderStatusEnum, native_enum=False, length=32), default=OrderStatusEnum.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = Column(DateTime, nullable=True)
    category_id = Column(Integer, nullable=True)
    priority = Column(Enum(OrderPriorityEnum, native_enum=False, length=16), default=OrderPriorityEnum.LOW, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    responses = Column(Integer, default=0, nullable=False)
    term = Column(Integer, nullable=False)
    order_type = Column(Enum(OrderTypeEnum, native_enum=False, length=16), nullable=False, default=OrderTypeEnum.REGULAR)
    
    # Relationships
    customer = relationship("UserORM", foreign_keys=[customer_id])
    executor = relationship("UserORM", foreign_keys=[executor_id])

class FavoriteOrderORM(Base):
    __tablename__ = "favorite_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserORM", foreign_keys=[user_id])
    order = relationship("OrderORM", foreign_keys=[order_id])


class ReviewORM(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)
    rate = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = relationship("UserORM", foreign_keys=[sender_id])
    recipient = relationship("UserORM", foreign_keys=[recipient_id])
    order = relationship("OrderORM", foreign_keys=[order_id])


class CommissionSettingsORM(Base):
    __tablename__ = "commission_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    commission_withdraw = Column(Float, default=3.0)
    commission_customer = Column(Float, default=10.0)
    commission_executor = Column(Float, default=5.0)
    commission_post_order = Column(Integer, default=200)
    commission_response_threshold = Column(Integer, default=5000)
    commission_response_percent = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CategoryORM(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContentORM(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    tags = Column(Text, nullable=False, default="[]")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)

    author = relationship("UserORM", backref="content_items")

class ContentLikeORM(Base):
    __tablename__ = "content_likes"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("content_id", "user_id", name="uq_content_likes_user"),)

    content = relationship("ContentORM", backref="likes_rel")
    user = relationship("UserORM")

class ChatORM(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("OrderORM", foreign_keys=[order_id])
    customer = relationship("UserORM", foreign_keys=[customer_id])
    executor = relationship("UserORM", foreign_keys=[executor_id])

class MessageORM(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime, nullable=True)
    message_type = Column(Enum(MessageTypeEnum, native_enum=False, length=16), nullable=False, default=MessageTypeEnum.TEXT)
    file_path = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    chat = relationship("ChatORM", foreign_keys=[chat_id])
    sender = relationship("UserORM", foreign_keys=[sender_id])


class SupportRequestORM(Base):
    __tablename__ = "support_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserORM", foreign_keys=[user_id])


class PortfolioItemORM(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    media_url = Column(String(255), nullable=True)
    attachment_url = Column(String(255), nullable=True)
    tags = Column(String(255), nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserORM", backref="portfolio_items")


class AchievementORM(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50), nullable=True)
    threshold = Column(Integer, nullable=True)

    user_awards = relationship("UserAchievementORM", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievementORM(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)
    context = Column(Text, nullable=True)

    user = relationship("UserORM", foreign_keys=[user_id])
    achievement = relationship("AchievementORM", back_populates="user_awards")

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement_unique"),
    )


class MonthlyRewardORM(Base):
    __tablename__ = "monthly_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(DateTime, nullable=False, index=True)
    reward_type = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False, default=0)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserORM", foreign_keys=[user_id])


class CareerTestORM(Base):
    __tablename__ = "career_tests"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(Text, nullable=False)  # JSON payload
    created_at = Column(DateTime, default=datetime.utcnow)


class CareerResultORM(Base):
    __tablename__ = "career_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("career_tests.id"), nullable=False)
    score = Column(Integer, nullable=False)
    profile = Column(String(100), nullable=False)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserORM", foreign_keys=[user_id])
    test = relationship("CareerTestORM", foreign_keys=[test_id])

