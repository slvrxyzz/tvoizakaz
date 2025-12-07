#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket чаты для TeenFreelance API
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
from collections import defaultdict
from http.cookies import SimpleCookie

from jose import JWTError

from src.infrastructure.monitoring.logger import logger
from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.auth_service import decode_access_token
from src.infrastructure.services.chat_service import ChatService
from src.infrastructure.services.message_service import MessageService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.repositiry.db_models import ChatORM, MessageORM, UserORM
from sqlalchemy import select
from src.domain.entity.userentity import UserPrivate
from src.presentation.api.v1.auth import get_current_user
from src.infrastructure.security.content_filter import ContentRejectedError

router = APIRouter(prefix="/ws", tags=["WebSocket Chats"])

# Переходная таблица типов сообщений для обратной совместимости
MESSAGE_TYPE_ALIASES = {
    "join_chat": "join_chat",
    "joinChat": "join_chat",
    "leave_chat": "leave_chat",
    "leaveChat": "leave_chat",
    "send_message": "send_message",
    "sendMessage": "send_message",
    "chat_message": "send_message",
    "message": "send_message",
    "get_chats": "get_chats",
    "getChats": "get_chats",
    "get_messages": "get_messages",
    "getMessages": "get_messages",
    "ping": "ping",
}

# Pydantic модели для WebSocket
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    chat_id: Optional[int] = None
    message_id: Optional[int] = None

class WSMessageData(BaseModel):
    text: str
    sender_id: int
    sender_name: str
    sender_nickname: str
    created_at: str
    type: Optional[str] = None
    order_id: Optional[int] = None
    offer_price: Optional[int] = None

class WSChatData(BaseModel):
    id: int
    customer_id: int
    executor_id: int
    customer_name: str
    customer_nickname: str
    executor_name: str
    executor_nickname: str
    created_at: str
    last_message: Optional[WSMessageData] = None

# Менеджер WebSocket соединений
class ConnectionManager:
    def __init__(self):
        # Словарь для хранения активных соединений по user_id
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)
        # Словарь для хранения соединений по chat_id
        self.chat_connections: Dict[int, List[WebSocket]] = defaultdict(list)
        # Словарь для хранения user_id по websocket
        self.websocket_users: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение пользователя к WebSocket"""
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        self.websocket_users[websocket] = user_id
        
        # Отправляем подтверждение подключения
        await self.send_personal_message({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

    def disconnect(self, websocket: WebSocket):
        """Отключение пользователя от WebSocket"""
        if websocket in self.websocket_users:
            user_id = self.websocket_users[websocket]
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            del self.websocket_users[websocket]

        for chat_id, sockets in list(self.chat_connections.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    del self.chat_connections[chat_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Отправка сообщения конкретному WebSocket"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as exc:
            logger.warning("WebSocket send failed", error=str(exc))

    async def send_to_user(self, message: dict, user_id: int):
        """Отправка сообщения всем соединениям пользователя"""
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                await self.send_personal_message(message, websocket)

    async def send_to_chat(self, message: dict, chat_id: int, exclude_user: Optional[int] = None):
        """Отправка сообщения всем участникам чата"""
        if chat_id in self.chat_connections:
            for websocket in self.chat_connections[chat_id]:
                if exclude_user and self.websocket_users.get(websocket) == exclude_user:
                    continue
                await self.send_personal_message(message, websocket)

    def add_to_chat(self, websocket: WebSocket, chat_id: int):
        """Добавление соединения к чату"""
        self.chat_connections[chat_id].append(websocket)

    def remove_from_chat(self, websocket: WebSocket, chat_id: int):
        """Удаление соединения из чата"""
        if websocket in self.chat_connections[chat_id]:
            self.chat_connections[chat_id].remove(websocket)

# Глобальный менеджер соединений
manager = ConnectionManager()

def get_user_from_token(token: str) -> Optional[int]:
    """Получение user_id из JWT токена"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id:
            return int(user_id)
        return None
    except JWTError as exc:
        logger.warning("WebSocket token decode error", error=str(exc))
        return None
    except Exception as exc:
        logger.error("WebSocket token unexpected error", error=str(exc))
        return None

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Основной WebSocket эндпоинт для чатов"""
    token: Optional[str] = None

    # Проверяем query параметры (обратная совместимость)
    query_params = dict(websocket.query_params)
    token = query_params.get('token')

    # Пытаемся извлечь из cookie (предпочтительный способ)
    if not token:
        cookie_header = websocket.headers.get("cookie")
        if cookie_header:
            cookies = SimpleCookie()
            cookies.load(cookie_header)
            if cookies.get("access_token"):
                token = cookies["access_token"].value

    # Если не нашли в cookie, проверяем заголовок Authorization
    if not token:
        auth_header = websocket.headers.get('authorization') or websocket.headers.get('Authorization', '')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')

    if not token:
        logger.warning("WebSocket authentication failed: missing token", endpoint="/api/v1/ws/chat")
        await websocket.close(code=1008, reason="No token provided")
        return

    user_id = get_user_from_token(token)
    if not user_id:
        logger.warning("WebSocket authentication failed", token_preview=token[:8])
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect(websocket, user_id)
    logger.info("WebSocket connected", user_id=user_id, endpoint="/api/v1/ws/chat")

    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обрабатываем сообщение
            await handle_websocket_message(websocket, user_id, message_data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected", user_id=user_id, endpoint="/api/v1/ws/chat")
    except Exception as e:
        logger.error("WebSocket error", error=str(e), user_id=user_id)
        manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка WebSocket сообщений"""
    message_type = message_data.get("type")
    normalized_type = MESSAGE_TYPE_ALIASES.get(message_type, message_type)

    if normalized_type == "join_chat":
        await handle_join_chat(websocket, user_id, message_data)
    elif normalized_type == "leave_chat":
        await handle_leave_chat(websocket, user_id, message_data)
    elif normalized_type == "send_message":
        await handle_send_message(websocket, user_id, message_data)
    elif normalized_type == "get_chats":
        await handle_get_chats(websocket, user_id, message_data)
    elif normalized_type == "get_messages":
        await handle_get_messages(websocket, user_id, message_data)
    elif normalized_type == "ping":
        await handle_ping(websocket, user_id, message_data)
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, websocket)

async def handle_join_chat(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка подключения к чату"""
    payload = message_data.get("data") if isinstance(message_data.get("data"), dict) else message_data
    chat_id = payload.get("chat_id") or payload.get("chatId")
    if not chat_id:
        await manager.send_personal_message({
            "type": "error",
            "message": "chat_id is required"
        }, websocket)
        return

    # Проверяем доступ к чату
    async with AsyncSessionLocal() as session:
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != user_id and chat.executor_id != user_id):
            await manager.send_personal_message({
                "type": "error",
                "message": "Access denied to chat"
            }, websocket)
            return

    # Добавляем соединение к чату
    manager.add_to_chat(websocket, chat_id)
    
    await manager.send_personal_message({
        "type": "chat_joined",
        "chat_id": chat_id
    }, websocket)

async def handle_leave_chat(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка отключения от чата"""
    payload = message_data.get("data") if isinstance(message_data.get("data"), dict) else message_data
    chat_id = payload.get("chat_id") or payload.get("chatId")
    if chat_id:
        manager.remove_from_chat(websocket, chat_id)
        
        await manager.send_personal_message({
            "type": "chat_left",
            "chat_id": chat_id
        }, websocket)

async def handle_send_message(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка отправки сообщения"""
    payload = message_data.get("data") if isinstance(message_data.get("data"), dict) else message_data
    chat_id = payload.get("chat_id") or payload.get("chatId")
    text = payload.get("text") or payload.get("message")
    
    if not chat_id or not text:
        await manager.send_personal_message({
            "type": "error",
            "message": "chat_id and text are required"
        }, websocket)
        return

    async with AsyncSessionLocal() as session:
        message_service = MessageService(session)
        user_service = UserService(session)
        
        # Проверяем доступ к чату
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != user_id and chat.executor_id != user_id):
            await manager.send_personal_message({
                "type": "error",
                "message": "Access denied to chat"
            }, websocket)
            return

        # Отправляем сообщение
        message = await message_service.send_message(chat_id, user_id, text)
        user = await user_service.get_user_by_id(user_id)
        
        # Формируем данные сообщения
        message_response = {
            "id": message.id,
            "text": message.content,
            "sender_id": message.sender_id,
            "sender_name": user.name if user else "",
            "sender_nickname": user.nickname if user else "",
            "created_at": message.created_at.isoformat(),
            "type": getattr(message, 'type', None),
            "order_id": getattr(message, 'order_id', None),
            "offer_price": getattr(message, 'offer_price', None)
        }
        
        # Отправляем сообщение всем участникам чата
        await manager.send_to_chat({
            "type": "new_message",
            "chat_id": chat_id,
            "message": message_response
        }, chat_id)

async def handle_get_chats(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка получения списка чатов"""
    async with AsyncSessionLocal() as session:
        chat_service = ChatService(session)
        user_service = UserService(session)
        message_service = MessageService(session)
        
        chat_orms = await chat_service.get_user_chats(user_id)
        chats = []
        
        for chat in chat_orms:
            other_id = chat.executor_id if chat.customer_id == user_id else chat.customer_id
            other = await user_service.get_user_by_id(other_id)
            customer = await user_service.get_user_by_id(chat.customer_id)
            executor = await user_service.get_user_by_id(chat.executor_id)
            
            # Получаем последнее сообщение
            messages = await message_service.get_messages(chat.id)
            last_message = None
            if messages:
                last_msg = messages[-1]
                sender = await user_service.get_user_by_id(last_msg.sender_id)
                last_message = {
                    "id": last_msg.id,
                    "text": last_msg.content,
                    "sender_id": last_msg.sender_id,
                    "sender_name": sender.name if sender else "",
                    "sender_nickname": sender.nickname if sender else "",
                    "created_at": last_msg.created_at.isoformat(),
                    "type": getattr(last_msg, 'type', None),
                    "order_id": getattr(last_msg, 'order_id', None),
                    "offer_price": getattr(last_msg, 'offer_price', None)
                }
            
            chats.append({
                "id": chat.id,
                "customer_id": chat.customer_id,
                "executor_id": chat.executor_id,
                "customer_name": customer.name if customer else "",
                "customer_nickname": customer.nickname if customer else "",
                "executor_name": executor.name if executor else "",
                "executor_nickname": executor.nickname if executor else "",
                "created_at": chat.created_at.isoformat(),
                "last_message": last_message
            })
        
        await manager.send_personal_message({
            "type": "chats",
            "chats": chats
        }, websocket)

async def handle_get_messages(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка получения сообщений чата"""
    payload = message_data.get("data") if isinstance(message_data.get("data"), dict) else message_data
    chat_id = payload.get("chat_id") or payload.get("chatId")
    after_id_raw = payload.get("after_id") or payload.get("afterId", 0)
    try:
        after_id = int(after_id_raw)
    except (TypeError, ValueError):
        after_id = 0
    
    if not chat_id:
        await manager.send_personal_message({
            "type": "error",
            "message": "chat_id is required"
        }, websocket)
        return

    async with AsyncSessionLocal() as session:
        message_service = MessageService(session)
        user_service = UserService(session)
        
        # Проверяем доступ к чату
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != user_id and chat.executor_id != user_id):
            await manager.send_personal_message({
                "type": "error",
                "message": "Access denied to chat"
            }, websocket)
            return

        messages = await message_service.get_messages(chat_id)
        
        # Фильтруем только новые сообщения
        new_messages = []
        for m in messages:
            if m.id > after_id and getattr(m, 'type', None) != 'offer':
                sender = await user_service.get_user_by_id(m.sender_id)
                new_messages.append({
                    "id": m.id,
                    "text": m.content,
                    "sender_id": m.sender_id,
                    "sender_name": sender.name if sender else "",
                    "sender_nickname": sender.nickname if sender else "",
                    "created_at": m.created_at.isoformat(),
                    "type": getattr(m, 'type', None),
                    "order_id": getattr(m, 'order_id', None),
                    "offer_price": getattr(m, 'offer_price', None)
                })
        
        await manager.send_personal_message({
            "type": "messages",
            "chat_id": chat_id,
            "messages": new_messages
        }, websocket)

async def handle_ping(websocket: WebSocket, user_id: int, message_data: dict):
    """Обработка ping сообщения"""
    await manager.send_personal_message({
        "type": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }, websocket)

# HTTP эндпоинты для совместимости
@router.get("/chats")
async def get_user_chats_http(current_user: UserPrivate = Depends(get_current_user)):
    """HTTP эндпоинт для получения чатов (для совместимости)"""
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
            customer = await user_service.get_user_by_id(chat.customer_id)
            executor = await user_service.get_user_by_id(chat.executor_id)
            
            # Получаем последнее сообщение
            messages = await message_service.get_messages(chat.id)
            last_message = None
            if messages:
                last_msg = messages[-1]
                sender = await user_service.get_user_by_id(last_msg.sender_id)
                last_message = {
                    "id": last_msg.id,
                    "text": last_msg.content,
                    "sender_id": last_msg.sender_id,
                    "sender_name": sender.name if sender else "",
                    "sender_nickname": sender.nickname if sender else "",
                    "created_at": last_msg.created_at.isoformat(),
                    "type": getattr(last_msg, 'type', None),
                    "order_id": getattr(last_msg, 'order_id', None),
                    "offer_price": getattr(last_msg, 'offer_price', None)
                }
            
            chats.append({
                "id": chat.id,
                "customer_id": chat.customer_id,
                "executor_id": chat.executor_id,
                "customer_name": customer.name if customer else "",
                "customer_nickname": customer.nickname if customer else "",
                "executor_name": executor.name if executor else "",
                "executor_nickname": executor.nickname if executor else "",
                "created_at": chat.created_at.isoformat(),
                "last_message": last_message
            })
        
        return {"chats": chats}

@router.post("/chats/start/{user_id}")
async def start_chat_http(user_id: int, current_user: UserPrivate = Depends(get_current_user)):
    """HTTP эндпоинт для создания чата (для совместимости)"""
    async with AsyncSessionLocal() as session:
        chat_service = ChatService(session)
        
        chat = await chat_service.get_or_create_chat_between_users(current_user.id, user_id)
        
        return {"chat_id": chat.id}

