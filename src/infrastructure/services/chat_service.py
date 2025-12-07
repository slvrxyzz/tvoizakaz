from src.infrastructure.repositiry.chat_repository import ChatRepository
from src.domain.entity.chatentity import Chat
from typing import List, Optional
from datetime import datetime

class ChatService:
    def __init__(self, session):
        self.chat_repo = ChatRepository(session)
        self.session = session

    async def get_or_create_chat_between_users(self, user1_id: int, user2_id: int, order_id: Optional[int] = None) -> Chat:
        # Сначала проверяем, есть ли уже чат между этими пользователями
        existing_chat = await self.chat_repo.get_chat_between_users(user1_id, user2_id)
        
        if existing_chat:
            return Chat(
                id=existing_chat.id,
                user1_id=existing_chat.customer_id,
                user2_id=existing_chat.executor_id,
                order_id=existing_chat.order_id,
                created_at=existing_chat.created_at
            )
        
        # Если чата нет, создаем новый
        chat_orm = await self.chat_repo.create(user1_id, user2_id, order_id)
        
        return Chat(
            id=chat_orm.id,
            user1_id=chat_orm.customer_id,
            user2_id=chat_orm.executor_id,
            order_id=chat_orm.order_id,
            created_at=chat_orm.created_at
        )

    async def get_chat_by_id(self, chat_id: int) -> Optional[Chat]:
        chat_orm = await self.chat_repo.get_by_id(chat_id)
        
        if not chat_orm:
            return None
            
        return Chat(
            id=chat_orm.id,
            user1_id=chat_orm.customer_id,
            user2_id=chat_orm.executor_id,
            order_id=chat_orm.order_id,
            created_at=chat_orm.created_at
        )

    async def get_user_chats(self, user_id: int) -> List[Chat]:
        chats_orm = await self.chat_repo.get_user_chats(user_id)
        
        return [
            Chat(
                id=chat.id,
                user1_id=chat.customer_id,
                user2_id=chat.executor_id,
                order_id=chat.order_id,
                created_at=chat.created_at
            )
            for chat in chats_orm
        ]

    async def create_chat(self, user1_id: int, user2_id: int, order_id: Optional[int] = None) -> Chat:
        chat_orm = await self.chat_repo.create(user1_id, user2_id, order_id)
        
        return Chat(
            id=chat_orm.id,
            user1_id=chat_orm.customer_id,
            user2_id=chat_orm.executor_id,
            order_id=chat_orm.order_id,
            created_at=chat_orm.created_at
        )