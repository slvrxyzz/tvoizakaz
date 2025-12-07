from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import CareerResultORM, CareerTestORM, UserORM


@dataclass
class TestQuestion:
    id: str
    text: str
    options: List[Dict[str, Any]]


class CareerTestService:
    """Сервис профориентационных тестов и рекомендаций."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_tests(self) -> List[Dict[str, Any]]:
        stmt = select(CareerTestORM).order_by(CareerTestORM.created_at.asc())
        rows = await self.session.execute(stmt)
        return [self._serialize_test(test, with_questions=False) for test in rows.scalars().all()]

    async def get_test(self, test_id: int) -> Optional[Dict[str, Any]]:
        test = await self.session.get(CareerTestORM, test_id)
        if not test:
            return None
        return self._serialize_test(test, with_questions=True)

    async def submit_answers(
        self,
        *,
        user_id: int,
        test_id: int,
        answers: Dict[str, Any],
    ) -> Dict[str, Any]:
        test = await self.session.get(CareerTestORM, test_id)
        if not test:
            raise ValueError("Test not found")

        user = await self.session.get(UserORM, user_id)
        if not user:
            raise ValueError("User not found")

        questions = json.loads(test.questions)
        score = 0
        matched_profile = "generalist"
        recommendations: List[str] = []

        for question in questions:
            qid = question.get("id")
            if not qid:
                continue
            answer = answers.get(qid)
            options = question.get("options", [])
            matched_option = next((opt for opt in options if opt.get("value") == answer), None)
            if matched_option:
                score += int(matched_option.get("score", 0))
                recommendations.extend(matched_option.get("recommendations", []))
                matched_profile = matched_option.get("profile", matched_profile)

        result = CareerResultORM(
            user_id=user_id,
            test_id=test_id,
            score=score,
            profile=matched_profile,
            recommendations=json.dumps(recommendations),
        )
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)

        return {
            "profile": matched_profile,
            "score": score,
            "recommendations": recommendations,
            "result_id": result.id,
        }

    async def list_results(self, user_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(CareerResultORM, CareerTestORM)
            .join(CareerTestORM, CareerTestORM.id == CareerResultORM.test_id)
            .where(CareerResultORM.user_id == user_id)
            .order_by(CareerResultORM.created_at.desc())
        )
        rows = await self.session.execute(stmt)

        results = []
        for result, test in rows:
            results.append(
                {
                    "id": result.id,
                    "test": self._serialize_test(test, with_questions=False),
                    "profile": result.profile,
                    "score": result.score,
                    "recommendations": json.loads(result.recommendations or "[]"),
                    "created_at": result.created_at,
                }
            )
        return results

    def _serialize_test(self, test: CareerTestORM, *, with_questions: bool) -> Dict[str, Any]:
        payload = {
            "id": test.id,
            "slug": test.slug,
            "title": test.title,
            "description": test.description,
            "created_at": test.created_at,
        }
        if with_questions:
            payload["questions"] = json.loads(test.questions)
        return payload



