from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.infrastructure.services.content_service import ContentService, ContentStatus, ContentType
from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.repositiry.db_models import UserORM
from src.presentation.api.v1.auth import get_current_user, get_admin_user
from src.domain.entity.userentity import UserPrivate, UserRole
from src.infrastructure.dependencies import get_workflow_service
from src.domain.services.workflow_service import WorkflowService, WorkflowError

router = APIRouter(prefix="/content", tags=["Content"])

# Pydantic models
class ContentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=50000)
    type: str = Field(..., description="Type of content: news, article, test, career")
    tags: List[str] = Field(default_factory=list, max_items=10)
    is_published: bool = False

class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=50000)
    tags: Optional[List[str]] = Field(None, max_items=10)
    is_published: Optional[bool] = None

class ContentResponse(BaseModel):
    id: int
    title: str
    content: str
    type: str
    status: str
    tags: List[str]
    author_id: int
    author_name: str
    author_nickname: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    views: int
    likes: int
    is_published: bool

class ContentListResponse(BaseModel):
    content: List[ContentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# Dependency для проверки прав редактора/админа
async def get_editor_user(current_user: UserPrivate = Depends(get_current_user)) -> UserPrivate:
    role_value = getattr(current_user, "role", UserRole.CUSTOMER.value)
    try:
        role = role_value if isinstance(role_value, UserRole) else UserRole(str(role_value))
    except ValueError:
        role = UserRole.CUSTOMER
    if role not in {UserRole.ADMIN, UserRole.EDITOR} and not getattr(current_user, 'is_editor', False):
        raise HTTPException(status_code=403, detail="Editor access required")
    return current_user

@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: UserPrivate = Depends(get_current_user)
):
    if content_data.is_published and current_user.nickname != "admin":
        content_data.is_published = False

    if ContentType.from_value(content_data.type) is None:
        raise HTTPException(status_code=400, detail="Invalid content type")

    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        content_obj = await content_service.create_content(
            title=content_data.title,
            content=content_data.content,
            content_type=content_data.type,
            author_id=current_user.id,
            tags=content_data.tags,
            is_published=content_data.is_published,
        )

    return ContentResponse(**content_obj)

@router.get("/", response_model=ContentListResponse)
async def get_content(
    type: Optional[str] = Query(None, description="Filter by content type: news, article, test, career"),
    status: Optional[str] = Query("published", description="Filter by status: draft, pending, published, rejected"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1, max_length=100)
):
    if type and ContentType.from_value(type) is None:
        raise HTTPException(status_code=400, detail="Invalid content type")

    if status and ContentStatus.from_value(status) is None:
        raise HTTPException(status_code=400, detail="Invalid status")

    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        result = await content_service.get_content_list(
            content_type=type,
            status=status,
            search=search,
            page=page,
            page_size=page_size,
            only_published=(status is None or status.lower() == ContentStatus.PUBLISHED.value),
        )

    return ContentListResponse(**result)

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(content_id: int):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        content_obj = await content_service.get_content_by_id(content_id)
        if not content_obj:
            raise HTTPException(status_code=404, detail="Content not found")

        await content_service.increment_views(content_id)

    return ContentResponse(**content_obj)

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        updated_content = await content_service.update_content(
            content_id=content_id,
            title=content_data.title,
            content=content_data.content,
            tags=content_data.tags,
            is_published=content_data.is_published,
            user_id=current_user.id,
        )

    if not updated_content:
        raise HTTPException(status_code=404, detail="Content not found or access denied")

    return ContentResponse(**updated_content)

@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        success = await content_service.delete_content(content_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found or access denied")

    return {"success": True, "message": "Content deleted successfully"}

@router.post("/{content_id}/like")
async def like_content(
    content_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        result = await content_service.toggle_like(content_id, current_user.id)
    return result

@router.post("/{content_id}/unlike")
async def unlike_content(
    content_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    # В реальном проекте здесь должна быть логика снятия лайка
    return {"success": True, "message": "Content unliked"}

@router.post("/{content_id}/approve")
async def approve_content(
    content_id: int,
    editor_user: UserPrivate = Depends(get_editor_user)
):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        success = await content_service.approve_content(content_id, editor_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found or access denied")

    return {"success": True, "message": "Content approved"}

@router.post("/{content_id}/reject")
async def reject_content(
    content_id: int,
    editor_user: UserPrivate = Depends(get_editor_user)
):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        success = await content_service.reject_content(content_id, editor_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found or access denied")

    return {"success": True, "message": "Content rejected"}


@router.post("/{content_id}/submit")
async def submit_for_review(
    content_id: int,
    current_user: UserPrivate = Depends(get_current_user),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    try:
        result = await workflow_service.submit_for_review(content_id, current_user.id)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, **result}


@router.post("/{content_id}/request_changes")
async def request_changes(
    content_id: int,
    editor_user: UserPrivate = Depends(get_editor_user),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    try:
        result = await workflow_service.request_changes(content_id, editor_user.id)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, **result}


@router.post("/{content_id}/archive")
async def archive_content(
    content_id: int,
    editor_user: UserPrivate = Depends(get_editor_user),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    try:
        result = await workflow_service.archive(content_id, editor_user.id)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, **result}


@router.get("/pending", response_model=ContentListResponse)
async def list_pending_content(
    editor_user: UserPrivate = Depends(get_editor_user),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    async with AsyncSessionLocal() as session:
        content_service = ContentService(session)
        items = await workflow_service.list_pending()
        serialized = []
        for content in items:
            author = await session.get(UserORM, content.author_id)
            serialized.append(content_service._serialize(content, author))
    return ContentListResponse(
        content=serialized,
        total=len(serialized),
        page=1,
        page_size=len(serialized) if serialized else 1,
        total_pages=1,
    )


@router.post("/editors/{user_id}/assign")
async def assign_editor(
    user_id: int,
    admin_user: UserPrivate = Depends(get_admin_user),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    await workflow_service.assign_editor(user_id)
    return {"success": True, "user_id": user_id}


@router.post("/editors/{user_id}/revoke")
async def revoke_editor(
    user_id: int,
    admin_user: UserPrivate = Depends(get_admin_user),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    await workflow_service.revoke_editor(user_id)
    return {"success": True, "user_id": user_id}
