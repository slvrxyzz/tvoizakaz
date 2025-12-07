from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.user_service import UserService
from src.infrastructure.repositiry.db_models import UserORM, ReviewORM
from sqlalchemy import func, select, or_
from src.presentation.api.v1.auth import get_current_user
from src.domain.entity.userentity import UserPrivate, UserRole
from src.domain.entity.orderentity import CurrencyType

router = APIRouter(prefix="/users", tags=["Users"])

# Pydantic models
class UserPublicProfile(BaseModel):
    id: int
    name: str
    nickname: str
    specification: str
    description: Optional[str] = None
    created_at: datetime
    photo: Optional[str] = None
    phone_verified: bool
    admin_verified: bool
    is_premium: bool
    customer_rating: float
    executor_rating: float
    done_count: int
    taken_count: int
    reviews: Optional[List[dict]] = None  # Структура соответствует ReviewDTO
    role: str

class UsersListResponse(BaseModel):
    users: List[UserPublicProfile]
    total: int
    page: int
    page_size: int

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=15)
    description: Optional[str] = Field(None, max_length=500)
    specification: Optional[str] = Field(None, max_length=100)

class UserProfileResponse(BaseModel):
    id: int
    name: str
    nickname: str
    email: str
    specification: str
    description: Optional[str]
    photo: Optional[str]
    balance: float
    tf_balance: float
    customer_rating: float
    executor_rating: float
    done_count: int
    taken_count: int
    phone_verified: bool
    admin_verified: bool
    phone_number: Optional[str]
    created_at: datetime
    role: UserRole

# Удален дубликат UserPublicProfile - используется класс выше

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
    reviewee_id: int
    order_id: int
    created_at: datetime

@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: UserPrivate = Depends(get_current_user)):
    """Получить текущего пользователя (для фронтенда)"""
    balance = current_user.get_balance(CurrencyType.RUB)
    tf_balance = current_user.get_balance(CurrencyType.TF)
    is_support = bool(getattr(current_user, "is_support", False))
    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        nickname=current_user.nickname,
        email=current_user.email,
        specification=current_user.specification or "",
        description=current_user.description or "",
        photo=getattr(current_user, "photo", None),
        balance=float(balance),
        tf_balance=float(tf_balance),
        customer_rating=current_user.customer_rating if current_user.customer_rating is not None else 0.0,
        executor_rating=current_user.executor_rating if current_user.executor_rating is not None else 0.0,
        done_count=int(getattr(current_user, "done_count", 0) or 0),
        taken_count=int(getattr(current_user, "taken_count", 0) or 0),
        phone_verified=current_user.phone_verified if current_user.phone_verified is not None else False,
        admin_verified=bool(current_user.admin_verified) or is_support,
        phone_number=getattr(current_user, "phone_number", None),
        created_at=current_user.created_at,
        role=current_user.role if isinstance(current_user.role, UserRole) else UserRole(str(current_user.role or UserRole.CUSTOMER.value)),
    )

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: UserPrivate = Depends(get_current_user)):
    """Получить профиль пользователя (альтернативный эндпоинт)"""
    balance = current_user.get_balance(CurrencyType.RUB)
    tf_balance = current_user.get_balance(CurrencyType.TF)
    is_support = bool(getattr(current_user, "is_support", False))
    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        nickname=current_user.nickname,
        email=current_user.email,
        specification=current_user.specification or "",
        description=current_user.description or "",
        photo=getattr(current_user, "photo", None),
        balance=float(balance),
        tf_balance=float(tf_balance),
        customer_rating=current_user.customer_rating if current_user.customer_rating is not None else 0.0,
        executor_rating=current_user.executor_rating if current_user.executor_rating is not None else 0.0,
        done_count=int(getattr(current_user, "done_count", 0) or 0),
        taken_count=int(getattr(current_user, "taken_count", 0) or 0),
        phone_verified=current_user.phone_verified if current_user.phone_verified is not None else False,
        admin_verified=bool(current_user.admin_verified) or is_support,
        phone_number=getattr(current_user, "phone_number", None),
        created_at=current_user.created_at,
        role=current_user.role if isinstance(current_user.role, UserRole) else UserRole(str(current_user.role or UserRole.CUSTOMER.value)),
    )

