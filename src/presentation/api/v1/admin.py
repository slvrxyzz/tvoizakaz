from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.user_service import UserService
from src.infrastructure.services.order_service import OrderService
from src.infrastructure.repositiry.db_models import (
    UserORM,
    OrderORM,
    MessageORM,
    CommissionSettingsORM,
    ChatORM,
    SupportRequestORM,
    CurrencyTypeEnum,
)
from sqlalchemy import select, func, text as sa_text
from sqlalchemy.orm import selectinload
from src.presentation.api.v1.auth import get_current_user
from src.domain.entity.userentity import UserPrivate, UserRole
from src.infrastructure.monitoring.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])

# Pydantic models
class AdminStats(BaseModel):
    total_users: int
    total_orders: int
    total_messages: int
    total_contact_requests: int
    active_users_today: int
    orders_today: int

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=15)
    nickname: Optional[str] = Field(None, min_length=4, max_length=10)
    email: Optional[str] = None
    balance: Optional[float] = Field(None, ge=0)
    rub_balance: Optional[float] = Field(None, ge=0)
    tf_balance: Optional[float] = Field(None, ge=0)
    customer_rating: Optional[float] = Field(None, ge=0, le=5)
    executor_rating: Optional[float] = Field(None, ge=0, le=5)
    is_support: Optional[bool] = None
    phone_verified: Optional[bool] = None
    admin_verified: Optional[bool] = None
    role: Optional[UserRole] = None

class OrderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=30)
    description: Optional[str] = Field(None, min_length=1, max_length=250)
    price: Optional[int] = Field(None, ge=400, le=400000)
    status: Optional[str] = None
    executor_id: Optional[int] = None

class CommissionSettings(BaseModel):
    commission_withdraw: float = Field(..., ge=0, le=100)
    commission_customer: float = Field(..., ge=0, le=100)
    commission_executor: float = Field(..., ge=0, le=100)
    commission_post_order: int = Field(..., ge=0)
    commission_response_threshold: int = Field(..., ge=0)
    commission_response_percent: float = Field(..., ge=0, le=100)

