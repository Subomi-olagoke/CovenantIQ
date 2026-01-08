from pydantic import BaseModel, EmailStr, UUID4, condecimal
from typing import Optional, List
from datetime import date, datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID4
    email: str
    full_name: Optional[str]
    company: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Loan schemas
class LoanCreate(BaseModel):
    title: str
    borrower_name: str
    loan_amount: Optional[condecimal(max_digits=15, decimal_places=2)]
    currency: str = "USD"
    origination_date: Optional[date]
    maturity_date: Optional[date]

class LoanResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    title: str
    borrower_name: str
    loan_amount: Optional[float]
    currency: str
    origination_date: Optional[date]
    maturity_date: Optional[date]
    file_name: Optional[str]
    extraction_status: str
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
    measurement_frequency: Optional[str]
    next_measurement_date: Optional[date]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MeasurementCreate(BaseModel):
    measurement_date: date
    actual_value: condecimal(max_digits=15, decimal_places=4)
    notes: Optional[str] = None

class MeasurementResponse(BaseModel):
    id: UUID4
    covenant_id: UUID4
    measurement_date: date
    actual_value: float
    is_compliant: bool
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    prediction_date: date
    predicted_value: Optional[float]
    breach_probability: Optional[float]
    confidence_score: Optional[float]
    
    class Config:
        from_attributes = True

# Alert schemas
class AlertResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    covenant_id: Optional[UUID4]
    alert_type: Optional[str]
    severity: Optional[str]
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_loans: int
    healthy_covenants: int
    warning_covenants: int
    critical_covenants: int
    unread_alerts: int