@router.put("/profile", response_model=UserProfileResponse)
@router.put("/me", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_id(current_user.id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if profile_data.name is not None:
            user.name = profile_data.name
        if profile_data.description is not None:
            user.description = profile_data.description
        if profile_data.specification is not None:
            user.specification = profile_data.specification
        
        await session.commit()
        await session.refresh(user)
        
        balance = float(getattr(user, 'balance', getattr(user, 'rub_balance', 0.0)) or 0.0)
        tf_balance = float(getattr(user, 'tf_balance', 0.0) or 0.0)
        return UserProfileResponse(
            id=user.id,
            name=user.name,
            nickname=user.nickname,
            email=user.email,
            specification=user.specification,
            description=user.description,
            photo=getattr(user, 'photo', None),
            balance=float(balance),
            tf_balance=float(tf_balance),
            customer_rating=user.customer_rating if user.customer_rating is not None else 0.0,
            executor_rating=user.executor_rating if user.executor_rating is not None else 0.0,
            done_count=getattr(user, 'done_count', 0),
            taken_count=getattr(user, 'taken_count', 0),
            phone_verified=user.phone_verified if user.phone_verified is not None else False,
            admin_verified=user.admin_verified if user.admin_verified is not None else False,
            phone_number=getattr(user, 'phone_number', None),
            created_at=user.created_at,
            role=UserRole(getattr(user, 'role', UserRole.CUSTOMER.value)),
        )

@router.get("/{nickname}", response_model=UserPublicProfile)
async def get_public_profile(nickname: str):
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(UserORM).where(UserORM.nickname == nickname))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем отзывы
        reviews_result = await session.execute(select(ReviewORM).where(ReviewORM.recipient_id == user.id))
        reviews = reviews_result.scalars().all()
        
        reviews_data = []
        for review in reviews:
            sender_result = await session.execute(select(UserORM).where(UserORM.id == review.sender_id))
            sender = sender_result.scalar_one_or_none()

            # Структура соответствует ReviewDTO фронтенда
            reviews_data.append({
                "id": review.id,
                "type": review.type,
                "rate": review.rate,
                "text": review.text,
                "response": review.response,
                "sender_id": review.sender_id,
                "reviewee_id": review.recipient_id,
                "order_id": review.order_id,
                "reviewer_name": sender.name if sender else "",
                "reviewer_nickname": sender.nickname if sender else "",
                "created_at": review.created_at.isoformat() if hasattr(review.created_at, 'isoformat') else str(review.created_at)
            })

        return UserPublicProfile(
            id=user.id,
            name=user.name,
            nickname=user.nickname,
            specification=user.specification,
            description=user.description,
            created_at=user.created_at,
            photo=getattr(user, 'photo', None),
            phone_verified=user.phone_verified if user.phone_verified is not None else False,
            admin_verified=user.admin_verified if user.admin_verified is not None else False,
            is_premium=getattr(user, 'is_premium', False),
            customer_rating=user.customer_rating if user.customer_rating is not None else 0.0,
            executor_rating=user.executor_rating if user.executor_rating is not None else 0.0,
            done_count=getattr(user, 'done_count', 0),
            taken_count=getattr(user, 'taken_count', 0),
            reviews=reviews_data
        )

@router.get("/", response_model=UsersListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    min_rating: Optional[float] = Query(3.0, ge=0.0, le=5.0),
    specification: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None, description="Фильтр по роли пользователя: CUSTOMER/EXECUTOR/ADMIN"),
):
    async with AsyncSessionLocal() as session:
        role_column = func.upper(func.coalesce(UserORM.role, ""))
        base_query = select(UserORM).where(
            or_(UserORM.is_support.is_(False), UserORM.is_support.is_(None)),
        )

        if role and role.upper() != "ALL":
            try:
                normalized_role = UserRole(role.upper()).value
                base_query = base_query.where(role_column == normalized_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid role filter")

        if min_rating is not None and min_rating > 0:
            base_query = base_query.where(
                func.coalesce(UserORM.executor_rating, 0) >= min_rating
            )

        if specification:
            base_query = base_query.where(UserORM.specification.ilike(f"%{specification}%"))

        if search:
            pattern = f"%{search}%"
            base_query = base_query.where(
                (UserORM.name.ilike(pattern)) |
                (UserORM.nickname.ilike(pattern))
            )

        count_query = base_query.with_only_columns(func.count()).order_by(None)
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        pagination_query = base_query.offset(offset).limit(page_size)
        result = await session.execute(pagination_query)
        users = result.scalars().all()

        users_data: List[UserPublicProfile] = []
        for user in users:
            reviews_result = await session.execute(select(ReviewORM).where(ReviewORM.recipient_id == user.id))
            reviews = reviews_result.scalars().all()

            reviews_data = []
            for review in reviews:
                sender_result = await session.execute(select(UserORM).where(UserORM.id == review.sender_id))
                sender = sender_result.scalar_one_or_none()

                reviews_data.append(
                    {
                        "id": review.id,
                        "type": review.type,
                        "rate": review.rate,
                        "text": review.text,
                        "response": review.response,
                        "sender_id": review.sender_id,
                        "reviewee_id": review.recipient_id,
                        "order_id": review.order_id,
                        "reviewer_name": sender.name if sender else "",
                        "reviewer_nickname": sender.nickname if sender else "",
                        "created_at": review.created_at.isoformat()
                        if hasattr(review.created_at, "isoformat")
                        else str(review.created_at),
                    }
                )

            role_value = (user.role or "CUSTOMER").upper()
            if role_value == "SUPPORT":
                continue

            users_data.append(
                UserPublicProfile(
                    id=user.id,
                    name=user.name,
                    nickname=user.nickname,
                    specification=user.specification or "",
                    description=user.description or "",
                    created_at=user.created_at,
                    photo=user.photo,
                    phone_verified=bool(user.phone_verified),
                    admin_verified=bool(user.admin_verified),
                    is_premium=bool(getattr(user, "is_premium", False)),
                    customer_rating=float(user.customer_rating or 0.0),
                    executor_rating=float(user.executor_rating or 0.0),
                    done_count=int(getattr(user, "done_count", 0) or 0),
                    taken_count=int(getattr(user, "taken_count", 0) or 0),
                    reviews=reviews_data,
                    role=role_value,
                )
            )

        total_result_count = len(users_data)
        total_pages = (total_result_count + page_size - 1) // page_size if page_size else 1

        return UsersListResponse(
            users=users_data,
            total=total_result_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
