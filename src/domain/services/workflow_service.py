from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositiry.db_models import ContentORM, UserORM
from src.domain.entity.userentity import UserRole
from src.infrastructure.services.content_service import ContentStatus


class WorkflowError(Exception):
    ...


class WorkflowService:
    """Управляет жизненным циклом контента и ролями модерации."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def submit_for_review(self, content_id: int, author_id: int) -> Dict[str, str]:
        content = await self.session.get(ContentORM, content_id)
        if not content:
            raise WorkflowError("Content not found")
        if content.author_id != author_id:
            raise WorkflowError("You can submit only your own content")

        content.status = ContentStatus.PENDING.value
        content.updated_at = datetime.utcnow()
        await self.session.commit()

        return {"status": content.status}

    async def approve(self, content_id: int, editor_id: int) -> Dict[str, str]:
        await self._ensure_editor(editor_id)
        content = await self.session.get(ContentORM, content_id)
        if not content:
            raise WorkflowError("Content not found")

        content.status = ContentStatus.PUBLISHED.value
        content.is_published = True
        content.published_at = datetime.utcnow()
        content.updated_at = datetime.utcnow()
        await self.session.commit()

        return {"status": content.status}

    async def request_changes(self, content_id: int, editor_id: int) -> Dict[str, str]:
        await self._ensure_editor(editor_id)
        content = await self.session.get(ContentORM, content_id)
        if not content:
            raise WorkflowError("Content not found")

        content.status = ContentStatus.DRAFT.value
        content.is_published = False
        content.updated_at = datetime.utcnow()
        await self.session.commit()

        return {"status": content.status}

    async def archive(self, content_id: int, editor_id: int) -> Dict[str, str]:
        await self._ensure_editor(editor_id)
        content = await self.session.get(ContentORM, content_id)
        if not content:
            raise WorkflowError("Content not found")

        content.status = ContentStatus.ARCHIVED.value
        content.is_published = False
        content.updated_at = datetime.utcnow()
        await self.session.commit()

        return {"status": content.status}

    async def assign_editor(self, user_id: int) -> None:
        await self.session.execute(
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(
                is_editor=True,
                role=UserRole.EDITOR.value,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.commit()

    async def revoke_editor(self, user_id: int) -> None:
        await self.session.execute(
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(
                is_editor=False,
                role=UserRole.CUSTOMER.value,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.commit()

    async def list_pending(self, *, limit: int = 20) -> List[ContentORM]:
        stmt = (
            select(ContentORM)
            .where(ContentORM.status == ContentStatus.PENDING.value)
            .order_by(ContentORM.updated_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _ensure_editor(self, user_id: int) -> None:
        user = await self.session.get(UserORM, user_id)
        if not user:
            raise WorkflowError("Editor permissions required")
        raw_role = getattr(user, "role", UserRole.CUSTOMER.value)
        try:
            role = raw_role if isinstance(raw_role, UserRole) else UserRole(str(raw_role))
        except ValueError:
            role = UserRole.CUSTOMER
        if role not in {UserRole.ADMIN, UserRole.EDITOR} and (not user.is_editor and user.nickname != "admin"):
            raise WorkflowError("Editor permissions required")



