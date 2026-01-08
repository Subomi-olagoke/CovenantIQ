from sqlalchemy import Column, String, DateTime, Numeric, Date, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class LoanAgreement(Base):
    __tablename__ = "loan_agreements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    borrower_name = Column(String(255))
    loan_amount = Column(Numeric(20, 2))
    currency = Column(String(3), default="EUR")  # European markets default
    origination_date = Column(Date)
    maturity_date = Column(Date)
    status = Column(String(50), default="active")  # active, matured, defaulted
    document_path = Column(String(500))  # Path to uploaded PDF
    ai_extraction_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    ai_extraction_result = Column(JSONB)  # Full Claude API response
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    covenants = relationship("Covenant", back_populates="loan_agreement", cascade="all, delete-orphan")
    borrower_financials = relationship("BorrowerFinancial", back_populates="loan_agreement", cascade="all, delete-orphan")
