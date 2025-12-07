"""
Интерфейсы репозиториев для Clean Architecture
Enterprise-level repository interfaces
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"
    EDITOR = "EDITOR"
    CUSTOMER = "CUSTOMER"
    EXECUTOR = "EXECUTOR"


class OrderStatus(str, Enum):
    """Статусы заказов (синхронизированы с OrderORM/REST схемами)"""
    OPEN = "OPEN"
    WORK = "WORK"
    REVIEW = "REVIEW"
    CLOSE = "CLOSE"
    ARCHIVED = "ARCHIVED"


class OrderPriority(str, Enum):
    """Приоритеты заказов"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class OrderType(str, Enum):
    """Типы заказов"""
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    NEW = "NEW"


class CurrencyType(str, Enum):
    """Валюты заказа"""
    RUB = "RUB"
    TF = "TF"


# DTOs для передачи данных
class UserCreateDto(BaseModel):
    """DTO для создания пользователя"""
    name: str
    nickname: str
    email: str
    password: str
    role: UserRole = UserRole.CUSTOMER
    phone: Optional[str] = None
    description: Optional[str] = None
    specification: Optional[str] = None


class UserUpdateDto(BaseModel):
    """DTO для обновления пользователя"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    specification: Optional[str] = None
    is_active: Optional[bool] = None


class UserLoginDto(BaseModel):
    """DTO для входа пользователя"""
    identifier: str  # email или nickname
    password: str


class OrderCreateDto(BaseModel):
    """DTO для создания заказа (используется инфраструктурой FastAPI)"""
    title: str
    description: str
    price: int
    currency: CurrencyType = CurrencyType.RUB
    term: int
    customer_id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    priority: OrderPriority = OrderPriority.NORMAL
    order_type: OrderType = OrderType.REGULAR
    deadline: Optional[datetime] = None
    tags: List[str] = []


class OrderUpdateDto(BaseModel):
    """DTO для обновления заказа"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[CurrencyType] = None
    term: Optional[int] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[OrderPriority] = None
    order_type: Optional[OrderType] = None
    status: Optional[OrderStatus] = None
    tags: Optional[List[str]] = None


class OrderFilterDto(BaseModel):
    """DTO для фильтрации заказов"""
    status: Optional[OrderStatus] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    currency: Optional[CurrencyType] = None
    priority: Optional[OrderPriority] = None
    customer_id: Optional[int] = None
    executor_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    tags: Optional[List[str]] = None


# Интерфейсы репозиториев
class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def create(self, user_data: UserCreateDto) -> int:
        """Создание пользователя"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_nickname(self, nickname: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по никнейму"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email"""
        pass
    
    @abstractmethod
    async def get_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email или nickname"""
        pass
    
    @abstractmethod
    async def update(self, user_id: int, user_data: UserUpdateDto) -> bool:
        """Обновление пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Удаление пользователя"""
        pass
    
    @abstractmethod
    async def verify_password(self, user_id: int, password: str) -> bool:
        """Проверка пароля пользователя"""
        pass
    
    @abstractmethod
    async def update_password(self, user_id: int, new_password: str) -> bool:
        """Обновление пароля пользователя"""
        pass
    
    @abstractmethod
    async def get_by_role(self, role: UserRole, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение пользователей по роли"""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Поиск пользователей"""
        pass
    
    @abstractmethod
    async def get_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        pass


class IOrderRepository(ABC):
    """Интерфейс репозитория заказов"""
    
    @abstractmethod
    async def create(self, order_data: OrderCreateDto) -> int:
        """Создание заказа"""
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получение заказа по ID"""
        pass
    
    @abstractmethod
    async def update(self, order_id: int, order_data: OrderUpdateDto) -> bool:
        """Обновление заказа"""
        pass
    
    @abstractmethod
    async def delete(self, order_id: int) -> bool:
        """Удаление заказа"""
        pass
    
    @abstractmethod
    async def get_by_customer(self, customer_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение заказов заказчика"""
        pass
    
    @abstractmethod
    async def get_by_executor(self, executor_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение заказов исполнителя"""
        pass
    
    @abstractmethod
    async def search(self, filters: OrderFilterDto, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Поиск заказов по фильтрам"""
        pass
    
    @abstractmethod
    async def assign_executor(self, order_id: int, executor_id: int) -> bool:
        """Назначение исполнителя на заказ"""
        pass
    
    @abstractmethod
    async def update_status(self, order_id: int, status: OrderStatus) -> bool:
        """Обновление статуса заказа"""
        pass
    
    @abstractmethod
    async def get_popular_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение популярных категорий"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики заказов"""
        pass


class IMessageRepository(ABC):
    """Интерфейс репозитория сообщений"""
    
    @abstractmethod
    async def create(self, chat_id: int, sender_id: int, content: str, message_type: str = "text") -> int:
        """Создание сообщения"""
        pass
    
    @abstractmethod
    async def get_by_chat(self, chat_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение сообщений чата"""
        pass
    
    @abstractmethod
    async def get_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Получение сообщения по ID"""
        pass
    
    @abstractmethod
    async def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """Отметка сообщения как прочитанного"""
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: int) -> int:
        """Получение количества непрочитанных сообщений"""
        pass


class IChatRepository(ABC):
    """Интерфейс репозитория чатов"""
    
    @abstractmethod
    async def create(self, order_id: int, customer_id: int, executor_id: int) -> int:
        """Создание чата"""
        pass
    
    @abstractmethod
    async def get_by_id(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Получение чата по ID"""
        pass
    
    @abstractmethod
    async def get_by_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получение чата по заказу"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение чатов пользователя"""
        pass
    
    @abstractmethod
    async def update_last_activity(self, chat_id: int) -> bool:
        """Обновление времени последней активности"""
        pass


class IReviewRepository(ABC):
    """Интерфейс репозитория отзывов"""
    
    @abstractmethod
    async def create(self, order_id: int, reviewer_id: int, target_id: int, 
                    rating: int, comment: str) -> int:
        """Создание отзыва"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение отзывов о пользователе"""
        pass
    
    @abstractmethod
    async def get_by_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получение отзыва по заказу"""
        pass
    
    @abstractmethod
    async def get_average_rating(self, user_id: int) -> float:
        """Получение среднего рейтинга пользователя"""
        pass
    
    @abstractmethod
    async def get_rating_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики рейтингов"""
        pass







