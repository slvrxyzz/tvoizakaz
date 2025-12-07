#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API эндпоинты для работы с избранными заказами
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.domain.entity.userentity import UserPrivate
from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.favorite_service import FavoriteService
from src.presentation.api.v1.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# Pydantic модели
class FavoriteResponse(BaseModel):
    id: int
    order_id: int
    title: str
    description: str
    price: float
    currency: str
    term: int
    status: str
    priority: str
    responses: int
    created_at: datetime
    customer_id: int
    category_id: int
    category_name: str
    customer_name: str
    customer_nickname: str
    favorited_at: datetime

class FavoritesListResponse(BaseModel):
    favorites: List[FavoriteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class FavoriteStatusResponse(BaseModel):
    is_favorite: bool
    favorite_count: int

@router.post("/orders/{order_id}")
@router.post("/{order_id}")
async def add_to_favorites(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    """Добавить заказ в избранное"""
    async with AsyncSessionLocal() as session:
        favorite_service = FavoriteService(session)
        
        try:
            favorite = await favorite_service.add_to_favorites(current_user.id, order_id)
            return {
                "success": True,
                "message": "Заказ добавлен в избранное",
                "favorite_id": favorite.id
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Ошибка при добавлении в избранное")

@router.delete("/orders/{order_id}")
@router.delete("/{order_id}")
async def remove_from_favorites(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    """Удалить заказ из избранного"""
    async with AsyncSessionLocal() as session:
        favorite_service = FavoriteService(session)
        
        success = await favorite_service.remove_from_favorites(current_user.id, order_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Заказ не найден в избранном")
        
        return {
            "success": True,
            "message": "Заказ удален из избранного"
        }

@router.get("/orders", response_model=FavoritesListResponse)
@router.get("/", response_model=FavoritesListResponse)
async def get_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    limit: Optional[int] = Query(None, ge=1, le=100),
    current_user: UserPrivate = Depends(get_current_user)
):
    """Получить список избранных заказов"""
    async with AsyncSessionLocal() as session:
        favorite_service = FavoriteService(session)

        page_limit = limit or page_size
        
        result = await favorite_service.get_user_favorites(
            current_user.id, page, page_limit
        )
        
        return FavoritesListResponse(**result)

@router.get("/orders/{order_id}/status", response_model=FavoriteStatusResponse)
@router.get("/{order_id}/status", response_model=FavoriteStatusResponse)
async def get_favorite_status(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    """Проверить статус избранного для заказа"""
    async with AsyncSessionLocal() as session:
        favorite_service = FavoriteService(session)
        
        is_favorite = await favorite_service.is_favorite(current_user.id, order_id)
        favorite_count = await favorite_service.get_favorite_count(current_user.id)
        
        return FavoriteStatusResponse(
            is_favorite=is_favorite,
            favorite_count=favorite_count
        )

@router.get("/count")
async def get_favorite_count(
    current_user: UserPrivate = Depends(get_current_user)
):
    """Получить количество избранных заказов"""
    async with AsyncSessionLocal() as session:
        favorite_service = FavoriteService(session)
        
        count = await favorite_service.get_favorite_count(current_user.id)
        
        return {
            "favorite_count": count
        }
