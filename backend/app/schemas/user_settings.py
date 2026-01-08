from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Profile Update
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None

# User Preferences
class UserPreferencesBase(BaseModel):
    email_alerts: bool = True
    weekly_reports: bool = False
    system_updates: bool = True

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferences(UserPreferencesBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# User Activity
class UserActivityItem(BaseModel):
    id: str
    action: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
