from sqlalchemy import Column, String, DateTime, Numeric, Date, Text, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Covenant(Base):
    __tablename__ = "covenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_agreement_id = Column(UUID(as_uuid=True), ForeignKey("loan_agreements.id", ondelete="CASCADE"), nullable=False, index=True)
    covenant_type = Column(String(100), nullable=False)  # financial, information, negative, affirmative
    covenant_name = Column(String(255), nullable=False)
    description = Column(Text)
    threshold_value = Column(Numeric(20, 4))
    threshold_operator = Column(String(20))  # less_than, greater_than, less_or_equal, greater_or_equal, equal
    frequency = Column(String(50))  # quarterly, semi-annual, annual
    next_test_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    loan_agreement = relationship("LoanAgreement", back_populates="covenants")
    measurements = relationship("CovenantMeasurement", back_populates="covenant", cascade="all, delete-orphan")


class CovenantMeasurement(Base):
    __tablename__ = "covenant_measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    covenant_id = Column(UUID(as_uuid=True), ForeignKey("covenants.id", ondelete="CASCADE"), nullable=False, index=True)
    measurement_date = Column(Date, nullable=False, index=True)
    actual_value = Column(Numeric(20, 4), nullable=False)
    threshold_value = Column(Numeric(20, 4))  # Store threshold at measurement time
    status = Column(String(50), nullable=False)  # compliant, warning, breach
    distance_to_breach = Column(Numeric(10, 4))  # Positive = safe, Negative = breach
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    covenant = relationship("Covenant", back_populates="measurements")
