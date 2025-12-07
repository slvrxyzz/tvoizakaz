from fastapi import HTTPException
from sqlalchemy import select
from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.order_service import OrderService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.services.message_service import MessageService
from src.infrastructure.repositiry.db_models import OrderORM, CategoryORM, UserORM, OrderTypeEnum, CurrencyTypeEnum
from src.presentation.api.v1.schemas.order_schemas import OrderResponse, OrderListResponse, OrderStatus, OrderPriority, OrderType, CurrencyType
from src.domain.entity.userentity import UserPrivate

STATUS_ALIASES = {
    "ACTIVE": OrderStatus.OPEN,
    "OPEN": OrderStatus.OPEN,
    "WORK": OrderStatus.WORK,
    "IN_PROGRESS": OrderStatus.WORK,
    "REVIEW": OrderStatus.REVIEW,
    "CLOSE": OrderStatus.CLOSE,
    "CLOSED": OrderStatus.CLOSE,
    "COMPLETED": OrderStatus.CLOSE,
}


class OrderHandlers:
    @staticmethod
    def _resolve_enum(enum_cls, value, default, aliases=None):
        if isinstance(value, enum_cls):
            return value

        if value is None:
            return default

        if hasattr(value, "value"):
            value = value.value

        if isinstance(value, str):
            normalized = value.upper()
            if aliases and normalized in aliases:
                return aliases[normalized]
            if normalized in enum_cls.__members__:
                return enum_cls[normalized]
            try:
                return enum_cls(value)
            except ValueError:
                try:
                    return enum_cls(normalized)
                except ValueError:
                    return default

        try:
            return enum_cls(value)
        except ValueError:
            return default

    @staticmethod
    async def create_order_response(order_orm: OrderORM, customer: UserORM, category: CategoryORM) -> OrderResponse:
        status = OrderHandlers._resolve_enum(OrderStatus, getattr(order_orm, "status", None), OrderStatus.OPEN, STATUS_ALIASES)
        priority = OrderHandlers._resolve_enum(OrderPriority, getattr(order_orm, "priority", None), OrderPriority.NORMAL)

        raw_order_type = getattr(order_orm, "order_type", None)
        order_type = OrderHandlers._resolve_enum(
            OrderType,
            raw_order_type.value if hasattr(raw_order_type, "value") else raw_order_type,
            OrderType.REGULAR,
        )

        raw_currency = getattr(order_orm, "currency", None)
        currency = OrderHandlers._resolve_enum(
            CurrencyType,
            raw_currency.value if hasattr(raw_currency, "value") else raw_currency,
            CurrencyType.RUB,
        )

        return OrderResponse(
            id=order_orm.id,
            title=order_orm.title,
            description=order_orm.description,
            price=order_orm.price,
            term=order_orm.term,
            status=status,
            priority=priority,
            order_type=order_type,
            currency=currency,
            responses=order_orm.responses,
            created_at=order_orm.created_at,
            customer_id=order_orm.customer_id,
            executor_id=order_orm.executor_id,
            category_id=order_orm.category_id,
            category_name=category.name if category else "Без категории",
            customer_name=customer.name if customer else "",
            customer_nickname=customer.nickname if customer else ""
        )

    @staticmethod
    async def get_orders_with_filters(
        category_id: int = None,
        min_price: int = None,
        max_price: int = None,
        status: OrderStatus = None,
        exclude_my_orders: bool = False,
        current_user_id: int = None,
        sort_by: str = "date",
        page: int = 1,
        page_size: int = 15
    ) -> OrderListResponse:
        async with AsyncSessionLocal() as session:
            query = select(OrderORM)
            
            if category_id:
                query = query.where(OrderORM.category_id == category_id)
            if min_price is not None:
                query = query.where(OrderORM.price >= min_price)
            if max_price is not None:
                query = query.where(OrderORM.price <= max_price)
            if status:
                query = query.where(OrderORM.status == status.value)
            if exclude_my_orders and current_user_id:
                query = query.where(OrderORM.customer_id != current_user_id)
            
            if sort_by == "price":
                query = query.order_by(OrderORM.price.desc())
            else:
                query = query.order_by(OrderORM.id.desc())
            
            count_query = query.with_only_columns(OrderORM.id).order_by(None)
            total_orders = (await session.execute(count_query)).scalars().all()
            total_count = len(total_orders)
            
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            result = await session.execute(query)
            order_orms = result.scalars().all()
            
            orders = []
            for order in order_orms:
                customer_result = await session.execute(select(UserORM).where(UserORM.id == order.customer_id))
                customer = customer_result.scalar_one_or_none()
                category_result = await session.execute(select(CategoryORM).where(CategoryORM.id == order.category_id))
                category = category_result.scalar_one_or_none()
                
                order_response = await OrderHandlers.create_order_response(order, customer, category)
                orders.append(order_response)
            
            total_pages = (total_count + page_size - 1) // page_size
            
            return OrderListResponse(
                orders=orders,
                total=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )


