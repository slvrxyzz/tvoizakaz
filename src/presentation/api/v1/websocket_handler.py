#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket обработчик для чатов
"""

import json
import jwt
import asyncio
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.chat_service import ChatService
from src.infrastructure.repositiry.message_repository import MessageRepository
from src.infrastructure.services.message_service import MessageService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.repositiry.db_models import ChatORM
from sqlalchemy import select
from src.infrastructure.security.content_filter import ContentRejectedError

# Секретный ключ для JWT (должен совпадать с auth.py)
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

class ConnectionManager:
    def __init__(self):
        # Словарь для хранения активных соединений по user_id
        self.active_connections: Dict[int, List] = defaultdict(list)
        # Словарь для хранения соединений по chat_id
        self.chat_connections: Dict[int, List] = defaultdict(list)
        # Словарь для хранения user_id по websocket
        self.websocket_users: Dict = {}

    async def connect(self, websocket, user_id: int):
        """Подключение пользователя к WebSocket"""
        # websocket.accept() уже вызван в main.py
        print(f"WebSocket: Connecting user {user_id}")
        self.active_connections[user_id].append(websocket)
        self.websocket_users[websocket] = user_id
        
        # Отправляем подтверждение подключения
        await self.send_personal_message({
            "type": "connection_established",
            "data": {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)
        print(f"WebSocket: User {user_id} connected successfully")

    def disconnect(self, websocket):
        """Отключение пользователя от WebSocket"""
        if websocket in self.websocket_users:
            user_id = self.websocket_users[websocket]
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            del self.websocket_users[websocket]

    async def send_personal_message(self, message: dict, websocket):
        """Отправка сообщения конкретному WebSocket"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
            print(f"WebSocket: Message sent successfully: {message.get('type')}")
        except Exception as e:
            print(f"WebSocket: Error sending message: {e}")

    async def send_to_user(self, message: dict, user_id: int):
        """Отправка сообщения всем соединениям пользователя"""
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                await self.send_personal_message(message, websocket)

    async def send_to_chat(self, message: dict, chat_id: int, exclude_user: Optional[int] = None):
        """Отправка сообщения всем участникам чата"""
        # Получаем участников чата из базы данных
        from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
        from src.infrastructure.repositiry.db_models import ChatORM
        from sqlalchemy import select
        
        try:
            async with AsyncSessionLocal() as session:
                chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
                chat = chat_result.scalar_one_or_none()
                
                if chat:
                    print(f"WebSocket: Found chat {chat_id} with participants {chat.customer_id}, {chat.executor_id}")
                    print(f"WebSocket: Active connections: {list(self.active_connections.keys())}")
                    # Отправляем сообщение всем участникам чата
                    for user_id in [chat.customer_id, chat.executor_id]:
                        if user_id != exclude_user and user_id in self.active_connections:
                            print(f"WebSocket: Sending to user {user_id}")
                            for websocket in self.active_connections[user_id]:
                                await self.send_personal_message(message, websocket)
                        else:
                            print(f"WebSocket: User {user_id} not active or excluded (exclude_user: {exclude_user})")
                else:
                    print(f"WebSocket: Chat {chat_id} not found")
        except Exception as e:
            print(f"WebSocket: Error in send_to_chat: {e}")

    def add_to_chat(self, websocket, chat_id: int):
        """Добавление соединения к чату"""
        self.chat_connections[chat_id].append(websocket)

    def remove_from_chat(self, websocket, chat_id: int):
        """Удаление соединения из чата"""
        if websocket in self.chat_connections[chat_id]:
            self.chat_connections[chat_id].remove(websocket)
    
    async def send_chat_created_notification(self, chat_id: int, customer_id: int, executor_id: int):
        """Отправка уведомления о создании чата"""
        # Получаем информацию о чате из базы данных
        async with AsyncSessionLocal() as session:
            chat_service = ChatService(session)
            chat = await chat_service.get_chat_by_id(chat_id)
            
            if chat:
                # Отправляем уведомление всем участникам чата
                for user_id in [customer_id, executor_id]:
                    if user_id in self.active_connections:
                        for websocket in self.active_connections[user_id]:
                            try:
                                await self.send_personal_message({
                                    "type": "chat_created",
                                    "data": {
                                        "id": chat.id,
                                        "customer_id": chat.customer_id,
                                        "executor_id": chat.executor_id,
                                        "customer_name": chat.customer_name,
                                        "customer_nickname": chat.customer_nickname,
                                        "executor_name": chat.executor_name,
                                        "executor_nickname": chat.executor_nickname,
                                        "created_at": chat.created_at.isoformat()
                                    }
                                }, websocket)
                            except Exception as e:
                                print(f"Error sending chat_created notification: {e}")

