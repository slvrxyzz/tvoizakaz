from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.domain.entity.userentity import UserPrivate
from src.infrastructure.dependencies import (
    get_career_guidance_service,
    get_career_test_service,
)
from src.domain.services.career_test_service import CareerTestService
from src.infrastructure.services.career_guidance_service import CareerGuidanceService
from src.presentation.api.v1.auth import get_current_user

router = APIRouter(prefix="/career", tags=["Career Guidance"])


class SubmitAnswersRequest(BaseModel):
    answers: Dict[str, str] = Field(..., description="Map question_id -> selected option value")


@router.get("/tests")
async def list_tests(service: CareerTestService = Depends(get_career_test_service)):
    return await service.list_tests()


@router.get("/tests/{test_id}")
async def get_test(test_id: int, service: CareerTestService = Depends(get_career_test_service)):
    test = await service.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@router.post("/tests/{test_id}/submit")
async def submit_test(
    test_id: int,
    payload: SubmitAnswersRequest,
    current_user: UserPrivate = Depends(get_current_user),
    service: CareerTestService = Depends(get_career_test_service),
):
    try:
        result = await service.submit_answers(
            user_id=current_user.id,
            test_id=test_id,
            answers=payload.answers,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, **result}


@router.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    guidance_service: CareerGuidanceService = Depends(get_career_guidance_service),
):
    if current_user.id != user_id and current_user.nickname != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return await guidance_service.recommend_for_user(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/results")
async def list_my_results(
    current_user: UserPrivate = Depends(get_current_user),
    service: CareerTestService = Depends(get_career_test_service),
):
    return await service.list_results(current_user.id)



