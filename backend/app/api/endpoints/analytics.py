from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.database import get_db
from app.models.user import User
from app.models.loan import LoanAgreement
from app.models.covenant import Covenant, CovenantMeasurement
from app.models.alert import Alert
from app.schemas.loan import (
    PortfolioSummary, RiskHeatmapItem, AlertResponse, LoanResponse,
    PortfolioValueResponse, PortfolioTrendsResponse, CovenantTrendsResponse
)
from app.api.deps import get_current_user
from typing import List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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

@router.get("/portfolio-value", response_model=PortfolioValueResponse)
def get_portfolio_value(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total portfolio value with period comparison"""
    # Get current total loan amount
    current_value = db.query(
        func.coalesce(func.sum(LoanAgreement.loan_amount), 0)
    ).filter(
        LoanAgreement.user_id == current_user.id,
        LoanAgreement.status == 'active'
    ).scalar() or 0.0

    # Calculate date 30 days ago for comparison
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # Get loans created before 30 days ago (previous period snapshot)
    previous_value = db.query(
        func.coalesce(func.sum(LoanAgreement.loan_amount), 0)
    ).filter(
        LoanAgreement.user_id == current_user.id,
        LoanAgreement.status == 'active',
        LoanAgreement.created_at < thirty_days_ago
    ).scalar() or 0.0

    # Calculate change
    change_amount = float(current_value) - float(previous_value)
    change_percentage = (change_amount / float(previous_value) * 100) if previous_value > 0 else 0.0

    return PortfolioValueResponse(
        current_value=float(current_value),
        previous_value=float(previous_value),
        change_percentage=change_percentage,
        change_amount=change_amount
    )

@router.get("/portfolio-trends", response_model=PortfolioTrendsResponse)
def get_portfolio_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio value trends over the last 13 months"""
    # Calculate 13 months of data
    now = datetime.now()
    months = []
    current_period = []
    previous_period = []

    for i in range(12, -1, -1):
        month_date = now - relativedelta(months=i)
        month_label = month_date.strftime('%b')
        months.append(month_label)

        # Get total loan value up to this month (current year)
        current_month_value = db.query(
            func.coalesce(func.sum(LoanAgreement.loan_amount), 0)
        ).filter(
            LoanAgreement.user_id == current_user.id,
            LoanAgreement.status == 'active',
            LoanAgreement.created_at <= month_date
        ).scalar() or 0.0

        current_period.append(float(current_month_value) / 1000)  # Convert to thousands

        # Get previous year's value for comparison
        prev_year_month = month_date - relativedelta(years=1)
        previous_month_value = db.query(
            func.coalesce(func.sum(LoanAgreement.loan_amount), 0)
        ).filter(
            LoanAgreement.user_id == current_user.id,
            LoanAgreement.status == 'active',
            LoanAgreement.created_at <= prev_year_month
        ).scalar() or 0.0

        previous_period.append(float(previous_month_value) / 1000)  # Convert to thousands

    return PortfolioTrendsResponse(
        months=months,
        current_period=current_period,
        previous_period=previous_period
    )

@router.get("/covenant-trends", response_model=CovenantTrendsResponse)
def get_covenant_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get covenant status trends compared to previous period"""
    # Get current covenant statuses
    current_statuses = db.query(
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

    current_dict = {status: count for status, count in current_statuses}
    current_compliant = current_dict.get('compliant', 0)
    current_warning = current_dict.get('warning', 0)
    current_breach = current_dict.get('breach', 0)

    # Get previous period statuses (30 days ago)
    thirty_days_ago = datetime.now() - timedelta(days=30)

    previous_statuses = db.query(
        CovenantMeasurement.status,
        func.count(func.distinct(CovenantMeasurement.covenant_id)).label('count')
    ).join(
        Covenant
    ).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id,
        Covenant.is_active == True,
        CovenantMeasurement.created_at < thirty_days_ago
    ).group_by(
        CovenantMeasurement.status
    ).all()

    previous_dict = {status: count for status, count in previous_statuses}
    previous_compliant = previous_dict.get('compliant', 0)
    previous_warning = previous_dict.get('warning', 0)
    previous_breach = previous_dict.get('breach', 0)

    # Calculate percentage changes
    def calc_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100.0

    return CovenantTrendsResponse(
        compliant_change=calc_change(current_compliant, previous_compliant),
        warning_change=calc_change(current_warning, previous_warning),
        breach_change=calc_change(current_breach, previous_breach)
    )
