from sqlalchemy import Column, String, DateTime, Numeric, Date, Text, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Covenant(Base):
    __tablename__ = "covenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_agreement_id = Column(UUID(as_uuid=True), ForeignKey("loan_agreements.id", ondelete="CASCADE"), nullable=False, index=True)
    covenant_type = Column(String(100), nullable=False)  # financial, non-financial, reporting
    covenant_name = Column(String(255), nullable=False)
    description = Column(Text)
    threshold_value = Column(Numeric(15, 4))
    threshold_operator = Column(String(10))  # >, <, >=, <=, =
    measurement_frequency = Column(String(50))  # quarterly, annually, monthly
    next_measurement_date = Column(Date)
    status = Column(String(50), default="healthy")  # healthy, warning, critical, breached
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    loan_agreement = relationship("LoanAgreement", back_populates="covenants")
    measurements = relationship("CovenantMeasurement", back_populates="covenant", cascade="all, delete-orphan")
    predictions = relationship("CovenantPrediction", back_populates="covenant", cascade="all, delete-orphan")


class CovenantMeasurement(Base):
    __tablename__ = "covenant_measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    covenant_id = Column(UUID(as_uuid=True), ForeignKey("covenants.id", ondelete="CASCADE"), nullable=False, index=True)
    measurement_date = Column(Date, nullable=False)
    actual_value = Column(Numeric(15, 4), nullable=False)
    is_compliant = Column(Boolean, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    covenant = relationship("Covenant", back_populates="measurements")


class CovenantPrediction(Base):
    __tablename__ = "covenant_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    covenant_id = Column(UUID(as_uuid=True), ForeignKey("covenants.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False)
    predicted_value = Column(Numeric(15, 4))
    breach_probability = Column(Numeric(5, 2))  # 0-100
    days_to_potential_breach = Column(Numeric(10, 0))
    confidence_score = Column(Numeric(5, 2))  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    covenant = relationship("Covenant", back_populates="predictions")
