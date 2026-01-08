from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas.loan import AlertResponse
from app.api.deps import get_current_user
from typing import List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    unread_only: bool = False,
    severity: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts for current user"""
    from app.models.loan import LoanAgreement
    
    # Query alerts through loan agreements
    query = db.query(Alert).join(
        LoanAgreement
    ).filter(
        LoanAgreement.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    
    query = query.filter(Alert.is_resolved == False)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return [AlertResponse.from_orm(a) for a in alerts]

@router.put("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_as_read(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as read"""
    from app.models.loan import LoanAgreement
    
    alert = db.query(Alert).join(
        LoanAgreement
    ).filter(
        Alert.id == UUID(alert_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    
    return AlertResponse.from_orm(alert)

@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved"""
    from app.models.loan import LoanAgreement
    
    alert = db.query(Alert).join(
        LoanAgreement
    ).filter(
        Alert.id == UUID(alert_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_resolved = True
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    
    return AlertResponse.from_orm(alert)

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    from app.models.loan import LoanAgreement
    
    alert = db.query(Alert).join(
        LoanAgreement
    ).filter(
        Alert.id == UUID(alert_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return None
