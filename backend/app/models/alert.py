from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Date, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    covenant_id = Column(UUID(as_uuid=True), ForeignKey("covenants.id", ondelete="CASCADE"))
    loan_agreement_id = Column(UUID(as_uuid=True), ForeignKey("loan_agreements.id", ondelete="CASCADE"), index=True)
    alert_type = Column(String(50), nullable=False)  # prediction, breach, due_date, compliance
    severity = Column(String(50), nullable=False, index=True)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    predicted_breach_date = Column(Date)  # For predictive alerts
    days_until_breach = Column(Integer)  #Days until predicted/actual breach
    is_read = Column(Boolean, default=False, index=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
