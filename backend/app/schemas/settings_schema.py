from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class UserSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    theme: str = "light"  # light, dark, system
    color_scheme: str = "blue"  # blue, green, purple, orange
    notification_email: bool = True
    notification_push: bool = True
    notification_sms: bool = False
    language: str = "en"
    timezone: str = "Asia/Kolkata"
    dashboard_layout: str = "default"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    color_scheme: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_sms: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    dashboard_layout: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
