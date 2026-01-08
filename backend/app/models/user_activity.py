from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class UserActivity(Base):
    __tablename__ = "user_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    action = Column(String(100), nullable=False)  # e.g., 'login', 'loan_upload', 'settings_update'
    description = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
