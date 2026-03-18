from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class DocumentWorkflow(BaseModel):
    level: str  # office, faculty, hod, principal
    user_id: str
    user_name: str
    action: str  # submitted, verified, approved, rejected, signed, generated
    remarks: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_number: str = Field(default_factory=lambda: f"DOC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}")
    student_id: str
    document_type: str  # bonafide, tc, marksheet, fee_letter, character_certificate, custom
    custom_document_name: Optional[str] = None
    purpose: Optional[str] = None
    status: str = "Pending"  # Pending, Verified, Approved, Signed, Issued
    current_level: str = "office"  # office, principal
    workflow_history: List[dict] = []
    generated_document_url: Optional[str] = None
    collected_at: Optional[datetime] = None
    remarks: Optional[str] = None
    priority: str = "normal"  # normal, urgent
    expected_date: Optional[str] = None
    delivery_type: str = "hard"  # hard, soft
    file_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentRequestCreate(BaseModel):
    document_type: str
    custom_document_name: Optional[str] = None
    purpose: Optional[str] = None
    remarks: Optional[str] = None
    priority: str = "normal"
    delivery_type: str = "hard"
