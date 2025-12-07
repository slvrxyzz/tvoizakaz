from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import and_, func, select

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.repositiry.db_models import CategoryORM, OrderORM


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    active_orders_count: int


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
async def list_categories() -> List[CategoryResponse]:
    async with AsyncSessionLocal() as session:
        query = (
            select(
                CategoryORM.id,
                CategoryORM.name,
                CategoryORM.description,
                func.count(OrderORM.id).label("active_orders_count"),
            )
            .outerjoin(
                OrderORM,
                and_(
                    OrderORM.category_id == CategoryORM.id,
                    func.upper(OrderORM.status).in_(["OPEN", "WORK"]),
                ),
            )
            .group_by(CategoryORM.id)
            .order_by(CategoryORM.name.asc())
        )

        result = await session.execute(query)
        rows = result.all()

        return [
            CategoryResponse(
                id=row.id,
                name=row.name,
                description=row.description,
                active_orders_count=int(row.active_orders_count or 0),
            )
            for row in rows
        ]

