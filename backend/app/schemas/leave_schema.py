from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class LeaveRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    from_date: str
    to_date: str
    reason: str
    leave_type: str = "Personal Leave"  # Medical, Personal, Emergency, Other
    attachment_url: Optional[str] = None
    status: str = "Pending"  # Pending, Approved, Rejected
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeaveRequestCreate(BaseModel):
    from_date: str
    to_date: str
    reason: str
    leave_type: str
    attachment_url: Optional[str] = None
