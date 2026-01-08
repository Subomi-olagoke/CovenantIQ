from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.loan import LoanAgreement
from models.covenant import Covenant
from models.alert import Alert
from schemas import DashboardStats, LoanResponse, AlertResponse
from routes.auth import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio overview statistics"""
    # Total loans
    total_loans = db.query(func.count(LoanAgreement.id)).filter(
        LoanAgreement.user_id == current_user.id
    ).scalar()
    
    # Covenant status counts
    healthy_count = db.query(func.count(Covenant.id)).join(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id,
        Covenant.status == 'healthy'
    ).scalar()
    
    warning_count = db.query(func.count(Covenant.id)).join(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id,
        Covenant.status == 'warning'
    ).scalar()
    
    critical_count = db.query(func.count(Covenant.id)).join(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id,
        Covenant.status.in_(['critical', 'breached'])
    ).scalar()
    
    # Unread alerts
    unread_alerts = db.query(func.count(Alert.id)).filter(
        Alert.user_id == current_user.id,
        Alert.is_read == False
    ).scalar()
    
    return DashboardStats(
        total_loans=total_loans or 0,
        healthy_covenants=healthy_count or 0,
        warning_covenants=warning_count or 0,
        critical_covenants=critical_count or 0,
        unread_alerts=unread_alerts or 0
    )

@router.get("/recent-loans", response_model=List[LoanResponse])
def get_recent_loans(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent loans"""
    loans = db.query(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id
    ).order_by(LoanAgreement.created_at.desc()).limit(limit).all()
    
    return [LoanResponse.from_orm(loan) for loan in loans]

@router.get("/critical-alerts", response_model=List[AlertResponse])
def get_critical_alerts(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top critical alerts"""
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.severity.in_(['critical', 'warning'])
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    return [AlertResponse.from_orm(alert) for alert in alerts]
