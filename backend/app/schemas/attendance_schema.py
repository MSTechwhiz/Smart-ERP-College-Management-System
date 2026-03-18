from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class Attendance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    subject_id: str
    date: str  # YYYY-MM-DD
    status: str  # present, absent, od
    marked_by: str
    marked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AttendanceCreate(BaseModel):
    student_id: str
    subject_id: str
    date: str
    status: str

class BulkAttendanceCreate(BaseModel):
    subject_id: str
    date: str
    records: List[dict]  # [{"student_id": "...", "status": "present/absent"}]
