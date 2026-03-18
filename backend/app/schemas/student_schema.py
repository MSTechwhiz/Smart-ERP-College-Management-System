from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Student(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    roll_number: str
    department_id: str
    batch: str
    year: int = 1
    semester: int = 1
    section: Optional[str] = None
    mentor_id: Optional[str] = None
    cgpa: float = 0.0
    regulation: str = "R2023"
    admission_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Extended fields from Google Sheet
    umis_id: Optional[str] = None
    aadhar_number: Optional[str] = None
    community: Optional[str] = None
    blood_group: Optional[str] = None
    admission_quota: Optional[str] = None
    admission_type: Optional[str] = None
    emis_id: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    mobile_number: Optional[str] = None
    permanent_address: Optional[str] = None
    is_active: bool = True


class StudentCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    roll_number: Optional[str] = None
    department_id: str
    batch: str
    year: int = 1
    semester: int = 1
    section: Optional[str] = None
    mentor_id: Optional[str] = None
    regulation: str = "R2023"
    
    # Extended fields
    umis_id: Optional[str] = None
    aadhar_number: Optional[str] = None
    community: Optional[str] = None
    blood_group: Optional[str] = None
    admission_quota: Optional[str] = None
    admission_type: Optional[str] = None
    emis_id: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    mobile_number: Optional[str] = None
    permanent_address: Optional[str] = None

