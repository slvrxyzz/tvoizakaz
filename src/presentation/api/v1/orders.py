from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.dependencies import get_order_service, get_session, get_user_service
from src.infrastructure.monitoring.logger import logger
from src.infrastructure.services.order_service import OrderService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.repositiry.db_models import (
    OrderORM,
    CategoryORM,
    UserORM,
    MessageORM,
    ChatORM,
    OrderTypeEnum,
    CurrencyTypeEnum,
)
from sqlalchemy import select, delete, and_
from src.presentation.api.v1.auth import get_current_user, get_optional_user
from src.presentation.api.v1.schemas.order_schemas import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, 
    OrderRespond, OrderStatus, OrderPriority
)
from src.presentation.api.v1.services.order_handlers import OrderHandlers
from src.domain.entity.userentity import UserPrivate

router = APIRouter(prefix="/orders", tags=["Orders"])

def _currency_label(currency: CurrencyTypeEnum) -> str:
    return "руб." if currency == CurrencyTypeEnum.RUB else "TF"

def _get_balance(user: UserPrivate | UserORM, currency: CurrencyTypeEnum) -> float:
    if hasattr(user, "get_balance"):
        return float(user.get_balance(currency))
    if currency == CurrencyTypeEnum.TF:
        return float(getattr(user, "tf_balance", 0.0) or 0.0)
    return float(getattr(user, "balance", 0.0) or 0.0)

def _set_balance(user: UserPrivate | UserORM, currency: CurrencyTypeEnum, value: float) -> None:
    amount = float(value or 0.0)
    if hasattr(user, "set_balance"):
        user.set_balance(currency, amount)
        return
    if currency == CurrencyTypeEnum.TF:
        setattr(user, "tf_balance", amount)
    else:
        user.balance = amount

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user_orm = await user_service.get_user_by_id(current_user.id)
        if not user_orm:
            raise HTTPException(status_code=404, detail="User not found")

        commission = await order_service.get_commission_settings(session)
        commission_post_order = int(commission.get("commission_post_order", 200)) if commission else 200
        order_currency = CurrencyTypeEnum(order_data.currency.value)

        user_balance = _get_balance(user_orm, order_currency)
        if user_balance < commission_post_order:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Недостаточно средств для публикации заказа. Нужно {commission_post_order} {_currency_label(order_currency)}, "
                    f"доступно {user_balance} {_currency_label(order_currency)}."
                ),
            )

        category = None
        if order_data.category_id:
            cat_result = await session.execute(
                select(CategoryORM).where(CategoryORM.id == order_data.category_id)
            )
            category = cat_result.scalar_one_or_none()
            if not category:
                category_name = order_data.category or f"Category {order_data.category_id}"
                category = CategoryORM(name=category_name)
                session.add(category)
                await session.commit()
                await session.refresh(category)
        else:
            cat_result = await session.execute(
                select(CategoryORM).where(CategoryORM.name == order_data.category)
            )
            category = cat_result.scalar_one_or_none()
            if not category:
                category = CategoryORM(name=order_data.category)
                session.add(category)
                await session.commit()
                await session.refresh(category)

        new_order = OrderORM(
            title=order_data.title,
            description=order_data.description,
            price=order_data.price,
            currency=order_currency,
            customer_id=current_user.id,
            term=order_data.term,
            priority=order_data.priority.value,
            status=OrderStatus.OPEN.value,
            category_id=category.id,
            order_type=OrderTypeEnum(order_data.order_type.value),
        )
        session.add(new_order)

        _set_balance(user_orm, order_currency, user_balance - commission_post_order)
        await session.commit()
        await session.refresh(new_order)

        customer_result = await session.execute(select(UserORM).where(UserORM.id == new_order.customer_id))
        customer = customer_result.scalar_one_or_none()
        category_result = await session.execute(select(CategoryORM).where(CategoryORM.id == new_order.category_id))
        category = category_result.scalar_one_or_none()

        return await OrderHandlers.create_order_response(new_order, customer, category)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Ошибка при создании заказа: {str(e)}")

