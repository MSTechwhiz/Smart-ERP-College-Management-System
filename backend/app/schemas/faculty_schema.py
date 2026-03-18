from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Faculty(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    employee_id: str
    department_id: str
    designation: str
    specialization: Optional[str] = None
    is_class_incharge: bool = False
    incharge_class: Optional[str] = None
    joining_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FacultyCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    employee_id: str
    department_id: str
    designation: str
    specialization: Optional[str] = None

