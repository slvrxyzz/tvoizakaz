#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервис для работы с избранными заказами
"""

from typing import Any, Dict

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import CategoryORM, FavoriteOrderORM, OrderORM, UserORM

class FavoriteService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_to_favorites(self, user_id: int, order_id: int) -> FavoriteOrderORM:
        """Добавить заказ в избранное"""
        # Проверяем, не добавлен ли уже заказ в избранное
        existing = await self.session.execute(
            select(FavoriteOrderORM).where(
                and_(
                    FavoriteOrderORM.user_id == user_id,
                    FavoriteOrderORM.order_id == order_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Заказ уже в избранном")
        
        favorite = FavoriteOrderORM(
            user_id=user_id,
            order_id=order_id
        )
        
        self.session.add(favorite)
        await self.session.commit()
        await self.session.refresh(favorite)
        return favorite

    async def remove_from_favorites(self, user_id: int, order_id: int) -> bool:
        """Удалить заказ из избранного"""
        result = await self.session.execute(
            select(FavoriteOrderORM).where(
                and_(
                    FavoriteOrderORM.user_id == user_id,
                    FavoriteOrderORM.order_id == order_id
                )
            )
        )
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            return False
        
        await self.session.delete(favorite)
        await self.session.commit()
        return True

    async def get_user_favorites(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Получить избранные заказы пользователя"""
        offset = (page - 1) * page_size
        
        base_query = (
            select(
                FavoriteOrderORM,
                OrderORM,
                UserORM,
                CategoryORM,
            )
            .join(OrderORM, FavoriteOrderORM.order_id == OrderORM.id)
            .join(UserORM, OrderORM.customer_id == UserORM.id)
            .outerjoin(CategoryORM, OrderORM.category_id == CategoryORM.id)
            .where(FavoriteOrderORM.user_id == user_id)
            .order_by(FavoriteOrderORM.created_at.desc())
        )

        total_result = await self.session.execute(
            select(func.count()).select_from(
                select(FavoriteOrderORM.id)
                .where(FavoriteOrderORM.user_id == user_id)
                .subquery()
            )
        )
        total = total_result.scalar_one() or 0

        result = await self.session.execute(
            base_query.offset(offset).limit(page_size)
        )

        favorites = []
        for favorite, order, customer, category in result:
            favorites.append(
                {
                    "id": favorite.id,
                    "order_id": order.id,
                    "title": order.title,
                    "description": order.description,
                    "price": order.price,
                    "currency": order.currency.value if hasattr(order.currency, "value") else order.currency,
                    "term": order.term,
                    "status": order.status,
                    "priority": order.priority,
                    "responses": order.responses,
                    "created_at": order.created_at,
                    "customer_id": order.customer_id,
                    "category_id": order.category_id,
                    "category_name": category.name if category else "Без категории",
                    "customer_name": customer.name if customer else "",
                    "customer_nickname": customer.nickname if customer else "",
                    "favorited_at": favorite.created_at,
                }
            )

        return {
            "favorites": favorites,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def is_favorite(self, user_id: int, order_id: int) -> bool:
        """Проверить, находится ли заказ в избранном"""
        result = await self.session.execute(
            select(FavoriteOrderORM).where(
                and_(
                    FavoriteOrderORM.user_id == user_id,
                    FavoriteOrderORM.order_id == order_id
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_favorite_count(self, user_id: int) -> int:
        """Получить количество избранных заказов пользователя"""
        result = await self.session.execute(
            select(func.count()).select_from(FavoriteOrderORM).where(
                FavoriteOrderORM.user_id == user_id
            )
        )
        return result.scalar_one() or 0
