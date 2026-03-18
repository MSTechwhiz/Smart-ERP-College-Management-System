from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class Announcement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    created_by: str
    target_roles: List[str] = []  # Empty means all
    target_departments: List[str] = []
    target_batches: List[str] = []
    target_semesters: List[int] = []
    publish_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    is_deleted: bool = False

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    target_roles: List[str] = []
    target_departments: List[str] = []
    target_batches: List[str] = []
    target_semesters: List[int] = []
    publish_date: Optional[datetime] = None

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    target_roles: Optional[List[str]] = None
    target_departments: Optional[List[str]] = None
    target_batches: Optional[List[str]] = None
    target_semesters: Optional[List[int]] = None
    publish_date: Optional[datetime] = None
    is_active: Optional[bool] = None
