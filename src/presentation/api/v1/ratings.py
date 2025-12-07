from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.infrastructure.dependencies import get_rating_service
from src.infrastructure.services.rating_service import RatingService

router = APIRouter(prefix="/ratings", tags=["Ratings"])


class LeaderboardEntry(BaseModel):
    user_id: int
    name: str
    nickname: str
    value: float
    rank: int


class LeaderboardResponse(BaseModel):
    type: str
    period: str
    entries: List[LeaderboardEntry]


def _map_entries(raw_entries: List[dict]) -> List[LeaderboardEntry]:
    entries: List[LeaderboardEntry] = []
    for idx, row in enumerate(raw_entries, start=1):
        entries.append(
            LeaderboardEntry(
                user_id=row["user_id"],
                name=row["name"],
                nickname=row["nickname"],
                value=float(row["value"]),
                rank=idx,
            )
        )
    return entries


@router.get("/earnings", response_model=LeaderboardResponse)
async def earnings_leaderboard(
    period: str = Query("month", pattern="^(week|month|all)$"),
    limit: int = Query(10, ge=1, le=50),
    rating_service: RatingService = Depends(get_rating_service),
):
    data = await rating_service.earnings_leaderboard(period=period, limit=limit)
    return LeaderboardResponse(
        type="earnings",
        period=period,
        entries=_map_entries(data),
    )


@router.get("/tasks", response_model=LeaderboardResponse)
async def tasks_leaderboard(
    period: str = Query("month", pattern="^(week|month|all)$"),
    limit: int = Query(10, ge=1, le=50),
    rating_service: RatingService = Depends(get_rating_service),
):
    data = await rating_service.tasks_leaderboard(period=period, limit=limit)
    return LeaderboardResponse(
        type="tasks",
        period=period,
        entries=_map_entries(data),
    )


@router.get("/loyalty", response_model=LeaderboardResponse)
async def loyalty_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    rating_service: RatingService = Depends(get_rating_service),
):
    data = await rating_service.loyalty_leaderboard(limit=limit)
    return LeaderboardResponse(
        type="loyalty",
        period="all",
        entries=_map_entries(data),
    )
