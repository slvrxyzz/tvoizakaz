from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Message(BaseModel):
    id: Optional[int] = None
    chat_id: int
    sender_id: int
    content: str
    message_type: str = "text"
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None