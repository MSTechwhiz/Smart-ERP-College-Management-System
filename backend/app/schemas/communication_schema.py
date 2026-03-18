from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class CommunicationBase(BaseModel):
    title: str
    message: str
    target_role: str
    priority: Optional[str] = "normal"
    attachment_url: Optional[str] = None

class CommunicationCreate(CommunicationBase):
    pass

class Communication(CommunicationBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    sender_role: str
    sender_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_status: List[str] = [] # List of user IDs who have read the message
    is_deleted: bool = False

class CommunicationResponse(BaseModel):
    id: str
    title: str
    message: str
    sender_id: str
    sender_role: str
    sender_name: str
    target_role: str
    priority: Optional[str]
    attachment_url: Optional[str]
    created_at: datetime
    read_status: List[str]
    is_deleted: bool
