from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# Loan schemas
class LoanCreate(BaseModel):
    title: str
    borrower_name: Optional[str] = None
    loan_amount: Optional[Decimal] = None
    currency: str = "EUR"
    origination_date: Optional[date] = None
    maturity_date: Optional[date] = None

class LoanResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    title: str
    borrower_name: Optional[str]
    loan_amount: Optional[float]
    currency: str
    origination_date: Optional[date]
    maturity_date: Optional[date]
    status: str
    ai_extraction_status: str
    created_at: datetime
    covenant_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Covenant schemas
class CovenantResponse(BaseModel):
    id: UUID4
    loan_agreement_id: UUID4
    covenant_type: str
    covenant_name: str
    description: Optional[str]
    threshold_value: Optional[float]
    threshold_operator: Optional[str]
    frequency: Optional[str]
    next_test_date: Optional[date]
    is_active: bool
    latest_status: Optional[str] = None
    latest_value: Optional[float] = None
    
    class Config:
        from_attributes = True

class MeasurementCreate(BaseModel):
    measurement_date: date
    actual_value: Decimal
    notes: Optional[str] = None

class MeasurementResponse(BaseModel):
    id: UUID4
    covenant_id: UUID4
    measurement_date: date
    actual_value: float
    threshold_value: Optional[float]
    status: str
    distance_to_breach: Optional[float]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Alert schemas
class AlertResponse(BaseModel):
    id: UUID4
    covenant_id: Optional[UUID4]
    loan_agreement_id: Optional[UUID4]
    alert_type: str
    severity: str
    title: str
    message: str
    predicted_breach_date: Optional[date]
    days_until_breach: Optional[int]
    is_read: bool
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard/Analytics schemas
class PortfolioSummary(BaseModel):
    total_loans: int
    active_loans: int
    total_covenants: int
    compliant_covenants: int
    warning_covenants: int
    breach_covenants: int
    unread_alerts: int
    critical_alerts: int

class RiskHeatmapItem(BaseModel):
    loan_id: UUID4
    loan_title: str
    borrower_name: Optional[str]
    status: str  # compliant, warning, breach
    covenant_count: int
    critical_count: int

class PortfolioValueResponse(BaseModel):
    current_value: float
    previous_value: float
    change_percentage: float
    change_amount: float

class TrendDataPoint(BaseModel):
    month: str
    value: float

class PortfolioTrendsResponse(BaseModel):
    months: List[str]
    current_period: List[float]
    previous_period: List[float]

class CovenantTrendsResponse(BaseModel):
    compliant_change: float
    warning_change: float
    breach_change: float
