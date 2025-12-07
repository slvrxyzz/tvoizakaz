from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import OrderORM, UserORM


class RatingService:
    """Сервисы формирования рейтингов и статистики."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def earnings_leaderboard(
        self, period: str = "month", limit: int = 10
    ) -> List[dict]:
        condition = [OrderORM.status == "CLOSE"]
        start_date = _period_start(period)
        if start_date:
            condition.append(OrderORM.completed_at >= start_date)

        stmt: Select = (
            select(
                UserORM.id,
                UserORM.name,
                UserORM.nickname,
                func.coalesce(func.sum(OrderORM.price), 0).label("total"),
            )
            .join(OrderORM, OrderORM.executor_id == UserORM.id)
            .where(*condition)
            .group_by(UserORM.id)
            .order_by(desc("total"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return [
            {
                "user_id": row.id,
                "name": row.name,
                "nickname": row.nickname,
                "value": float(row.total or 0),
            }
            for row in result.fetchall()
        ]

    async def tasks_leaderboard(
        self, period: str = "month", limit: int = 10
    ) -> List[dict]:
        condition = [OrderORM.status == "CLOSE"]
        start_date = _period_start(period)
        if start_date:
            condition.append(OrderORM.completed_at >= start_date)

        stmt: Select = (
            select(
                UserORM.id,
                UserORM.name,
                UserORM.nickname,
                func.count(OrderORM.id).label("tasks"),
            )
            .join(OrderORM, OrderORM.executor_id == UserORM.id)
            .where(*condition)
            .group_by(UserORM.id)
            .order_by(desc("tasks"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return [
            {
                "user_id": row.id,
                "name": row.name,
                "nickname": row.nickname,
                "value": int(row.tasks or 0),
            }
            for row in result.fetchall()
        ]

    async def loyalty_leaderboard(self, limit: int = 10) -> List[dict]:
        condition = [OrderORM.status == "CLOSE"]
        subquery = (
            select(
                OrderORM.executor_id.label("executor_id"),
                OrderORM.customer_id.label("customer_id"),
                func.count(OrderORM.id).label("orders"),
            )
            .where(*condition)
            .group_by(OrderORM.executor_id, OrderORM.customer_id)
            .subquery()
        )

        max_orders = (
            select(
                subquery.c.executor_id,
                func.max(subquery.c.orders).label("orders_with_company"),
            )
            .group_by(subquery.c.executor_id)
            .order_by(desc("orders_with_company"))
            .limit(limit)
            .subquery()
        )

        stmt = (
            select(
                UserORM.id,
                UserORM.name,
                UserORM.nickname,
                max_orders.c.orders_with_company,
            )
            .join(max_orders, max_orders.c.executor_id == UserORM.id)
            .order_by(desc(max_orders.c.orders_with_company))
        )

        result = await self.session.execute(stmt)
        return [
            {
                "user_id": row.id,
                "name": row.name,
                "nickname": row.nickname,
                "value": int(row.orders_with_company or 0),
            }
            for row in result.fetchall()
        ]


def _period_start(period: str) -> Optional[datetime]:
    now = datetime.utcnow()
    if period == "month":
        return now - timedelta(days=30)
    if period == "week":
        return now - timedelta(days=7)
    return None



