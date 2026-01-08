from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.covenant import Covenant, CovenantMeasurement
from app.models.loan import LoanAgreement
from app.models.alert import Alert
from app.schemas.loan import CovenantResponse, MeasurementCreate, MeasurementResponse
from app.api.deps import get_current_user
from app.services.prediction_service import prediction_service
from app.utils.helpers import calculate_distance_to_breach, determine_measurement_status
from typing import List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/covenants", tags=["Covenants"])

@router.get("/{covenant_id}", response_model=CovenantResponse)
def get_covenant(
    covenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get covenant details with latest measurement"""
    covenant = db.query(Covenant).join(LoanAgreement).filter(
        Covenant.id == UUID(covenant_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not covenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covenant not found"
        )
    
    # Get latest measurement
    latest = db.query(CovenantMeasurement).filter(
        CovenantMeasurement.covenant_id == UUID(covenant_id)
    ).order_by(CovenantMeasurement.measurement_date.desc()).first()
    
    cov_dict = CovenantResponse.from_orm(covenant).dict()
    if latest:
        cov_dict['latest_status'] = latest.status
        cov_dict['latest_value'] = float(latest.actual_value)
    
    return CovenantResponse(**cov_dict)

@router.post("/{covenant_id}/measurements", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
def add_measurement(
    covenant_id: str,
    measurement_data: MeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new covenant measurement and trigger predictions"""
    # Verify covenant belongs to user
    covenant = db.query(Covenant).join(LoanAgreement).filter(
        Covenant.id == UUID(covenant_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not covenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covenant not found"
        )
    
    # Calculate status and distance to breach
    actual_value = float(measurement_data.actual_value)
    threshold_value = float(covenant.threshold_value) if covenant.threshold_value else None
    
    if threshold_value and covenant.threshold_operator:
        status_result = determine_measurement_status(
            actual_value,
            threshold_value,
            covenant.threshold_operator
        )
        distance = calculate_distance_to_breach(
            actual_value,
            threshold_value,
            covenant.threshold_operator
        )
    else:
        status_result = 'compliant'
        distance = None
        threshold_value = None
    
    # Create measurement
    measurement = CovenantMeasurement(
        covenant_id=UUID(covenant_id),
        measurement_date=measurement_data.measurement_date,
        actual_value=measurement_data.actual_value,
        threshold_value=threshold_value,
        status=status_result,
        distance_to_breach=distance,
        notes=measurement_data.notes
    )
    
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    
    # Create alert if breach
    if status_result == 'breach':
        alert = Alert(
            covenant_id=UUID(covenant_id),
            loan_agreement_id=covenant.loan_agreement_id,
            alert_type='breach',
            severity='critical',
            title=f'Covenant Breach: {covenant.covenant_name}',
            message=f'Covenant has breached threshold. Actual: {actual_value}, Threshold: {threshold_value}',
            is_read=False,
            is_resolved=False
        )
        db.add(alert)
        db.commit()
    
    # Trigger prediction update
    measurements = db.query(CovenantMeasurement).filter(
        CovenantMeasurement.covenant_id == UUID(covenant_id)
    ).order_by(CovenantMeasurement.measurement_date).all()
    
    if len(measurements) >= 3 and threshold_value:
        historical_data = [
            {
                'date': m.measurement_date.isoformat(),
                'value': float(m.actual_value)
            }
            for m in measurements
        ]
        
        prediction_result = prediction_service.predict_breach_date(
            historical_data,
            threshold_value,
            covenant.threshold_operator
        )
        
        if prediction_result:
            days_until = prediction_result['days_until_breach']
            
            # Determine severity based on days
            if days_until <= 30:
                severity = 'critical'
            elif days_until <= 60:
                severity = 'high'
            else:
                severity = 'medium'
            
            alert = Alert(
                covenant_id=UUID(covenant_id),
                loan_agreement_id=covenant.loan_agreement_id,
                alert_type='prediction',
                severity=severity,
                title=f'Predicted Breach: {covenant.covenant_name}',
                message=f'Breach predicted in {days_until} days. Confidence: {int(prediction_result["confidence"] * 100)}%',
                predicted_breach_date=prediction_result['predicted_breach_date'],
                days_until_breach=days_until,
                is_read=False,
                is_resolved=False
            )
            db.add(alert)
            db.commit()
    
    logger.info(f"Added measurement for covenant {covenant_id}, status: {status_result}")
    
    return MeasurementResponse.from_orm(measurement)

@router.get("/{covenant_id}/measurements", response_model=List[MeasurementResponse])
def get_measurements(
    covenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all measurements for a covenant"""
    # Verify covenant belongs to user
    covenant = db.query(Covenant).join(LoanAgreement).filter(
        Covenant.id == UUID(covenant_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not covenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covenant not found"
        )
    
    measurements = db.query(CovenantMeasurement).filter(
        CovenantMeasurement.covenant_id == UUID(covenant_id)
    ).order_by(CovenantMeasurement.measurement_date.desc()).all()
    
    return [MeasurementResponse.from_orm(m) for m in measurements]

@router.get("/{covenant_id}/prediction")
def get_covenant_prediction(
    covenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get breach prediction for a covenant"""
    # Verify covenant
    covenant = db.query(Covenant).join(LoanAgreement).filter(
        Covenant.id == UUID(covenant_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not covenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covenant not found"
        )
    
    if not covenant.threshold_value or not covenant.threshold_operator:
        return {"prediction": None, "message": "No threshold defined for covenant"}
    
    # Get historical measurements
    measurements = db.query(CovenantMeasurement).filter(
        CovenantMeasurement.covenant_id == UUID(covenant_id)
    ).order_by(CovenantMeasurement.measurement_date).all()
    
    if len(measurements) < 3:
        return {"prediction": None, "message": "Insufficient historical data (minimum 3 measurements required)"}
    
    historical_data = [
        {
            'date': m.measurement_date.isoformat(),
            'value': float(m.actual_value)
        }
        for m in measurements
    ]
    
    prediction_result = prediction_service.predict_breach_date(
        historical_data,
        float(covenant.threshold_value),
        covenant.threshold_operator
    )
    
    return {"prediction": prediction_result}
