from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.repositiry.db_models import OrderORM, UserORM, ReviewORM
from sqlalchemy import select, func
from src.presentation.api.v1.auth import get_current_user
from src.domain.entity.userentity import UserPrivate

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Pydantic models
class ReviewCreate(BaseModel):
    rate: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=3, max_length=150)

class ReviewResponse(BaseModel):
    id: int
    type: str
    rate: int
    text: str
    response: Optional[str]
    sender_id: int
    reviewee_id: int  # Соответствует ReviewDTO фронтенда (reviewee_id вместо recipient_id)
    order_id: int
    created_at: datetime
    reviewer_name: Optional[str] = None  # Соответствует ReviewDTO фронтенда
    reviewer_nickname: Optional[str] = None  # Соответствует ReviewDTO фронтенда
    # Для обратной совместимости
    sender_name: Optional[str] = None
    sender_nickname: Optional[str] = None
    recipient_id: Optional[int] = None
    recipient_name: Optional[str] = None
    recipient_nickname: Optional[str] = None

class ReviewUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=3, max_length=150)
    rate: Optional[int] = Field(None, ge=1, le=5)

class ReviewResponseCreate(BaseModel):
    response: str = Field(..., min_length=1, max_length=100)

@router.post("/orders/{order_id}/executor", response_model=ReviewResponse)
async def create_executor_review(
    order_id: int,
    review_data: ReviewCreate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        # Проверяем заказ
        order_result = await session.execute(select(OrderORM).where(OrderORM.id == order_id))
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != 'REVIEW':
            raise HTTPException(status_code=400, detail="Order not in REVIEW status")
        
        customer = await session.execute(select(UserORM).where(UserORM.id == order.customer_id))
        customer = customer.scalar_one_or_none()
        
        executor = await session.execute(select(UserORM).where(UserORM.id == order.executor_id))
        executor = executor.scalar_one_or_none()
        
        if not customer or not executor:
            raise HTTPException(status_code=404, detail="Users not found")
        
        # Проверяем, что текущий пользователь - заказчик
        if current_user.id != customer.id:
            raise HTTPException(status_code=403, detail="Only customer can review executor")
        
        # Создаём отзыв
        review = ReviewORM(
            type='executor',
            rate=review_data.rate,
            text=review_data.text,
            sender_id=customer.id,
            recipient_id=executor.id,
            order_id=order.id
        )
        session.add(review)
        
        # Обновляем рейтинг исполнителя
        all_reviews = await session.execute(
            select(ReviewORM).where(
                ReviewORM.recipient_id == executor.id,
                ReviewORM.type == 'executor'
            )
        )
        all_reviews = all_reviews.scalars().all()
        
        if all_reviews:
            executor.executor_rating = sum(r.rate for r in all_reviews) / len(all_reviews)
        
        # done_count не существует в UserORM, пропускаем
        order.status = 'CLOSE'
        order.completed_at = func.now()
        
        await session.commit()
        await session.refresh(review)
        
        return ReviewResponse(
            id=review.id,
            type=review.type,
            rate=review.rate,
            text=review.text,
            response=review.response,
            sender_id=review.sender_id,
            reviewee_id=review.recipient_id,  # Соответствует ReviewDTO фронтенда
            order_id=review.order_id,
            created_at=review.created_at,
            reviewer_name=customer.name,
            reviewer_nickname=customer.nickname,
            # Для обратной совместимости
            sender_name=customer.name,
            sender_nickname=customer.nickname,
            recipient_id=review.recipient_id,
            recipient_name=executor.name,
            recipient_nickname=executor.nickname
        )

@router.post("/orders/{order_id}/customer", response_model=ReviewResponse)
async def create_customer_review(
    order_id: int,
    review_data: ReviewCreate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        # Проверяем заказ
        order_result = await session.execute(select(OrderORM).where(OrderORM.id == order_id))
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != 'CLOSE':
            raise HTTPException(status_code=400, detail="Order not closed")
        
        executor = await session.execute(select(UserORM).where(UserORM.id == order.executor_id))
        executor = executor.scalar_one_or_none()
        
        customer = await session.execute(select(UserORM).where(UserORM.id == order.customer_id))
        customer = customer.scalar_one_or_none()
        
        if not customer or not executor:
            raise HTTPException(status_code=404, detail="Users not found")
        
        # Проверяем, что текущий пользователь - исполнитель
        if current_user.id != executor.id:
            raise HTTPException(status_code=403, detail="Only executor can review customer")
        
        # Проверяем, что отзыв ещё не оставлен
        existing = await session.execute(
            select(ReviewORM).where(
                ReviewORM.order_id == order.id,
                ReviewORM.type == 'customer',
                ReviewORM.sender_id == executor.id
            )
        )
        existing = existing.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Review already exists")
        
        # Создаём отзыв
        review = ReviewORM(
            type='customer',
            rate=review_data.rate,
            text=review_data.text,
            sender_id=executor.id,
            recipient_id=customer.id,
            order_id=order.id
        )
        session.add(review)
        
        # Обновляем рейтинг заказчика
        all_reviews = await session.execute(
            select(ReviewORM).where(
                ReviewORM.recipient_id == customer.id,
                ReviewORM.type == 'customer'
            )
        )
        all_reviews = all_reviews.scalars().all()
        
        if all_reviews:
            customer.customer_rating = sum(r.rate for r in all_reviews) / len(all_reviews)
        
        await session.commit()
        await session.refresh(review)
        
        return ReviewResponse(
            id=review.id,
            type=review.type,
            rate=review.rate,
            text=review.text,
            response=review.response,
            sender_id=review.sender_id,
            reviewee_id=review.recipient_id,  # Соответствует ReviewDTO фронтенда
            order_id=review.order_id,
            created_at=review.created_at,
            reviewer_name=executor.name,
            reviewer_nickname=executor.nickname,
            # Для обратной совместимости
            sender_name=executor.name,
            sender_nickname=executor.nickname,
            recipient_id=review.recipient_id,
            recipient_name=customer.name,
            recipient_nickname=customer.nickname
        )

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(user_id: int):
    async with AsyncSessionLocal() as session:
        reviews_result = await session.execute(
            select(ReviewORM).where(ReviewORM.recipient_id == user_id)
        )
        reviews = reviews_result.scalars().all()
        
        reviews_data = []
        for review in reviews:
            sender_result = await session.execute(select(UserORM).where(UserORM.id == review.sender_id))
            sender = sender_result.scalar_one_or_none()
            
            recipient_result = await session.execute(select(UserORM).where(UserORM.id == review.recipient_id))
            recipient = recipient_result.scalar_one_or_none()
            
            reviews_data.append(ReviewResponse(
                id=review.id,
                type=review.type,
                rate=review.rate,
                text=review.text,
                response=review.response,
                sender_id=review.sender_id,
                reviewee_id=review.recipient_id,  # Соответствует ReviewDTO фронтенда
                order_id=review.order_id,
                created_at=review.created_at,
                reviewer_name=sender.name if sender else "",
                reviewer_nickname=sender.nickname if sender else "",
                # Для обратной совместимости
                sender_name=sender.name if sender else "",
                sender_nickname=sender.nickname if sender else "",
                recipient_id=review.recipient_id,
                recipient_name=recipient.name if recipient else "",
                recipient_nickname=recipient.nickname if recipient else ""
            ))
        
        return reviews_data

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        review_result = await session.execute(select(ReviewORM).where(ReviewORM.id == review_id))
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Проверяем, что пользователь может редактировать отзыв
        if review.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="Can only edit your own reviews")
        
        # Обновляем поля
        if review_data.text is not None:
            review.text = review_data.text
        if review_data.rate is not None:
            review.rate = review_data.rate
        
        await session.commit()
        await session.refresh(review)
        
        # Получаем данные отправителя и получателя
        sender_result = await session.execute(select(UserORM).where(UserORM.id == review.sender_id))
        sender = sender_result.scalar_one_or_none()
        
        recipient_result = await session.execute(select(UserORM).where(UserORM.id == review.recipient_id))
        recipient = recipient_result.scalar_one_or_none()
        
        return ReviewResponse(
            id=review.id,
            type=review.type,
            rate=review.rate,
            text=review.text,
            response=review.response,
            sender_id=review.sender_id,
            reviewee_id=review.recipient_id,  # Соответствует ReviewDTO фронтенда
            order_id=review.order_id,
            created_at=review.created_at,
            reviewer_name=sender.name if sender else "",
            reviewer_nickname=sender.nickname if sender else "",
            # Для обратной совместимости
            sender_name=sender.name if sender else "",
            sender_nickname=sender.nickname if sender else "",
            recipient_id=review.recipient_id,
            recipient_name=recipient.name if recipient else "",
            recipient_nickname=recipient.nickname if recipient else ""
        )

@router.post("/{review_id}/response", response_model=ReviewResponse)
async def respond_to_review(
    review_id: int,
    response_data: ReviewResponseCreate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        review_result = await session.execute(select(ReviewORM).where(ReviewORM.id == review_id))
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Проверяем, что пользователь может отвечать на отзыв
        if review.recipient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Can only respond to reviews about you")
        
        review.response = response_data.response
        await session.commit()
        await session.refresh(review)
        
        # Получаем данные отправителя и получателя
        sender_result = await session.execute(select(UserORM).where(UserORM.id == review.sender_id))
        sender = sender_result.scalar_one_or_none()
        
        recipient_result = await session.execute(select(UserORM).where(UserORM.id == review.recipient_id))
        recipient = recipient_result.scalar_one_or_none()
        
        return ReviewResponse(
            id=review.id,
            type=review.type,
            rate=review.rate,
            text=review.text,
            response=review.response,
            sender_id=review.sender_id,
            reviewee_id=review.recipient_id,  # Соответствует ReviewDTO фронтенда
            order_id=review.order_id,
            created_at=review.created_at,
            reviewer_name=sender.name if sender else "",
            reviewer_nickname=sender.nickname if sender else "",
            # Для обратной совместимости
            sender_name=sender.name if sender else "",
            sender_nickname=sender.nickname if sender else "",
            recipient_id=review.recipient_id,
            recipient_name=recipient.name if recipient else "",
            recipient_nickname=recipient.nickname if recipient else ""
        )