@router.get("/", response_model=OrderListResponse)
async def get_orders(
    category_id: Optional[int] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    sort_by: str = Query("date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    status: Optional[OrderStatus] = Query(OrderStatus.OPEN),
    exclude_my_orders: bool = Query(False),
    current_user: Optional[UserPrivate] = Depends(get_optional_user),
):
    user_id = current_user.id if current_user else None

    return await OrderHandlers.get_orders_with_filters(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        status=status,
        exclude_my_orders=exclude_my_orders if user_id else False,
        current_user_id=user_id,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )

@router.get("/my", response_model=OrderListResponse)
async def get_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    current_user: UserPrivate = Depends(get_current_user)
):
    return await OrderHandlers.get_orders_with_filters(
        status=status,
        exclude_my_orders=False,
        current_user_id=current_user.id,
        page=page,
        page_size=page_size
    )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(OrderORM).where(OrderORM.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    customer_result = await session.execute(select(UserORM).where(UserORM.id == order.customer_id))
    customer = customer_result.scalar_one_or_none()
    category_result = await session.execute(select(CategoryORM).where(CategoryORM.id == order.category_id))
    category = category_result.scalar_one_or_none()

    return await OrderHandlers.create_order_response(order, customer, category)

@router.post("/{order_id}/respond")
async def respond_to_order(
    order_id: int,
    respond_data: OrderRespond,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    user_service: UserService = Depends(get_user_service),
):
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot respond to your own order")

    executor = await user_service.get_user_by_id(current_user.id)
    if not executor:
        raise HTTPException(status_code=401, detail="User not found")

    existing_response = await session.execute(
        select(MessageORM).where(
            and_(
                MessageORM.message_type == "offer",
                MessageORM.chat_id.in_(select(ChatORM.id).where(ChatORM.order_id == order_id)),
                MessageORM.sender_id == current_user.id,
            )
        )
    )
    if existing_response.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already responded to this order")

    await order_service.increment_responses(order)

    order_currency = order.currency if isinstance(order.currency, CurrencyTypeEnum) else CurrencyTypeEnum(order.currency)

    commission = await order_service.get_commission_settings(session) or {}
    commission_response_threshold = int(commission.get("commission_response_threshold", 5000))
    commission_response_percent = float(commission.get("commission_response_percent", 1.0))

    response_fee = 0
    if respond_data.price > commission_response_threshold:
        response_fee = int(respond_data.price * commission_response_percent / 100)
        executor_balance = _get_balance(executor, order_currency)
        if executor_balance < response_fee:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно средств для отклика. Нужно {response_fee} {_currency_label(order_currency)}.",
            )
        _set_balance(executor, order_currency, executor_balance - response_fee)
        await session.commit()

    from src.infrastructure.services.chat_service import ChatService
    from src.infrastructure.repositiry.message_repository import MessageRepository
    from src.domain.entity.messageentity import Message

    chat_service = ChatService(session)
    message_repo = MessageRepository(session)

    customer = await user_service.get_user_by_id(order.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.id == executor.id:
        raise HTTPException(status_code=400, detail="You cannot create a chat with yourself")

    chat = await chat_service.get_or_create_chat_between_users(customer.id, executor.id)

    message = Message(
        chat_id=chat.id,
        sender_id=executor.id,
        content=respond_data.message,
        message_type="offer",
    )
    await message_repo.add_message(message)

    return {"success": True, "chat_id": chat.id, "response_fee": response_fee}

@router.post("/{order_id}/accept")
async def accept_order(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    user_service: UserService = Depends(get_user_service),
):
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    customer = await user_service.get_user_by_id(current_user.id)
    if not customer or customer.id != order.customer_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    msgs = await session.execute(
        select(MessageORM)
        .where(
            MessageORM.chat_id.in_(select(ChatORM.id).where(ChatORM.order_id == order_id)),
            MessageORM.message_type == "offer",
            MessageORM.sender_id != order.customer_id,
        )
        .order_by(MessageORM.created_at.desc())
    )
    offers = msgs.scalars().all()

    if not offers:
        raise HTTPException(status_code=400, detail="Нет подходящего отклика для этого заказа")

    executor_id = offers[0].sender_id

    order.executor_id = executor_id
    order.status = "WORK"
    await session.commit()

    executor = await user_service.get_user_by_id(executor_id)
    if executor:
        executor.taken_count += 1
        await session.commit()

    return {
        "success": True,
        "order_id": order_id,
        "message": "Order accepted successfully",
    }

@router.post("/{order_id}/submit_for_review")
async def submit_order_for_review(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
):
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.executor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only executor can submit order for review")

    if order.status != "WORK":
        raise HTTPException(status_code=400, detail="Order must be in WORK status to submit for review")

    order.status = "REVIEW"
    await session.commit()

    return {"success": True, "order_id": order_id, "status": "REVIEW"}

@router.post("/{order_id}/approve")
async def approve_order(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
    user_service: UserService = Depends(get_user_service),
):
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only customer can approve order")

    customer = await user_service.get_user_by_id(current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if order.status != "REVIEW":
        raise HTTPException(status_code=400, detail="Order must be in REVIEW status to approve")

    offer_price = order.price
    order_currency = order.currency if isinstance(order.currency, CurrencyTypeEnum) else CurrencyTypeEnum(order.currency)

    commission = await order_service.get_commission_settings(session) or {}
    commission_customer = float(commission.get("commission_customer", 10.0))
    commission_executor = float(commission.get("commission_executor", 5.0))

    total_for_customer = int(offer_price + offer_price * commission_customer / 100)
    executor_balance = int(offer_price - offer_price * commission_executor / 100)

    customer_balance = _get_balance(customer, order_currency)
    if customer_balance < total_for_customer:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Недостаточно средств на балансе. Нужно {total_for_customer} {_currency_label(order_currency)}, "
                f"доступно {customer_balance} {_currency_label(order_currency)}."
            ),
        )

    _set_balance(customer, order_currency, customer_balance - total_for_customer)

    executor = await user_service.get_user_by_id(order.executor_id)
    if executor:
        executor_balance_before = _get_balance(executor, order_currency)
        _set_balance(executor, order_currency, executor_balance_before + executor_balance)
        executor.done_count += 1
        await session.commit()
    else:
        await session.commit()

    order.status = "CLOSE"
    await session.commit()

    return {
        "success": True,
        "order_id": order_id,
        "status": "CLOSE",
        "customer_balance": _get_balance(customer, order_currency),
        "executor_balance": _get_balance(executor, order_currency) if executor else 0,
        "total_paid": total_for_customer,
        "executor_received": executor_balance,
    }

@router.post("/{order_id}/reject")
async def reject_order(
    order_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    order_service: OrderService = Depends(get_order_service),
):
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only customer can reject order")

    if order.status != "REVIEW":
        raise HTTPException(status_code=400, detail="Order must be in REVIEW status to reject")

    order.status = "WORK"
    await session.commit()

    return {"success": True, "order_id": order_id, "status": "WORK"}
