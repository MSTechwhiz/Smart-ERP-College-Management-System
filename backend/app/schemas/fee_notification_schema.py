from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class FeeNotificationLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    student_name: str
    mobile_number: Optional[str] = None
    email_address: Optional[str] = None
    fee_name: str
    amount: float
    status: str  # Combined status for legacy support
    sms_status: str = "Pending"
    whatsapp_status: str = "Pending"
    email_status: str = "Pending"
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