class BalanceUpdate(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    currency: CurrencyTypeEnum = Field(default=CurrencyTypeEnum.RUB)
    reason: Optional[str] = Field(None, max_length=100)


class UserAdminEntry(BaseModel):
    id: int
    name: str
    nickname: str
    email: str
    balance: float
    rub_balance: float
    tf_balance: float
    customer_rating: float
    executor_rating: float
    done_count: int
    taken_count: int
    is_support: bool
    phone_verified: bool
    admin_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    role: str


class OrderAdminEntry(BaseModel):
    id: int
    title: str
    description: str
    price: int
    currency: str
    term: int
    status: str
    priority: str
    responses: int
    created_at: datetime
    customer_id: int
    customer_name: str
    customer_nickname: str
    executor_id: Optional[int]
    executor_name: Optional[str]
    executor_nickname: Optional[str]


class OfferAdminEntry(BaseModel):
    id: int
    text: str
    order_id: Optional[int]
    order_title: Optional[str]
    chat_id: int
    sender_id: int
    sender_nickname: Optional[str]
    created_at: datetime


class SupportRequestEntry(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    email: str
    message: str
    status: str
    created_at: datetime


class PaginatedUsersResponse(BaseModel):
    data: List[UserAdminEntry]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedOrdersResponse(BaseModel):
    data: List[OrderAdminEntry]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedOffersResponse(BaseModel):
    data: List[OfferAdminEntry]
    total: int
    page: int
    page_size: int
    total_pages: int


class SupportRequestsResponse(BaseModel):
    data: List[SupportRequestEntry]
    total: int
    page: int
    page_size: int
    total_pages: int


class SQLRequest(BaseModel):
    query: str = Field(..., min_length=1)


class SQLResponse(BaseModel):
    success: bool
    rows_affected: int
    result: List[Dict[str, Any]]


class BroadcastRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

# Dependency для проверки админских прав
async def get_admin_user(current_user: UserPrivate = Depends(get_current_user)) -> UserPrivate:
    role_value = getattr(current_user, 'role', UserRole.CUSTOMER.value)
    try:
        role = UserRole(role_value) if not isinstance(role_value, UserRole) else role_value
    except ValueError:
        role = UserRole.CUSTOMER

    if role not in {UserRole.ADMIN, UserRole.SUPPORT}:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(admin_user: UserPrivate = Depends(get_admin_user)):
    async with AsyncSessionLocal() as session:
        today = datetime.utcnow().date()
        # Подсчёт общей статистики
        users_count = await session.execute(select(func.count(UserORM.id)))
        total_users = users_count.scalar() or 0

        orders_count = await session.execute(select(func.count(OrderORM.id)))
        total_orders = orders_count.scalar() or 0

        messages_count = await session.execute(select(func.count(MessageORM.id)))
        total_messages = messages_count.scalar() or 0
        
        # ContactRequestORM не существует, используем 0
        total_contact_requests = 0
        
        # Активные пользователи сегодня (last_login не существует в UserORM)
        active_users_today = 0
        
        # Заказы сегодня
        orders_today_query = await session.execute(
            select(func.count(OrderORM.id)).where(func.date(OrderORM.created_at) == today)
        )
        orders_today = orders_today_query.scalar() or 0
        
        return AdminStats(
            total_users=total_users,
            total_orders=total_orders,
            total_messages=total_messages,
            total_contact_requests=total_contact_requests,
            active_users_today=active_users_today,
            orders_today=orders_today
        )

@router.get("/users", response_model=PaginatedUsersResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        query = select(UserORM)
        
        # Подсчёт общего количества
        count_query = query.with_only_columns(UserORM.id).order_by(None)
        total_users = (await session.execute(count_query)).scalars().all()
        total_count = len(total_users)
        
        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await session.execute(query)
        users = result.scalars().all()
        
        users_data: List[UserAdminEntry] = []
        for user in users:
            rub_balance = float(getattr(user, "rub_balance", getattr(user, "balance", 0.0)) or 0.0)
            tf_balance = float(getattr(user, "tf_balance", 0.0) or 0.0)
            customer_rating = float(getattr(user, "customer_rating", 0.0) or 0.0)
            executor_rating = float(getattr(user, "executor_rating", 0.0) or 0.0)
            done_count = int(getattr(user, "done_count", 0) or 0)
            taken_count = int(getattr(user, "taken_count", 0) or 0)
            is_support = bool(getattr(user, "is_support", False))
            phone_verified = bool(user.phone_verified) if user.phone_verified is not None else False
            admin_verified = bool(user.admin_verified) if user.admin_verified is not None else False
            raw_role = getattr(user, "role", UserRole.CUSTOMER.value)
            try:
                role_value = raw_role.value if isinstance(raw_role, UserRole) else UserRole(str(raw_role or UserRole.CUSTOMER.value)).value
            except ValueError:
                role_value = UserRole.CUSTOMER.value

            users_data.append(
                UserAdminEntry(
                    id=user.id,
                    name=user.name,
                    nickname=user.nickname,
                    email=user.email,
                    balance=rub_balance,
                    rub_balance=rub_balance,
                    tf_balance=tf_balance,
                    customer_rating=customer_rating,
                    executor_rating=executor_rating,
                    done_count=done_count,
                    taken_count=taken_count,
                    is_support=is_support,
                    phone_verified=phone_verified,
                    admin_verified=admin_verified,
                    created_at=user.created_at,
                    last_login=getattr(user, "last_login", None),
                    role=role_value,
                )
            )

        total_pages = (total_count + page_size - 1) // page_size if page_size else 1

        return PaginatedUsersResponse(
            data=users_data,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=max(1, total_pages),
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(UserORM).where(UserORM.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Обновляем только переданные поля
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.nickname is not None:
            user.nickname = user_data.nickname
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.rub_balance is not None:
            user.rub_balance = user_data.rub_balance
        elif user_data.balance is not None:
            user.balance = user_data.balance
        if user_data.tf_balance is not None:
            user.tf_balance = user_data.tf_balance
        if user_data.customer_rating is not None:
            user.customer_rating = user_data.customer_rating
        if user_data.executor_rating is not None:
            user.executor_rating = user_data.executor_rating
        if user_data.is_support is not None:
            user.is_support = user_data.is_support
        if user_data.phone_verified is not None:
            user.phone_verified = user_data.phone_verified
        if user_data.admin_verified is not None:
            user.admin_verified = user_data.admin_verified
        if user_data.role is not None:
            user.role = user_data.role.value
            user.is_support = user_data.role == UserRole.SUPPORT
            user.is_editor = user_data.role == UserRole.EDITOR
            if user_data.admin_verified is None:
                user.admin_verified = user_data.role in {UserRole.ADMIN, UserRole.SUPPORT}
        
        await session.commit()
        
        logger.audit("admin_update_user", user_id=admin_user.id, target_user=user_id)

        return {"success": True, "message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(UserORM).where(UserORM.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await session.delete(user)
        await session.commit()
        
        logger.audit("admin_delete_user", user_id=admin_user.id, target_user=user_id)

        return {"success": True, "message": "User deleted successfully"}

@router.get("/orders", response_model=PaginatedOrdersResponse)
async def get_all_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        query = select(OrderORM)
        
        # Подсчёт общего количества
        count_query = query.with_only_columns(OrderORM.id).order_by(None)
        total_orders = (await session.execute(count_query)).scalars().all()
        total_count = len(total_orders)
        
        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await session.execute(query)
        orders = result.scalars().all()
        
        orders_data: List[OrderAdminEntry] = []
        for order in orders:
            customer_result = await session.execute(select(UserORM).where(UserORM.id == order.customer_id))
            customer = customer_result.scalar_one_or_none()
            
            executor_result = await session.execute(select(UserORM).where(UserORM.id == order.executor_id))
            executor = executor_result.scalar_one_or_none()
            
            orders_data.append(
                OrderAdminEntry(
                    id=order.id,
                    title=order.title,
                    description=order.description,
                    price=order.price,
                    currency=(order.currency.value if hasattr(order.currency, "value") else order.currency),
                    term=order.term,
                    status=order.status,
                    priority=order.priority,
                    responses=order.responses,
                    created_at=order.created_at,
                    customer_id=order.customer_id,
                    customer_name=customer.name if customer else "",
                    customer_nickname=customer.nickname if customer else "",
                    executor_id=order.executor_id,
                    executor_name=executor.name if executor else None,
                    executor_nickname=executor.nickname if executor else None,
                )
            )

        total_pages = (total_count + page_size - 1) // page_size if page_size else 1

        return PaginatedOrdersResponse(
            data=orders_data,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=max(1, total_pages),
        )

@router.put("/orders/{order_id}")
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        order_result = await session.execute(select(OrderORM).where(OrderORM.id == order_id))
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Обновляем только переданные поля
        if order_data.title is not None:
            order.title = order_data.title
        if order_data.description is not None:
            order.description = order_data.description
        if order_data.price is not None:
            order.price = order_data.price
        if order_data.status is not None:
            order.status = order_data.status
        if order_data.executor_id is not None:
            order.executor_id = order_data.executor_id
        
        await session.commit()
        
        logger.audit("admin_update_order", user_id=admin_user.id, target_order=order_id)

        return {"success": True, "message": "Order updated successfully"}

@router.delete("/orders/{order_id}")
async def delete_order(
    order_id: int,
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        order_result = await session.execute(select(OrderORM).where(OrderORM.id == order_id))
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        await session.delete(order)
        await session.commit()
        
        logger.audit("admin_delete_order", user_id=admin_user.id, target_order=order_id)

        return {"success": True, "message": "Order deleted successfully"}

@router.get("/offers", response_model=PaginatedOffersResponse)
async def get_offers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: UserPrivate = Depends(get_admin_user),
):
    async with AsyncSessionLocal() as session:
        base_query = select(MessageORM).where(
            MessageORM.message_type == "offer",
            MessageORM.is_deleted.is_(False),
        )

        count_query = base_query.with_only_columns(MessageORM.id).order_by(None)
        total_rows = (await session.execute(count_query)).scalars().all()
        total_count = len(total_rows)

        offset = (page - 1) * page_size
        data_query = (
            base_query.order_by(MessageORM.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .options(
                selectinload(MessageORM.chat).selectinload(ChatORM.order),
                selectinload(MessageORM.sender),
            )
        )

        result = await session.execute(data_query)
        messages = result.scalars().all()

        offers: List[OfferAdminEntry] = []
        for message in messages:
            chat = message.chat
            order = chat.order if chat else None
            sender = message.sender
            offers.append(
                OfferAdminEntry(
                    id=message.id,
                    text=message.content,
                    order_id=order.id if order else None,
                    order_title=order.title if order else None,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    sender_nickname=sender.nickname if sender else None,
                    created_at=message.created_at,
                )
            )

        total_pages = (total_count + page_size - 1) // page_size if page_size else 1

        return PaginatedOffersResponse(
            data=offers,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=max(1, total_pages),
        )


@router.delete("/offers/{offer_id}")
async def delete_offer(
    offer_id: int,
    admin_user: UserPrivate = Depends(get_admin_user),
):
    async with AsyncSessionLocal() as session:
        offer_result = await session.execute(
            select(MessageORM).where(
                MessageORM.id == offer_id,
                MessageORM.message_type == "offer",
            )
        )
        offer = offer_result.scalar_one_or_none()

        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")

        offer.is_deleted = True
        await session.commit()

        logger.audit("admin_delete_offer", user_id=admin_user.id, target_offer=offer_id)

        return {"success": True, "message": "Offer deleted successfully"}


@router.get("/support/requests", response_model=SupportRequestsResponse)
async def get_support_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: UserPrivate = Depends(get_admin_user),
):
    async with AsyncSessionLocal() as session:
        base_query = select(SupportRequestORM).order_by(SupportRequestORM.created_at.desc())
        count_query = base_query.with_only_columns(SupportRequestORM.id).order_by(None)
        total_rows = (await session.execute(count_query)).scalars().all()
        total_count = len(total_rows)

        offset = (page - 1) * page_size
        data_query = base_query.offset(offset).limit(page_size)
        result = await session.execute(data_query)
        requests = result.scalars().all()

        data: List[SupportRequestEntry] = []
        for request in requests:
            data.append(
                SupportRequestEntry(
                    id=request.id,
                    user_id=request.user_id,
                    name=request.name,
                    email=request.email,
                    message=request.message,
                    status=request.status,
                    created_at=request.created_at,
                )
            )

        total_pages = (total_count + page_size - 1) // page_size if page_size else 1

        return SupportRequestsResponse(
            data=data,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=max(1, total_pages),
        )


@router.post("/support/requests/{request_id}/close")
async def close_support_request(
    request_id: int,
    admin_user: UserPrivate = Depends(get_admin_user),
):
    async with AsyncSessionLocal() as session:
        request_result = await session.execute(
            select(SupportRequestORM).where(SupportRequestORM.id == request_id)
        )
        support_request = request_result.scalar_one_or_none()

        if not support_request:
            raise HTTPException(status_code=404, detail="Support request not found")

        support_request.status = "answered"
        await session.commit()

        logger.audit(
            "admin_close_support_request",
            user_id=admin_user.id,
            target_request=request_id,
        )

        return {"success": True, "message": "Support request closed"}


@router.post("/support/broadcast")
async def broadcast_support_message(
    payload: BroadcastRequest,
    admin_user: UserPrivate = Depends(get_admin_user),
):
    logger.audit("admin_support_broadcast", user_id=admin_user.id)
    logger.info(
        "support_broadcast",
        user_id=admin_user.id,
        message=payload.message,
    )

    return {"success": True, "message": "Broadcast sent"}


@router.post("/sql", response_model=SQLResponse)
async def execute_admin_sql(
    sql_request: SQLRequest,
    admin_user: UserPrivate = Depends(get_admin_user),
):
    statement = sql_request.query.strip()
    if not statement:
        raise HTTPException(status_code=400, detail="SQL query is required")

    allowed_prefixes = (
        "select",
        "update",
        "delete",
        "insert",
        "with",
        "show",
        "describe",
        "explain",
        "create",
        "alter",
        "drop",
    )
    if not statement.lower().startswith(allowed_prefixes):
        raise HTTPException(status_code=400, detail="Unsupported SQL operation")

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(sa_text(statement))

            rows: List[Dict[str, Any]] = []
            if result.returns_rows:
                rows = [dict(row._mapping) for row in result.mappings().all()]

            rows_affected = result.rowcount if result.rowcount not in (None, -1) else len(rows)

            if not result.returns_rows:
                await session.commit()

            return SQLResponse(success=True, rows_affected=rows_affected, result=rows)
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            logger.error("admin_sql_error", error=str(exc))
            raise HTTPException(status_code=400, detail=f"SQL execution failed: {exc}") from exc

@router.get("/commission", response_model=CommissionSettings)
async def get_commission_settings(admin_user: UserPrivate = Depends(get_admin_user)):
    async with AsyncSessionLocal() as session:
        order_service = OrderService(session)
        commission = await order_service.get_commission_settings(session) or {}
        
        return CommissionSettings(
            commission_withdraw=commission.get('commission_withdraw', 3.0),
            commission_customer=commission.get('commission_customer', 10.0),
            commission_executor=commission.get('commission_executor', 5.0),
            commission_post_order=commission.get('commission_post_order', 200),
            commission_response_threshold=commission.get('commission_response_threshold', 5000),
            commission_response_percent=commission.get('commission_response_percent', 1.0)
        )

@router.put("/commission")
async def update_commission_settings(
    settings: CommissionSettings,
    admin_user: UserPrivate = Depends(get_admin_user)
):
    async with AsyncSessionLocal() as session:
        order_service = OrderService(session)
        try:
            await order_service.set_commission_settings(
                session,
                commission_withdraw=settings.commission_withdraw,
                commission_customer=settings.commission_customer,
                commission_executor=settings.commission_executor,
                commission_post_order=settings.commission_post_order,
                commission_response_threshold=settings.commission_response_threshold,
                commission_response_percent=settings.commission_response_percent
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        
        logger.audit("admin_update_commission", user_id=admin_user.id)

        return {"success": True, "message": "Commission settings updated successfully"}

# ContactRequestORM не существует, поэтому эти эндпоинты отключены

@router.post("/balance/add")
async def add_user_balance(
    balance_data: BalanceUpdate,
    admin_user: UserPrivate = Depends(get_admin_user)
):
    """Пополнение баланса пользователя (только для админов)"""
    async with AsyncSessionLocal() as session:
        user_service = UserService(session)
        
        # Получаем пользователя
        user = await user_service.get_user_by_id(balance_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Пополняем баланс
        current_balance = user.get_balance(balance_data.currency)
        new_balance = current_balance + balance_data.amount
        user.set_balance(balance_data.currency, new_balance)
        await session.commit()
        
        logger.audit(
            "admin_balance_topup",
            user_id=admin_user.id,
            target_user=balance_data.user_id,
            amount=balance_data.amount,
            currency=balance_data.currency.value,
        )

        return {
            "success": True,
            "message": f"Balance updated successfully",
            "user_id": balance_data.user_id,
            "currency": balance_data.currency.value,
            "new_balance": new_balance,
            "amount_added": balance_data.amount,
            "reason": balance_data.reason
        }