# Глобальный менеджер соединений
manager = ConnectionManager()

def get_user_from_token(token: str) -> Optional[int]:
    """Получение user_id из JWT токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except:
        return None

async def handle_websocket_message(websocket, user_id: int, message_data: dict):
    """Обработка WebSocket сообщений"""
    message_type = message_data.get("type")
    print(f"WebSocket: Received message from user {user_id}, type: {message_type}")
    
    if message_type == "join_chat":
        await handle_join_chat(websocket, user_id, message_data)
    elif message_type == "leave_chat":
        await handle_leave_chat(websocket, user_id, message_data)
    elif message_type == "send_message":
        await handle_send_message(websocket, user_id, message_data)
    elif message_type == "get_chats":
        await handle_get_chats(websocket, user_id, message_data)
    elif message_type == "get_messages":
        await handle_get_messages(websocket, user_id, message_data)
    elif message_type == "ping":
        await handle_ping(websocket, user_id, message_data)
    else:
        print(f"WebSocket: Unknown message type: {message_type}")
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": f"Unknown message type: {message_type}"}
        }, websocket)

async def handle_join_chat(websocket, user_id: int, message_data: dict):
    """Обработка подключения к чату"""
    chat_id = message_data.get("data", {}).get("chat_id")
    if not chat_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "chat_id is required"}
        }, websocket)
        return

    # Проверяем доступ к чату
    async with AsyncSessionLocal() as session:
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != user_id and chat.executor_id != user_id):
            await manager.send_personal_message({
                "type": "error",
                "data": {"message": "Access denied to chat"}
            }, websocket)
            return

    # Добавляем соединение к чату
    manager.add_to_chat(websocket, chat_id)
    
    await manager.send_personal_message({
        "type": "chat_joined",
        "data": {"chat_id": chat_id}
    }, websocket)

async def handle_leave_chat(websocket, user_id: int, message_data: dict):
    """Обработка отключения от чата"""
    chat_id = message_data.get("data", {}).get("chat_id")
    if chat_id:
        manager.remove_from_chat(websocket, chat_id)
        
        await manager.send_personal_message({
            "type": "chat_left",
            "data": {"chat_id": chat_id}
        }, websocket)

async def handle_send_message(websocket, user_id: int, message_data: dict):
    """Обработка отправки сообщения"""
    data = message_data.get("data", {})
    chat_id = data.get("chat_id")
    target_user_id = data.get("user_id")
    text = data.get("text")
    
    print(f"WebSocket: Sending message from user {user_id}, chat_id: {chat_id}, target_user_id: {target_user_id}, text: {text[:50]}...")
    
    if not text:
        print("WebSocket: No text provided")
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "text is required"}
        }, websocket)
        return

    async with AsyncSessionLocal() as session:
        message_repo = MessageRepository(session)
        message_service = MessageService(message_repo)
        user_service = UserService(session)
        chat_service = ChatService(session)
        
        # Если передан user_id, создаем или находим чат с этим пользователем
        if target_user_id:
            # Создаем или находим чат между пользователями
            chat = await chat_service.get_or_create_chat_between_users(user_id, target_user_id)
            chat_id = chat.id
            
            # Отправляем обновленный список чатов всем участникам
            await send_updated_chats_to_users([user_id, target_user_id], session)
        
        # Если chat_id не найден, возвращаем ошибку
        if not chat_id:
            await manager.send_personal_message({
                "type": "error",
                "data": {"message": "chat_id or user_id is required"}
            }, websocket)
            return
        
        # Проверяем доступ к чату
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != user_id and chat.executor_id != user_id):
            await manager.send_personal_message({
                "type": "error",
                "data": {"message": "Access denied to chat"}
            }, websocket)
            return

        # Отправляем сообщение
        try:
            message = await message_service.send_message(chat_id, user_id, text)
        except ContentRejectedError as exc:
            await manager.send_personal_message({
                "type": "moderation",
                "data": {
                    "message": "Сообщение отклонено автоматической модерацией",
                    "sanitized": exc.sanitized_text
                }
            }, websocket)
            return
        user = await user_service.get_user_by_id(user_id)
        
        # Формируем данные сообщения
        message_response = {
            "id": message.id,
            "text": message.content,
            "sender_id": message.sender_id,
            "sender_name": user.name if user else "",
            "sender_nickname": user.nickname if user else "",
            "created_at": message.created_at.isoformat(),
            "type": getattr(message, 'message_type', None),
            "order_id": getattr(message, 'order_id', None),
            "offer_price": getattr(message, 'offer_price', None)
        }
        
        # Отправляем сообщение всем участникам чата
        print(f"WebSocket: Sending message to chat {chat_id}")
        
        # Отправляем сообщение отправителю
        message_sent_data = message_response.copy()
        message_sent_data["chat_id"] = chat_id
        await manager.send_personal_message({
            "type": "message_sent",
            "data": message_sent_data
        }, websocket)
        print(f"WebSocket: Message sent to sender")
        
        # Отправляем сообщение другим участникам чата
        new_message_data = message_response.copy()
        new_message_data["chat_id"] = chat_id
        await manager.send_to_chat({
            "type": "new_message",
            "data": new_message_data
        }, chat_id, exclude_user=user_id)
        print(f"WebSocket: Message sent to other participants")
        
        # Пока что не обновляем список чатов, чтобы избежать ошибок
        print(f"WebSocket: Message processing completed for chat {chat_id}")

async def handle_get_chats(websocket, user_id: int, message_data: dict):
    """Обработка получения списка чатов"""
    async with AsyncSessionLocal() as session:
        chat_service = ChatService(session)
        user_service = UserService(session)
        message_repo = MessageRepository(session)
        message_service = MessageService(message_repo)
        
        chat_orms = await chat_service.get_user_chats(user_id)
        chats = []
        
        for chat in chat_orms:
            if chat.user1_id == user_id:
                other_id = chat.user2_id
            else:
                other_id = chat.user1_id
            
            other = await user_service.get_user_by_id(other_id)
            customer = await user_service.get_user_by_id(chat.user1_id)
            executor = await user_service.get_user_by_id(chat.user2_id)
            
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
                    "type": getattr(last_msg, 'message_type', None),
                    "order_id": getattr(last_msg, 'order_id', None),
                    "offer_price": getattr(last_msg, 'offer_price', None)
                }
            
            chats.append({
                "id": chat.id,
                "customer_id": chat.user1_id,
                "executor_id": chat.user2_id,
                "customer_name": customer.name if customer else "",
                "customer_nickname": customer.nickname if customer else "",
                "executor_name": executor.name if executor else "",
                "executor_nickname": executor.nickname if executor else "",
                "created_at": chat.created_at.isoformat(),
                "last_message": last_message
            })
        
        # Сортируем чаты по дате последнего сообщения (новые сверху)
        chats.sort(key=lambda chat: (
            chat["last_message"]["created_at"] if chat["last_message"] else chat["created_at"]
        ), reverse=True)
        
        await manager.send_personal_message({
            "type": "chats_list",
            "data": {"chats": chats}
        }, websocket)

async def handle_get_messages(websocket, user_id: int, message_data: dict):
    """Обработка получения сообщений чата"""
    data = message_data.get("data", {})
    chat_id = data.get("chat_id")
    after_id = data.get("after_id", 0)
    
    if not chat_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "chat_id is required"}
        }, websocket)
        return

    async with AsyncSessionLocal() as session:
        message_repo = MessageRepository(session)
        message_service = MessageService(message_repo)
        user_service = UserService(session)
        
        # Проверяем доступ к чату
        chat_result = await session.execute(select(ChatORM).where(ChatORM.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        
        if not chat or (chat.customer_id != user_id and chat.executor_id != user_id):
            await manager.send_personal_message({
                "type": "error",
                "data": {"message": "Access denied to chat"}
            }, websocket)
            return

        messages = await message_service.get_messages(chat_id)
        
        # Фильтруем только новые сообщения
        new_messages = []
        for m in messages:
            if m.id > after_id:  # Убрали фильтр по типу 'offer'
                sender = await user_service.get_user_by_id(m.sender_id)
                new_messages.append({
                    "id": m.id,
                    "text": m.content,
                    "sender_id": m.sender_id,
                    "sender_name": sender.name if sender else "",
                    "sender_nickname": sender.nickname if sender else "",
                    "created_at": m.created_at.isoformat(),
                    "type": getattr(m, 'message_type', None),
                    "order_id": getattr(m, 'order_id', None),
                    "offer_price": getattr(m, 'offer_price', None)
                })
        
        await manager.send_personal_message({
            "type": "messages_list",
            "data": {"messages": new_messages, "chat_id": chat_id}
        }, websocket)

async def handle_ping(websocket, user_id: int, message_data: dict):
    """Обработка ping сообщения"""
    await manager.send_personal_message({
        "type": "pong",
        "data": {"timestamp": datetime.now().isoformat()}
    }, websocket)

async def send_updated_chats_to_users(user_ids: list, session):
    """Отправка обновленного списка чатов пользователям"""
    from src.infrastructure.services.chat_service import ChatService
    from src.infrastructure.services.user_service import UserService
    from src.infrastructure.services.message_service import MessageService
    
    chat_service = ChatService(session)
    user_service = UserService(session)
    message_repo = MessageRepository(session)
    message_service = MessageService(message_repo)
    
    for user_id in user_ids:
        if user_id in manager.active_connections:
            # Получаем чаты пользователя
            chat_orms = await chat_service.get_user_chats(user_id)
            chats = []
            
            for chat in chat_orms:
                # Получаем информацию о собеседнике
                if chat.user1_id == user_id:
                    other_user = await user_service.get_user_by_id(chat.user2_id)
                    other_user_name = other_user.name if other_user else ""
                    other_user_nickname = other_user.nickname if other_user else ""
                else:
                    other_user = await user_service.get_user_by_id(chat.user1_id)
                    other_user_name = other_user.name if other_user else ""
                    other_user_nickname = other_user.nickname if other_user else ""
                
                # Получаем последнее сообщение
                last_message = await message_service.get_last_message(chat.id)
                
                # Получаем информацию о пользователях
                customer = await user_service.get_user_by_id(chat.user1_id)
                executor = await user_service.get_user_by_id(chat.user2_id)
                
                chat_data = {
                    "id": chat.id,
                    "customer_id": chat.user1_id,
                    "executor_id": chat.user2_id,
                    "customer_name": customer.name if customer else "",
                    "customer_nickname": customer.nickname if customer else "",
                    "executor_name": executor.name if executor else "",
                    "executor_nickname": executor.nickname if executor else "",
                    "created_at": chat.created_at.isoformat(),
                    "last_message": {
                        "id": last_message.id,
                        "text": last_message.content,
                        "sender_id": last_message.sender_id,
                        "created_at": last_message.created_at.isoformat()
                    } if last_message else None
                }
                chats.append(chat_data)
            
            # Сортируем чаты по дате последнего сообщения (новые сверху)
            chats.sort(key=lambda chat: (
                chat["last_message"]["created_at"] if chat["last_message"] else chat["created_at"]
            ), reverse=True)
            
            # Отправляем обновленный список чатов
            await manager.send_to_user({
                "type": "chats_updated",
                "data": {"chats": chats}
            }, user_id)
