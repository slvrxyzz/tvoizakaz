"""Сервис контента, работающий с базой данных."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.infrastructure.repositiry.db_models import ContentLikeORM, ContentORM, UserORM


class ContentType(str, Enum):
    NEWS = "news"
    ARTICLE = "article"
    TEST = "test"
    CAREER = "career"

    @classmethod
    def from_value(cls, value: Optional[str]) -> Optional["ContentType"]:
        if value is None:
            return None
        try:
            return cls(value.lower())
        except ValueError:
            return None


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"

    @classmethod
    def from_value(cls, value: Optional[str]) -> Optional["ContentStatus"]:
        if value is None:
            return None
        try:
            return cls(value.lower())
        except ValueError:
            return None


class ContentService:
    def __init__(self, session: AsyncSession):
        if session is None:
            raise ValueError("AsyncSession is required for ContentService")
        self.session = session

    # region helpers
    @staticmethod
    def _dump_tags(tags: Optional[List[str]]) -> str:
        try:
            return json.dumps(tags or [])
        except (TypeError, ValueError):
            return "[]"

    @staticmethod
    def _load_tags(raw: Optional[str]) -> List[str]:
        if not raw:
            return []
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(item) for item in data]
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
        return []

    @staticmethod
    def _normalize_type(value: str) -> str:
        return value.lower()

    @staticmethod
    def _normalize_status(value: str) -> str:
        return value.lower()

    def _serialize(self, content: ContentORM, author: Optional[UserORM]) -> Dict[str, Any]:
        return {
            "id": content.id,
            "title": content.title,
            "content": content.content,
            "type": content.type,
            "status": content.status,
            "tags": self._load_tags(content.tags),
            "author_id": content.author_id,
            "author_name": author.name if author else "",
            "author_nickname": author.nickname if author else "",
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            "published_at": content.published_at,
            "views": content.views,
            "likes": content.likes,
            "is_published": content.is_published,
        }

    # endregion

    async def create_content(
        self,
        title: str,
        content: str,
        content_type: str,
        author_id: int,
        tags: Optional[List[str]] = None,
        is_published: bool = False,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        normalized_type = self._normalize_type(content_type)
        status = ContentStatus.PUBLISHED.value if is_published else ContentStatus.DRAFT.value

        new_content = ContentORM(
            title=title,
            content=content,
            type=normalized_type,
            status=status,
            tags=self._dump_tags(tags),
            author_id=author_id,
            created_at=now,
            updated_at=now,
            published_at=now if is_published else None,
            is_published=is_published,
        )

        self.session.add(new_content)
        await self.session.commit()
        await self.session.refresh(new_content)

        author = await self.session.get(UserORM, author_id)
        return self._serialize(new_content, author)

    async def get_content_list(
        self,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        only_published: bool = False,
    ) -> Dict[str, Any]:
        filters = []
        if content_type:
            filters.append(ContentORM.type == self._normalize_type(content_type))
        if status:
            filters.append(ContentORM.status == self._normalize_status(status))
        if only_published:
            filters.append(ContentORM.is_published.is_(True))
        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(
                    ContentORM.title.ilike(pattern),
                    ContentORM.content.ilike(pattern),
                )
            )

        where_clause = and_(*filters) if filters else None

        count_stmt = select(func.count(ContentORM.id))
        if where_clause is not None:
            count_stmt = count_stmt.where(where_clause)

        total = (await self.session.execute(count_stmt)).scalar_one()

        data_stmt = (
            select(ContentORM, UserORM)
            .join(UserORM, ContentORM.author_id == UserORM.id)
            .order_by(ContentORM.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        if where_clause is not None:
            data_stmt = data_stmt.where(where_clause)

        rows = await self.session.execute(data_stmt)
        items = [self._serialize(content, author) for content, author in rows]

        return {
            "content": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size else 1,
        }

    async def get_content_by_id(self, content_id: int) -> Optional[Dict[str, Any]]:
        stmt = (
            select(ContentORM, UserORM)
            .join(UserORM, ContentORM.author_id == UserORM.id)
            .where(ContentORM.id == content_id)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if not row:
            return None
        content, author = row
        return self._serialize(content, author)

    async def increment_views(self, content_id: int) -> None:
        result = await self.session.execute(
            select(ContentORM).where(ContentORM.id == content_id).with_for_update()
        )
        content = result.scalar_one_or_none()
        if content:
            content.views += 1
            content.updated_at = datetime.utcnow()
            await self.session.commit()

    async def update_content(
        self,
        content_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_published: Optional[bool] = None,
        user_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        content_obj = await self.session.get(ContentORM, content_id)
        if not content_obj:
            return None

        if user_id is not None and user_id != content_obj.author_id:
            author = await self.session.get(UserORM, user_id)
            if not author or author.nickname != "admin":
                return None

        if title is not None:
            content_obj.title = title
        if content is not None:
            content_obj.content = content
        if tags is not None:
            content_obj.tags = self._dump_tags(tags)
        if is_published is not None:
            content_obj.is_published = is_published
            content_obj.status = ContentStatus.PUBLISHED.value if is_published else ContentStatus.DRAFT.value
            content_obj.published_at = datetime.utcnow() if is_published else None

        content_obj.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(content_obj)
        author = await self.session.get(UserORM, content_obj.author_id)
        return self._serialize(content_obj, author)

    async def delete_content(self, content_id: int, user_id: int) -> bool:
        content_obj = await self.session.get(ContentORM, content_id)
        if not content_obj:
            return False

        author = await self.session.get(UserORM, user_id)
        if user_id != content_obj.author_id and (not author or author.nickname != "admin"):
            return False

        await self.session.delete(content_obj)
        await self.session.commit()
        return True

    async def toggle_like(self, content_id: int, user_id: int) -> Dict[str, Any]:
        content_obj = await self.session.get(ContentORM, content_id)
        if not content_obj:
            return {"success": False, "message": "Content not found"}

        like_stmt = (
            select(ContentLikeORM)
            .where(ContentLikeORM.content_id == content_id, ContentLikeORM.user_id == user_id)
            .with_for_update()
        )
        like_result = await self.session.execute(like_stmt)
        like = like_result.scalar_one_or_none()

        liked = False
        if like:
            await self.session.delete(like)
            content_obj.likes = max(0, content_obj.likes - 1)
        else:
            new_like = ContentLikeORM(content_id=content_id, user_id=user_id)
            self.session.add(new_like)
            content_obj.likes += 1
            liked = True

        content_obj.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(content_obj)

        return {"success": True, "liked": liked, "likes": content_obj.likes}

    async def approve_content(self, content_id: int, editor_id: int) -> bool:
        content_obj = await self.session.get(ContentORM, content_id)
        if not content_obj:
            return False

        content_obj.status = ContentStatus.PUBLISHED.value
        content_obj.is_published = True
        content_obj.published_at = datetime.utcnow()
        content_obj.updated_at = datetime.utcnow()
        await self.session.commit()
        return True

    async def reject_content(self, content_id: int, editor_id: int) -> bool:
        content_obj = await self.session.get(ContentORM, content_id)
        if not content_obj:
            return False

        content_obj.status = ContentStatus.REJECTED.value
        content_obj.is_published = False
        content_obj.updated_at = datetime.utcnow()
        await self.session.commit()
        return True
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
