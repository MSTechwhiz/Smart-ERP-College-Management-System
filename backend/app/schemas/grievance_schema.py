from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class GrievanceWorkflow(BaseModel):
    level: str  # faculty, hod, admin, principal
    user_id: str
    user_name: str
    action: str  # forwarded, resolved, escalated, rejected
    remarks: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Grievance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str = Field(default_factory=lambda: f"GRV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}")
    student_id: str
    department_id: Optional[str] = None
    subject: str
    description: str
    category: str  # academic, fee, hostel, infrastructure, other
    target_type: str = "faculty"  # faculty, admin
    priority: str = "medium"  # low, medium, high, urgent
    status: str = "open"  # open, faculty_review, hod_review, admin_review, principal_review, resolved, closed, rejected
    current_level: str = "faculty"  # faculty, hod, admin, principal
    assigned_to: Optional[str] = None
    faculty_remarks_for_hod: Optional[str] = None
    attachments: List[str] = []
    workflow_history: List[dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None

class GrievanceCreate(BaseModel):
    subject: str
    description: str
    category: str
    target_type: str = "faculty"
    priority: str = "medium"
    attachments: List[str] = []

class GrievanceUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
