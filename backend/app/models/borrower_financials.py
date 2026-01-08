from sqlalchemy import Column, DateTime, Numeric, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class BorrowerFinancial(Base):
    """
    Borrower financial data for ML predictions.
    Stores time-series financial metrics used to train prediction models.
    """
    __tablename__ = "borrower_financials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_agreement_id = Column(UUID(as_uuid=True), ForeignKey("loan_agreements.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period = Column(Date, nullable=False)
    
    # Standard financial metrics
    revenue = Column(Numeric(20, 2))
    ebitda = Column(Numeric(20, 2))
    total_debt = Column(Numeric(20, 2))
    total_assets = Column(Numeric(20, 2))
    interest_expense = Column(Numeric(20, 2))
    free_cash_flow = Column(Numeric(20, 2))
    
    # Flexible JSON for additional metrics
    custom_metrics = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    loan_agreement = relationship("LoanAgreement", back_populates="borrower_financials")
