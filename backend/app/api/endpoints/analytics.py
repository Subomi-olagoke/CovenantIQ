from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.user import User
from app.models.loan import LoanAgreement
from app.models.covenant import Covenant, CovenantMeasurement
from app.models.alert import Alert
from app.schemas.loan import PortfolioSummary, RiskHeatmapItem, AlertResponse, LoanResponse
from app.api.deps import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/portfolio-summary", response_model=PortfolioSummary)
def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio overview statistics for dashboard"""
    # Total loans
    total_loans = db.query(func.count(LoanAgreement.id)).filter(
        LoanAgreement.user_id == current_user.id
    ).scalar() or 0
    
    # Active loans
    active_loans = db.query(func.count(LoanAgreement.id)).filter(
        LoanAgreement.user_id == current_user.id,
        LoanAgreement.status == 'active'
    ).scalar() or 0
    
    # Total covenants
    total_covenants = db.query(func.count(Covenant.id)).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id,
        Covenant.is_active == True
    ).scalar() or 0
    
    # Get covenant status counts via latest measurements
    covenant_statuses = db.query(
        CovenantMeasurement.status,
        func.count(func.distinct(CovenantMeasurement.covenant_id)).label('count')
    ).join(
        Covenant
    ).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id,
        Covenant.is_active == True
    ).group_by(
        CovenantMeasurement.status
    ).all()
    
    status_dict = {status: count for status, count in covenant_statuses}
    
    compliant_covenants = status_dict.get('compliant', 0)
    warning_covenants = status_dict.get('warning', 0)
    breach_covenants = status_dict.get('breach', 0)
    
    # Unread alerts
    unread_alerts = db.query(func.count(Alert.id)).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id,
        Alert.is_read == False,
        Alert.is_resolved == False
    ).scalar() or 0
    
    # Critical alerts
    critical_alerts = db.query(func.count(Alert.id)).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id,
        Alert.severity == 'critical',
        Alert.is_resolved == False
    ).scalar() or 0
    
    return PortfolioSummary(
        total_loans=total_loans,
        active_loans=active_loans,
        total_covenants=total_covenants,
        compliant_covenants=compliant_covenants,
        warning_covenants=warning_covenants,
        breach_covenants=breach_covenants,
        unread_alerts=unread_alerts,
        critical_alerts=critical_alerts
    )

@router.get("/risk-heatmap", response_model=List[RiskHeatmapItem])
def get_risk_heatmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk heatmap data for dashboard visualization"""
    # Get loans with their worst covenant status
    loans = db.query(LoanAgreement).filter(
        LoanAgreement.user_id == current_user.id,
        LoanAgreement.status == 'active'
    ).all()
    
    heatmap_items = []
    
    for loan in loans:
        # Get covenant count
        covenant_count = db.query(func.count(Covenant.id)).filter(
            Covenant.loan_agreement_id == loan.id,
            Covenant.is_active == True
        ).scalar() or 0
        
        # Get worst status from latest measurements
        worst_status = 'compliant'  # default
        critical_count = 0
        
        if covenant_count > 0:
            # Get all latest measurements for this loan's covenants
            measurements = db.query(CovenantMeasurement).join(
                Covenant
            ).filter(
                Covenant.loan_agreement_id == loan.id,
                Covenant.is_active == True
            ).order_by(
                CovenantMeasurement.covenant_id,
                CovenantMeasurement.measurement_date.desc()
            ).all()
            
            # Group by covenant and get latest
            covenant_latest = {}
            for m in measurements:
                if m.covenant_id not in covenant_latest:
                    covenant_latest[m.covenant_id] = m.status
            
            # Determine worst status
            statuses = list(covenant_latest.values())
            if 'breach' in statuses:
                worst_status = 'breach'
                critical_count = statuses.count('breach')
            elif 'warning' in statuses:
                worst_status = 'warning'
                critical_count = statuses.count('warning')
        
        heatmap_items.append(
            RiskHeatmapItem(
                loan_id=loan.id,
                loan_title=loan.title,
                borrower_name=loan.borrower_name,
                status=worst_status,
                covenant_count=covenant_count,
                critical_count=critical_count
            )
        )
    
    return heatmap_items

@router.get("/recent-loans", response_model=List[LoanResponse])
def get_recent_loans(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recently created loans"""
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
    """Get top critical alerts for dashboard"""
    alerts = db.query(Alert).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id,
        Alert.severity.in_(['critical', 'high']),
        Alert.is_resolved == False
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    return [AlertResponse.from_orm(alert) for alert in alerts]
