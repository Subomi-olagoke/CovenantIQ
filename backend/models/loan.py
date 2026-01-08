from sqlalchemy import Column, String, DateTime, Numeric, Date, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class LoanAgreement(Base):
    __tablename__ = "loan_agreements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    borrower_name = Column(String(255), nullable=False)
    loan_amount = Column(Numeric(15, 2))
    currency = Column(String(3), default="USD")
    origination_date = Column(Date)
    maturity_date = Column(Date)
    file_url = Column(Text)
    file_name = Column(String(255))
    extraction_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    covenants = relationship("Covenant", back_populates="loan_agreement", cascade="all, delete-orphan")
