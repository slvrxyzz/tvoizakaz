from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.repositiry.db_models import ChatORM
from src.domain.entity.chatentity import Chat
from typing import List, Optional

class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_chat_between_users(self, user1_id: int, user2_id: int) -> Optional[ChatORM]:
        query = select(ChatORM).where(
            ((ChatORM.customer_id == user1_id) & (ChatORM.executor_id == user2_id)) |
            ((ChatORM.customer_id == user2_id) & (ChatORM.executor_id == user1_id))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, chat_id: int) -> Optional[ChatORM]:
        query = select(ChatORM).where(ChatORM.id == chat_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, user1_id: int, user2_id: int, order_id: Optional[int]) -> ChatORM:
        chat = ChatORM(
            customer_id=user1_id,
            executor_id=user2_id,
            order_id=order_id
        )
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat
    
    async def get_user_chats(self, user_id: int) -> List[ChatORM]:
        query = select(ChatORM).where(
            (ChatORM.customer_id == user_id) | (ChatORM.executor_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()