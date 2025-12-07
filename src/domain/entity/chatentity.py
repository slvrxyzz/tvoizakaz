from pydantic import BaseModel, Field, root_validator
from typing import Optional
from datetime import datetime

from src.domain.entity.messageentity import Message as MessageEntity

class Chat(BaseModel):
    id: Optional[int] = None
    user1_id: int
    user2_id: int
    order_id: Optional[int] = None
    created_at: Optional[datetime] = None
    messages: list[MessageEntity] = Field(default_factory=list)


class Message(MessageEntity):
    """Backward-compatible re-export in chatentity module."""
    is_deleted: bool = False
    is_edited: bool = False
    @root_validator(pre=True)
    def _legacy_text_field(cls, values: dict) -> dict:
        text = values.pop("text", None)
        if text is not None:
            values.setdefault("content", text)
        return values

    @property
    def text(self) -> str:
        return self.content

    @text.setter
    def text(self, value: str) -> None:
        self.content = value