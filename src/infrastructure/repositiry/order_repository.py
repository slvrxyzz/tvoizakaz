from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Union

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.repositories import (
    CurrencyType,
    OrderCreateDto,
    OrderPriority,
    OrderStatus,
    OrderType,
    OrderUpdateDto,
)
from src.infrastructure.repositiry.db_models import FavoriteOrderORM, OrderORM
from src.infrastructure.monitoring.logger import logger


OrderPayload = Union[OrderCreateDto, OrderUpdateDto, Mapping[str, Any]]


class OrderRepository:
    """Репозиторий заказов, синхронизированный с текущими ORM моделями."""

    __ORDER_COLUMNS: Iterable[str] = (
        "title",
        "description",
        "price",
        "currency",
        "term",
        "customer_id",
        "executor_id",
        "status",
        "priority",
        "order_type",
        "responses",
        "deadline",
        "category_id",
        "created_at",
        "updated_at",
        "completed_at",
    )

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Optional[OrderORM]:
        result = await self.session.execute(
            select(OrderORM).where(OrderORM.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: int) -> list[OrderORM]:
        result = await self.session.execute(
            select(OrderORM).where(OrderORM.customer_id == user_id)
        )
        return list(result.scalars().all())

    async def increment_responses(self, order: OrderORM) -> None:
        order.responses = (order.responses or 0) + 1
        await self.session.commit()

    async def add_favorite(self, user_id: int, order_id: int) -> FavoriteOrderORM:
        result = await self.session.execute(
            select(FavoriteOrderORM).where(
                FavoriteOrderORM.user_id == user_id,
                FavoriteOrderORM.order_id == order_id,
            )
        )
        favorite = result.scalar_one_or_none()
        if favorite:
            return favorite

        favorite = FavoriteOrderORM(user_id=user_id, order_id=order_id)
        self.session.add(favorite)
        await self.session.commit()
        await self.session.refresh(favorite)
        return favorite

    async def remove_favorite(self, user_id: int, order_id: int) -> None:
        result = await self.session.execute(
            select(FavoriteOrderORM).where(
                FavoriteOrderORM.user_id == user_id,
                FavoriteOrderORM.order_id == order_id,
            )
        )
        favorite = result.scalar_one_or_none()
        if favorite:
            await self.session.delete(favorite)
            await self.session.commit()

    async def get_favorites(self, user_id: int) -> list[FavoriteOrderORM]:
        result = await self.session.execute(
            select(FavoriteOrderORM).where(FavoriteOrderORM.user_id == user_id)
        )
        return list(result.scalars().all())

    async def is_favorite(self, user_id: int, order_id: int) -> bool:
        result = await self.session.execute(
            select(FavoriteOrderORM).where(
                FavoriteOrderORM.user_id == user_id,
                FavoriteOrderORM.order_id == order_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(self, order_data: OrderPayload) -> OrderORM:
        payload = self._prepare_payload(order_data, is_create=True)
        order = OrderORM(**payload)

        self.session.add(order)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            logger.error("order_create_failed", error=str(exc))
            raise

        await self.session.refresh(order)
        return order

    async def update(self, order_id: int, order_data: OrderPayload) -> Optional[OrderORM]:
        order = await self.get_by_id(order_id)
        if not order:
            return None

        payload = self._prepare_payload(order_data, is_create=False)
        for key, value in payload.items():
            setattr(order, key, value)

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def delete(self, order_id: int) -> bool:
        order = await self.get_by_id(order_id)
        if not order:
            return False

        await self.session.delete(order)
        await self.session.commit()
        return True

    async def get_all(self, limit: int = 50, offset: int = 0) -> list[OrderORM]:
        result = await self.session.execute(
            select(OrderORM).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    def _prepare_payload(
        self, payload: OrderPayload, *, is_create: bool
    ) -> Dict[str, Any]:
        if isinstance(payload, (OrderCreateDto, OrderUpdateDto)):
            raw = payload.dict(exclude_unset=True)
        else:
            raw = dict(payload)

        normalized: Dict[str, Any] = {}
        for key, value in raw.items():
            if value is None:
                continue
            if key not in self.__ORDER_COLUMNS:
                # В DTO присутствуют служебные поля (например, category_name) — игнорируем.
                continue
            if isinstance(value, (OrderPriority, OrderStatus, OrderType, CurrencyType)):
                normalized[key] = value.value
            else:
                normalized[key] = value

        if is_create:
            normalized.setdefault("status", OrderStatus.OPEN.value)
            normalized.setdefault("responses", 0)

        return normalized