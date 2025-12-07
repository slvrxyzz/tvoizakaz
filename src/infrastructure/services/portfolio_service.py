from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import PortfolioItemORM


class PortfolioService:
    """Управление работами пользователя в портфолио."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: int, *, limit: int | None = None) -> List[PortfolioItemORM]:
        stmt = (
            select(PortfolioItemORM)
            .where(PortfolioItemORM.user_id == user_id)
            .order_by(PortfolioItemORM.created_at.desc())
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_item(self, item_id: int) -> Optional[PortfolioItemORM]:
        result = await self.session.execute(
            select(PortfolioItemORM).where(PortfolioItemORM.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create_item(
        self,
        *,
        user_id: int,
        title: str,
        description: Optional[str],
        media_url: Optional[str],
        attachment_url: Optional[str],
        tags: Optional[str],
        is_featured: bool,
    ) -> PortfolioItemORM:
        item = PortfolioItemORM(
            user_id=user_id,
            title=title,
            description=description,
            media_url=media_url,
            attachment_url=attachment_url,
            tags=tags,
            is_featured=is_featured,
            created_at=datetime.utcnow(),
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update_item(
        self,
        item_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        media_url: Optional[str] = None,
        attachment_url: Optional[str] = None,
        tags: Optional[str] = None,
        is_featured: Optional[bool] = None,
    ) -> Optional[PortfolioItemORM]:
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if media_url is not None:
            data["media_url"] = media_url
        if attachment_url is not None:
            data["attachment_url"] = attachment_url
        if tags is not None:
            data["tags"] = tags
        if is_featured is not None:
            data["is_featured"] = is_featured
        if not data:
            return await self.get_item(item_id)

        data["updated_at"] = datetime.utcnow()

        await self.session.execute(
            update(PortfolioItemORM)
            .where(PortfolioItemORM.id == item_id)
            .values(**data)
        )
        await self.session.commit()
        return await self.get_item(item_id)

    async def delete_item(self, item_id: int) -> None:
        await self.session.execute(
            delete(PortfolioItemORM).where(PortfolioItemORM.id == item_id)
        )
        await self.session.commit()


