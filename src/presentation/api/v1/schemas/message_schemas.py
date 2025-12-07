from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class MessageCreate(BaseModel):
    text: Optional[str] = Field(None, max_length=2000)
    message_type: MessageType = Field(default=MessageType.TEXT)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0, le=50*1024*1024)  # 50MB max

class MessageUpdate(BaseModel):
    text: Optional[str] = Field(None, max_length=2000)

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: Optional[str]
    message_type: MessageType
    file_name: Optional[str]
    file_size: Optional[int]
    is_edited: bool
    is_deleted: bool
    edited_at: Optional[datetime]
    created_at: datetime
    sender_name: str
    sender_nickname: str

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_size: int
    file_url: str
