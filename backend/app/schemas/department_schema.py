from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Department(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    code: str
    hod_id: Optional[str] = None
    vision: Optional[str] = None
    mission: Optional[str] = None
    established_year: Optional[int] = None
    total_intake: int = 60
    sections: List[str] = ["A", "B"]
    programs_offered: List[str] = []
    accreditation: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DepartmentCreate(BaseModel):
    name: str
    code: str
    hod_id: Optional[str] = None
    vision: Optional[str] = None
    mission: Optional[str] = None
    established_year: Optional[int] = None
    total_intake: int = 60
    sections: List[str] = ["A", "B"]

