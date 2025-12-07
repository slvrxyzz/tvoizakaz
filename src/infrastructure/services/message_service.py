from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entity.messageentity import Message
from src.infrastructure.repositiry.message_repository import MessageRepository
from src.infrastructure.security.content_filter import (
    ContentRejectedError,
    ContentFilter,
    default_content_filter,
)

class MessageService:
    def __init__(
        self,
        repo_or_session: Union[MessageRepository, AsyncSession],
        *,
        content_filter: ContentFilter | None = None,
    ):
        if isinstance(repo_or_session, MessageRepository):
            self.message_repo = repo_or_session
        else:
            self.message_repo = MessageRepository(repo_or_session)
        self.content_filter = content_filter or default_content_filter

    async def send_message(
        self,
        chat_id: int,
        sender_id: int,
        content: str,
        message_type: str = "text",
        file_url: Optional[str] = None,
    ) -> Message:
        try:
            self.content_filter.enforce(
                content,
                context={"chat_id": chat_id, "sender_id": sender_id},
            )
        except ContentRejectedError as exc:
            raise exc

        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            file_path=file_url
        )
        return await self.message_repo.add_message(message)

    async def get_messages(self, chat_id: int) -> List[Message]:
        return await self.message_repo.get_messages_by_chat_id(chat_id)

    async def edit_message(self, message_id: int, new_content: str) -> Optional[Message]:
        message = await self.message_repo.get_by_id(message_id)
        if message:
            try:
                self.content_filter.enforce(
                    new_content,
                    context={"message_id": message_id, "sender_id": message.sender_id},
                )
            except ContentRejectedError as exc:
                raise exc
            message.content = new_content
            message.edited_at = datetime.now()
            return await self.message_repo.update_message(message)
        return None

    async def delete_message(self, message_id: int) -> bool:
        return await self.message_repo.delete_message(message_id)

    async def get_message_by_id(self, message_id: int) -> Optional[Message]:
        return await self.message_repo.get_by_id(message_id)

    async def get_last_message(self, chat_id: int) -> Optional[Message]:
        messages = await self.message_repo.get_messages_by_chat_id(chat_id)
        return messages[-1] if messages else None