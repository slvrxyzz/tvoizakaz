from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import (
    AchievementORM,
    MonthlyRewardORM,
    UserAchievementORM,
    UserORM,
)


class RewardService:
    """Бизнес-логика системы наград и достижений."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_achievements(self) -> List[AchievementORM]:
        result = await self.session.execute(
            select(AchievementORM).order_by(AchievementORM.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_user_achievements(self, user_id: int) -> List[UserAchievementORM]:
        result = await self.session.execute(
            select(UserAchievementORM)
            .where(UserAchievementORM.user_id == user_id)
            .order_by(UserAchievementORM.awarded_at.desc())
            .options()
        )
        achievements = list(result.scalars().all())
        await self._prefetch_achievements(achievements)
        return achievements

    async def award_achievement(
        self,
        user_id: int,
        code: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        category: Optional[str] = None,
        threshold: Optional[int] = None,
        context: Optional[str] = None,
    ) -> UserAchievementORM:
        user = await self.session.get(UserORM, user_id)
        if not user:
            raise ValueError("User not found")

        achievement = await self._get_or_create_achievement(
            code,
            title=title or code.replace("_", " ").title(),
            description=description,
            icon=icon,
            category=category,
            threshold=threshold,
        )

        existing = await self.session.execute(
            select(UserAchievementORM).where(
                UserAchievementORM.user_id == user_id,
                UserAchievementORM.achievement_id == achievement.id,
            )
        )
        if existing.scalar_one_or_none():
            # уже выдано — возвращаем существующую запись
            return existing.scalar_one()

        award = UserAchievementORM(
            user_id=user_id,
            achievement_id=achievement.id,
            context=context,
        )
        self.session.add(award)
        await self.session.commit()
        await self.session.refresh(award)
        return award

    async def record_monthly_reward(
        self,
        user_id: int,
        reward_type: str,
        *,
        points: int,
        reason: Optional[str] = None,
        month: Optional[datetime] = None,
    ) -> MonthlyRewardORM:
        user = await self.session.get(UserORM, user_id)
        if not user:
            raise ValueError("User not found")

        period = _normalize_month(month or datetime.utcnow())

        reward = MonthlyRewardORM(
            user_id=user_id,
            reward_type=reward_type,
            points=points,
            reason=reason,
            month=period,
        )
        self.session.add(reward)
        await self.session.commit()
        await self.session.refresh(reward)
        return reward

    async def top_authors_for_month(self, month: datetime, limit: int = 10):
        """Вспомогательный метод — возвращает пользователей по сумме поинтов за месяц."""
        period = _normalize_month(month)
        stmt: Select = (
            select(MonthlyRewardORM.user_id, MonthlyRewardORM.points)
            .where(MonthlyRewardORM.month == period)
        )
        result = await self.session.execute(stmt)
        totals: dict[int, int] = {}
        for user_id, points in result.fetchall():
            totals[user_id] = totals.get(user_id, 0) + points

        ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)[:limit]
        if not ranked:
            return []

        users = await self.session.execute(
            select(UserORM).where(UserORM.id.in_([user_id for user_id, _ in ranked]))
        )
        users_map = {user.id: user for user in users.scalars().all()}

        return [
            {"user": users_map[user_id], "points": points}
            for user_id, points in ranked
            if user_id in users_map
        ]

    async def _get_or_create_achievement(
        self,
        code: str,
        *,
        title: str,
        description: Optional[str],
        icon: Optional[str],
        category: Optional[str],
        threshold: Optional[int],
    ) -> AchievementORM:
        result = await self.session.execute(
            select(AchievementORM).where(AchievementORM.code == code)
        )
        achievement = result.scalar_one_or_none()
        if achievement:
            return achievement

        achievement = AchievementORM(
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            threshold=threshold,
        )
        self.session.add(achievement)
        await self.session.commit()
        await self.session.refresh(achievement)
        return achievement

    async def _prefetch_achievements(
        self, awards: List[UserAchievementORM]
    ) -> None:
        if not awards:
            return
        achievement_ids = {award.achievement_id for award in awards}
        result = await self.session.execute(
            select(AchievementORM).where(AchievementORM.id.in_(achievement_ids))
        )
        mapping = {achievement.id: achievement for achievement in result.scalars().all()}
        for award in awards:
            award.achievement = mapping.get(award.achievement_id)


def _normalize_month(value: datetime) -> datetime:
    """Приводим дату к первому дню месяца (UTC)."""
    return datetime(value.year, value.month, 1)



