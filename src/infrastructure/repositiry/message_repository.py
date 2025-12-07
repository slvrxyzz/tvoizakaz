from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.infrastructure.repositiry.db_models import MessageORM
from src.domain.entity.messageentity import Message
from typing import List, Optional
from datetime import datetime

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_message(self, message: Message) -> Message:
        message_orm = MessageORM(
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            content=message.content,
            message_type=message.message_type,
            file_path=message.file_path
        )
        self.session.add(message_orm)
        await self.session.commit()
        await self.session.refresh(message_orm)
        
        return Message(
            id=message_orm.id,
            chat_id=message_orm.chat_id,
            sender_id=message_orm.sender_id,
            content=message_orm.content,
            message_type=message_orm.message_type,
            file_path=message_orm.file_path,
            created_at=message_orm.created_at,
            edited_at=message_orm.edited_at
        )
    
    async def get_by_id(self, message_id: int) -> Optional[Message]:
        query = select(MessageORM).where(MessageORM.id == message_id)
        result = await self.session.execute(query)
        message_orm = result.scalar_one_or_none()
        
        if not message_orm:
            return None
            
        return Message(
            id=message_orm.id,
            chat_id=message_orm.chat_id,
            sender_id=message_orm.sender_id,
            content=message_orm.content,
            message_type=message_orm.message_type,
            file_path=message_orm.file_path,
            created_at=message_orm.created_at,
            edited_at=message_orm.edited_at
        )
    
    async def get_messages_by_chat_id(self, chat_id: int) -> List[Message]:
        query = select(MessageORM).where(
            MessageORM.chat_id == chat_id,
            MessageORM.is_deleted == False
        ).order_by(MessageORM.created_at)
        
        result = await self.session.execute(query)
        messages_orm = result.scalars().all()
        
        return [
            Message(
                id=msg.id,
                chat_id=msg.chat_id,
                sender_id=msg.sender_id,
                content=msg.content,
                message_type=msg.message_type,
                file_path=msg.file_path,
                created_at=msg.created_at,
                edited_at=msg.edited_at
            )
            for msg in messages_orm
        ]
    
    async def update_message(self, message: Message) -> Message:
        query = update(MessageORM).where(MessageORM.id == message.id).values(
            content=message.content,
            edited_at=datetime.utcnow()
        )
        await self.session.execute(query)
        await self.session.commit()
        
        return message
    
    async def delete_message(self, message_id: int) -> bool:
        query = update(MessageORM).where(MessageORM.id == message_id).values(
            is_deleted=True
        )
        result = await self.session.execute(query)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def get_messages_by_sender(self, sender_id: int) -> List[Message]:
        query = select(MessageORM).where(
            MessageORM.sender_id == sender_id,
            MessageORM.is_deleted == False
        ).order_by(MessageORM.created_at.desc())
        
        result = await self.session.execute(query)
        messages_orm = result.scalars().all()
        
        return [
            Message(
                id=msg.id,
                chat_id=msg.chat_id,
                sender_id=msg.sender_id,
                content=msg.content,
                message_type=msg.message_type,
                file_path=msg.file_path,
                created_at=msg.created_at,
                edited_at=msg.edited_at
            )
            for msg in messages_orm
        ]