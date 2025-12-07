from __future__ import annotations

import os
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.domain.entity.userentity import UserPrivate
from src.infrastructure.dependencies import (
    get_portfolio_service,
    get_reward_service,
)
from src.infrastructure.services.portfolio_service import PortfolioService
from src.infrastructure.services.reward_service import RewardService
from src.presentation.api.v1.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

UPLOAD_DIR = os.path.join("assets", "uploads")


class PortfolioItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    media_url: Optional[str]
    attachment_url: Optional[str]
    tags: Optional[str]
    is_featured: bool
    created_at: str

    class Config:
        orm_mode = True


class PortfolioItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    media_url: Optional[str]
    attachment_url: Optional[str]
    tags: Optional[str]
    is_featured: bool = False


class PortfolioItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=2000)
    media_url: Optional[str]
    attachment_url: Optional[str]
    tags: Optional[str]
    is_featured: Optional[bool]


@router.get("/me", response_model=List[PortfolioItemResponse])
async def my_portfolio(
    current_user: UserPrivate = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    items = await portfolio_service.list_by_user(current_user.id)
    return items


@router.get("/users/{user_id}", response_model=List[PortfolioItemResponse])
async def user_portfolio(
    user_id: int,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    return await portfolio_service.list_by_user(user_id)


@router.post("", response_model=PortfolioItemResponse)
async def create_portfolio_item(
    payload: PortfolioItemCreate,
    current_user: UserPrivate = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    item = await portfolio_service.create_item(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        media_url=payload.media_url,
        attachment_url=payload.attachment_url,
        tags=payload.tags,
        is_featured=payload.is_featured,
    )
    return item


@router.put("/{item_id}", response_model=PortfolioItemResponse)
async def update_portfolio_item(
    item_id: int,
    payload: PortfolioItemUpdate,
    current_user: UserPrivate = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    existing = await portfolio_service.get_item(item_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    item = await portfolio_service.update_item(
        item_id,
        title=payload.title,
        description=payload.description,
        media_url=payload.media_url,
        attachment_url=payload.attachment_url,
        tags=payload.tags,
        is_featured=payload.is_featured,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return item


@router.delete("/{item_id}", response_model=dict)
async def delete_portfolio_item(
    item_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    existing = await portfolio_service.get_item(item_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    await portfolio_service.delete_item(item_id)
    return {"success": True}


@router.post("/upload", response_model=dict)
async def upload_portfolio_file(
    file: UploadFile = File(...),
    current_user: UserPrivate = Depends(get_current_user),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    destination = os.path.join(UPLOAD_DIR, safe_name)

    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url = f"/assets/uploads/{safe_name}"
    return {"url": url}


@router.get("/achievements", response_model=dict)
async def achievements_board(
    current_user: UserPrivate = Depends(get_current_user),
    reward_service: RewardService = Depends(get_reward_service),
):
    achievements = await reward_service.get_user_achievements(current_user.id)
    return {
        "items": [
            {
                "id": award.id,
                "title": award.achievement.title if award.achievement else "",
                "description": (
                    award.achievement.description if award.achievement else ""
                ),
                "icon": award.achievement.icon if award.achievement else None,
                "awarded_at": award.awarded_at,
            }
            for award in achievements
        ]
    }


