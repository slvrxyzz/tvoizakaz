from __future__ import annotations

import json
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import CareerResultORM, UserORM
from src.infrastructure.services.content_service import ContentService


class CareerGuidanceService:
    """Выдаёт рекомендации по профессиям и контенту на основе результатов тестов."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.content_service = ContentService(session)

    async def recommend_for_user(self, user_id: int) -> Dict[str, List[Dict]]:
        user = await self.session.get(UserORM, user_id)
        if not user:
            raise ValueError("User not found")

        stmt = (
            select(CareerResultORM)
            .where(CareerResultORM.user_id == user_id)
            .order_by(CareerResultORM.created_at.desc())
            .limit(1)
        )
        result_row = await self.session.execute(stmt)
        latest_result = result_row.scalar_one_or_none()

        if not latest_result:
            return {"profile": None, "recommendations": [], "content": []}

        recommendations = json.loads(latest_result.recommendations or "[]")

        content_results = await self.content_service.get_content_list(
            content_type=None,
            status="published",
            search=latest_result.profile,
            page=1,
            page_size=5,
            only_published=True,
        )

        return {
            "profile": latest_result.profile,
            "recommendations": recommendations,
            "content": content_results["content"],
        }



