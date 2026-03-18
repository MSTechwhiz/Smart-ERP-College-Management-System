from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class Mail(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str
    to_user_id: str
    subject: str
    body: str
    attachments: List[str] = []
    is_read: bool = False
    is_archived: bool = False
    is_draft: bool = False
    parent_id: Optional[str] = None  # For thread replies
    priority: str = "normal"  # normal, high
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MailCreate(BaseModel):
    to_user_id: str
    subject: str
    body: str
    attachments: List[str] = []
    priority: str = "normal"
    is_draft: bool = False
    parent_id: Optional[str] = None
