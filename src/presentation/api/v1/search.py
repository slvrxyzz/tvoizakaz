from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.repositiry.db_models import UserORM, OrderORM
from sqlalchemy import select, func, or_
from src.presentation.api.v1.auth import get_current_user
from src.domain.entity.userentity import UserPrivate

router = APIRouter(prefix="/search", tags=["Search"])

# Pydantic models
class SearchResult(BaseModel):
    id: int
    title: str
    description: str
    price: int
    status: str
    created_at: datetime
    customer_id: int
    customer_name: str
    customer_nickname: str
    category_id: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int

class UserSearchResult(BaseModel):
    id: int
    name: str
    nickname: str
    specification: str
    description: str
    customer_rating: float
    executor_rating: float
    done_count: int
    taken_count: int

class UserSearchResponse(BaseModel):
    results: List[UserSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/orders", response_model=SearchResponse)
async def search_orders(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Поиск заказов по тексту"""
    async with AsyncSessionLocal() as session:
        # Базовый запрос
        query = select(OrderORM, UserORM).join(
            UserORM, OrderORM.customer_id == UserORM.id
        ).where(
            OrderORM.status == "active"
        )
        
        # Поиск по тексту
        search_filter = or_(
            OrderORM.title.ilike(f"%{q}%"),
            OrderORM.description.ilike(f"%{q}%")
        )
        query = query.where(search_filter)
        
        # Фильтры
        if category_id:
            query = query.where(OrderORM.category_id == category_id)
        
        if min_price is not None:
            query = query.where(OrderORM.price >= min_price)
        
        if max_price is not None:
            query = query.where(OrderORM.price <= max_price)
        
        # Подсчет общего количества
        count_query = select(func.count()).select_from(
            OrderORM.join(UserORM, OrderORM.customer_id == UserORM.id)
        ).where(
            OrderORM.status == "active",
            search_filter
        )
        
        if category_id:
            count_query = count_query.where(OrderORM.category_id == category_id)
        if min_price is not None:
            count_query = count_query.where(OrderORM.price >= min_price)
        if max_price is not None:
            count_query = count_query.where(OrderORM.price <= max_price)
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(OrderORM.created_at.desc())
        
        result = await session.execute(query)
        rows = result.fetchall()
        
        results = []
        for order, customer in rows:
            results.append(SearchResult(
                id=order.id,
                title=order.title,
                description=order.description,
                price=order.price,
                status=order.status,
                created_at=order.created_at,
                customer_id=customer.id,
                customer_name=customer.name,
                customer_nickname=customer.nickname,
                category_id=order.category_id
            ))
        
        total_pages = (total + page_size - 1) // page_size
        
        return SearchResponse(
            results=results,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

@router.get("/users", response_model=UserSearchResponse)
async def search_users(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Поиск пользователей по тексту"""
    async with AsyncSessionLocal() as session:
        # Поиск по тексту
        search_filter = or_(
            UserORM.name.ilike(f"%{q}%"),
            UserORM.nickname.ilike(f"%{q}%"),
            UserORM.specification.ilike(f"%{q}%"),
            UserORM.description.ilike(f"%{q}%")
        )
        
        # Подсчет общего количества
        count_query = select(func.count()).where(search_filter)
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Основной запрос
        query = select(UserORM).where(search_filter)
        
        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(UserORM.created_at.desc())
        
        result = await session.execute(query)
        users = result.scalars().all()
        
        results = []
        for user in users:
            results.append(UserSearchResult(
                id=user.id,
                name=user.name,
                nickname=user.nickname,
                specification=user.specification,
                description=user.description,
                customer_rating=user.customer_rating,
                executor_rating=user.executor_rating,
                done_count=user.done_count,
                taken_count=user.taken_count
            ))
        
        total_pages = (total + page_size - 1) // page_size
        
        return UserSearchResponse(
            results=results,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50)
):
    """Получить предложения для автодополнения"""
    async with AsyncSessionLocal() as session:
        # Поиск по заказам
        orders_query = select(OrderORM.title).where(
            OrderORM.status == "active",
            OrderORM.title.ilike(f"%{q}%")
        ).limit(limit // 2)
        
        orders_result = await session.execute(orders_query)
        order_titles = [row[0] for row in orders_result.fetchall()]
        
        # Поиск по пользователям
        users_query = select(UserORM.nickname).where(
            UserORM.nickname.ilike(f"%{q}%")
        ).limit(limit // 2)
        
        users_result = await session.execute(users_query)
        user_nicknames = [row[0] for row in users_result.fetchall()]
        
        return {
            "suggestions": {
                "orders": order_titles,
                "users": user_nicknames
            }
        }






