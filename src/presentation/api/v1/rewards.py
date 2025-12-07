from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.domain.entity.userentity import UserPrivate, UserRole
from src.infrastructure.dependencies import (
    get_reward_service,
    get_user_service,
)
from src.infrastructure.services.reward_service import RewardService
from src.infrastructure.services.user_service import UserService
from src.presentation.api.v1.auth import get_admin_user, get_current_user, get_optional_user

router = APIRouter(prefix="/rewards", tags=["Rewards"])


class AchievementSchema(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str]
    icon: Optional[str]
    category: Optional[str]
    threshold: Optional[int]

    class Config:
        orm_mode = True


class UserAchievementSchema(BaseModel):
    id: int
    awarded_at: datetime
    context: Optional[str]
    achievement: AchievementSchema

    class Config:
        orm_mode = True


class AwardAchievementRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    code: str = Field(..., min_length=3, max_length=64)
    title: Optional[str] = Field(None, max_length=150)
    description: Optional[str]
    icon: Optional[str]
    category: Optional[str]
    threshold: Optional[int]
    context: Optional[str]


class MonthlyRewardRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    reward_type: str = Field(..., min_length=3, max_length=50)
    points: int = Field(..., ge=0)
    reason: Optional[str]
    month: Optional[datetime]


@router.get("/achievements", response_model=List[AchievementSchema])
async def list_achievements(
    reward_service: RewardService = Depends(get_reward_service),
):
    return await reward_service.list_achievements()


@router.get("/me", response_model=List[UserAchievementSchema])
async def my_achievements(
    current_user: UserPrivate = Depends(get_current_user),
    reward_service: RewardService = Depends(get_reward_service),
):
    return await reward_service.get_user_achievements(current_user.id)


@router.get("/users/{user_id}", response_model=List[UserAchievementSchema])
async def user_achievements(
    user_id: int,
    current_user: UserPrivate | None = Depends(get_optional_user),
    reward_service: RewardService = Depends(get_reward_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user and current_user.id == user_id:
        pass
    else:
        role_value = None
        if current_user is not None:
            role_attr = getattr(current_user, "role", UserRole.CUSTOMER)
            role_value = role_attr.value if isinstance(role_attr, UserRole) else str(role_attr).upper()
        if current_user is None or role_value != UserRole.ADMIN.value:
            achievements = await reward_service.get_user_achievements(user_id)
            return [
                UserAchievementSchema.from_orm(award).copy(
                    update={"context": None}
                )
                for award in achievements
            ]

    return await reward_service.get_user_achievements(user_id)


@router.post("/award", response_model=UserAchievementSchema)
async def award_achievement(
    payload: AwardAchievementRequest,
    admin_user: UserPrivate = Depends(get_admin_user),
    reward_service: RewardService = Depends(get_reward_service),
):
    award = await reward_service.award_achievement(
        payload.user_id,
        payload.code,
        title=payload.title,
        description=payload.description,
        icon=payload.icon,
        category=payload.category,
        threshold=payload.threshold,
        context=payload.context,
    )
    return award


@router.post("/monthly", response_model=dict)
async def record_monthly_reward(
    payload: MonthlyRewardRequest,
    admin_user: UserPrivate = Depends(get_admin_user),
    reward_service: RewardService = Depends(get_reward_service),
):
    reward = await reward_service.record_monthly_reward(
        user_id=payload.user_id,
        reward_type=payload.reward_type,
        points=payload.points,
        reason=payload.reason,
        month=payload.month,
    )
    return {
        "success": True,
        "reward_id": reward.id,
        "month": reward.month,
    }


@router.get("/leaderboard")
async def monthly_leaderboard(
    month: Optional[str] = Query(None, description="YYYY-MM format"),
    limit: int = Query(10, ge=1, le=50),
    reward_service: RewardService = Depends(get_reward_service),
):
    target_month = (
        datetime.strptime(month, "%Y-%m")
        if month
        else datetime.utcnow()
    )
    results = await reward_service.top_authors_for_month(target_month, limit=limit)
    return [
        {
            "user_id": entry["user"].id,
            "name": entry["user"].name,
            "nickname": entry["user"].nickname,
            "points": entry["points"],
        }
        for entry in results
    ]


