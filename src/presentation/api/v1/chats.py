from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.chat_service import ChatService
from src.infrastructure.services.message_service import MessageService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.repositiry.db_models import ChatORM, MessageORM, UserORM
from sqlalchemy import select
from src.presentation.api.v1.auth import get_current_user
from src.domain.entity.userentity import UserPrivate
from src.infrastructure.security.content_filter import ContentRejectedError

router = APIRouter(prefix="/chats", tags=["Chats"])

# Pydantic models
class MessageCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    message_type: Optional[str] = None  # Соответствует MessageCreateDTO фронтенда
    file_name: Optional[str] = None
    file_size: Optional[int] = None

class MessageResponse(BaseModel):
    id: int
    text: str
    sender_id: int
    sender_name: str
    sender_nickname: str
    created_at: datetime
    type: Optional[str] = None
    order_id: Optional[int] = None
    offer_price: Optional[int] = None
    # Опциональные поля для полной версии MessageDTO
    chat_id: Optional[int] = None
    message_type: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_edited: Optional[bool] = False
    is_deleted: Optional[bool] = False
    edited_at: Optional[datetime] = None

class ChatResponse(BaseModel):
    id: int
    customer_id: int
    executor_id: int
    customer_name: str
    customer_nickname: str
    executor_name: str
    executor_nickname: str
    created_at: datetime
    last_message: Optional[MessageResponse] = None

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]

@router.get("/", response_model=ChatListResponse)
async def get_user_chats(current_user: UserPrivate = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        chat_service = ChatService(session)
        user_service = UserService(session)
        message_service = MessageService(session)
        
        chat_orms = await chat_service.get_user_chats(current_user.id)
        chats = []
        
        for chat in chat_orms:
            if chat.customer_id == current_user.id:
                other_id = chat.executor_id
            else:
                other_id = chat.customer_id
            
            other = await user_service.get_user_by_id(other_id)
            other_name = other.nickname if other else "Пользователь"
            
            messages = await message_service.get_messages(chat.id)
            last_message = None
            if messages:
                last_msg = messages[-1]
                sender = await user_service.get_user_by_id(last_msg.sender_id)
                last_message = MessageResponse(
                    id=last_msg.id,
                    text=last_msg.content,
                    sender_id=last_msg.sender_id,
                    sender_name=sender.name if sender else "",
                    sender_nickname=sender.nickname if sender else "",
                    created_at=last_msg.created_at,
                    type=getattr(last_msg, 'type', None),
                    order_id=getattr(last_msg, 'order_id', None),
                    offer_price=getattr(last_msg, 'offer_price', None)
                )
            
            customer = await user_service.get_user_by_id(chat.customer_id)
            executor = await user_service.get_user_by_id(chat.executor_id)
            
            chats.append(ChatResponse(
                id=chat.id,
                customer_id=chat.customer_id,
                executor_id=chat.executor_id,
                customer_name=customer.name if customer else "",
                customer_nickname=customer.nickname if customer else "",
                executor_name=executor.name if executor else "",
                executor_nickname=executor.nickname if executor else "",
                created_at=chat.created_at,
                last_message=last_message
            ))
        
        return ChatListResponse(chats=chats)

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    after_id: int = Query(0),
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        message_service = MessageService(session)
        user_service = UserService(session)
        
        # Проверяем, что пользователь имеет доступ к чату
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != current_user.id and chat.executor_id != current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = await message_service.get_messages(chat_id)
        
        # Фильтруем только новые сообщения
        # Если after_id=0, возвращаем все сообщения (включая offer)
        new_messages = []
        for m in messages:
            if m.id > after_id:
                # Если after_id=0, включаем все сообщения, иначе исключаем offer
                if after_id == 0 or getattr(m, 'type', None) != 'offer':
                    sender = await user_service.get_user_by_id(m.sender_id)
                    new_messages.append(
                        MessageResponse(
                            id=m.id,
                            text=m.content,
                            sender_id=m.sender_id,
                            sender_name=sender.name if sender else "",
                            sender_nickname=sender.nickname if sender else "",
                            created_at=m.created_at,
                            type=getattr(m, 'type', None),
                            order_id=getattr(m, 'order_id', None),
                            offer_price=getattr(m, 'offer_price', None),
                        )
                    )
        
        return new_messages

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        message_service = MessageService(session)
        user_service = UserService(session)
        
        # Проверяем, что пользователь имеет доступ к чату
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != current_user.id and chat.executor_id != current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        user = await user_service.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        try:
            message = await message_service.send_message(chat_id, user.id, message_data.text)
        except ContentRejectedError as exc:
            raise HTTPException(status_code=400, detail="Сообщение отклонено автоматической модерацией") from exc
        
        return MessageResponse(
            id=message.id,
            text=message.content,
            sender_id=message.sender_id,
            sender_name=user.name,
            sender_nickname=user.nickname,
            created_at=message.created_at,
            type=getattr(message, 'type', None),
            order_id=getattr(message, 'order_id', None),
            offer_price=getattr(message, 'offer_price', None),
        )

@router.post("/start/{user_id}")
async def start_chat(
    user_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        chat_service = ChatService(session)
        
        chat = await chat_service.get_or_create_chat_between_users(current_user.id, user_id)
        
        return {"chat_id": chat.id}
