from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.covenant import Covenant, CovenantMeasurement, CovenantPrediction
from models.loan import LoanAgreement
from schemas import CovenantResponse, MeasurementCreate, MeasurementResponse, PredictionResponse
from routes.auth import get_current_user
from services.prediction_service import prediction_service
from services.alert_service import alert_service
from typing import List
import logging
from uuid import UUID
from datetime import date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/covenants", tags=["Covenants"])

@router.get("/{covenant_id}", response_model=CovenantResponse)
def get_covenant(
    covenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get covenant details"""
    covenant = db.query(Covenant).join(LoanAgreement).filter(
        Covenant.id == UUID(covenant_id),
        LoanAgreement.user_id == current_user.id
    ).first()
    
    if not covenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Covenant not found"
        )
    
    return CovenantResponse.from_orm(covenant)

@router.post("/{covenant_id}/measurements", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
def add_measurement(
    covenant_id: str,
    measurement_data: MeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new covenant measurement"""
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
    
    # Check compliance
    is_compliant = check_compliance(
        float(measurement_data.actual_value),
        float(covenant.threshold_value) if covenant.threshold_value else None,
        covenant.threshold_operator
    )
    
    # Create measurement
    measurement = CovenantMeasurement(
        covenant_id=UUID(covenant_id),
        measurement_date=measurement_data.measurement_date,
        actual_value=measurement_data.actual_value,
        is_compliant=is_compliant,
        notes=measurement_data.notes
    )
    
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    
    # Update covenant status
    update_covenant_status(db, covenant, is_compliant)
    
    # Create alert if non-compliant
    if not is_compliant:
        alert_service.create_measurement_alert(
            db=db,
            user_id=current_user.id,
            covenant_id=UUID(covenant_id),
            is_compliant=is_compliant,
            actual_value=float(measurement_data.actual_value),
            threshold_value=float(covenant.threshold_value) if covenant.threshold_value else 0
        )
    
    # Trigger prediction update
    measurements = db.query(CovenantMeasurement).filter(
        CovenantMeasurement.covenant_id == UUID(covenant_id)
    ).order_by(CovenantMeasurement.measurement_date).all()
    
    if len(measurements) >= 3:
        update_predictions(db, covenant, measurements, current_user.id)
    
    logger.info(f"Added measurement for covenant {covenant_id}")
    
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

@router.get("/{covenant_id}/predictions", response_model=List[PredictionResponse])
def get_predictions(
    covenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get predictions for a covenant"""
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
    
    predictions = db.query(CovenantPrediction).filter(
        CovenantPrediction.covenant_id == UUID(covenant_id)
    ).filter(
        CovenantPrediction.prediction_date >= date.today()
    ).order_by(CovenantPrediction.prediction_date).limit(90).all()
    
    return [PredictionResponse.from_orm(p) for p in predictions]

def check_compliance(actual_value: float, threshold_value: float, operator: str) -> bool:
    """Check if measurement is compliant with threshold"""
    if threshold_value is None or operator is None:
        return True
    
    if operator == '>':
        return actual_value > threshold_value
    elif operator == '<':
        return actual_value < threshold_value
    elif operator == '>=':
        return actual_value >= threshold_value
    elif operator == '<=':
        return actual_value <= threshold_value
    elif operator == '=':
        tolerance = threshold_value * 0.05
        return abs(actual_value - threshold_value) <= tolerance
    
    return True

def update_covenant_status(db: Session, covenant: Covenant, is_compliant: bool):
    """Update covenant status based on latest measurement"""
    if not is_compliant:
        covenant.status = 'breached'
    else:
        covenant.status = 'healthy'
    
    db.commit()

def update_predictions(db: Session, covenant: Covenant, measurements: List, user_id: UUID):
    """Update predictions based on new measurements"""
    # Prepare measurement data
    measurement_data = [
        {
            'measurement_date': m.measurement_date,
            'actual_value': float(m.actual_value)
        }
        for m in measurements
    ]
    
    # Run prediction
    prediction_result = prediction_service.predict_covenant_breach(
        measurements=measurement_data,
        threshold_value=float(covenant.threshold_value) if covenant.threshold_value else None,
        threshold_operator=covenant.threshold_operator
    )
    
    # Delete old predictions
    db.query(CovenantPrediction).filter(
        CovenantPrediction.covenant_id == covenant.id
    ).delete()
    
    # Create new predictions
    for pred in prediction_result.get('predictions', [])[:90]:  # Limit to 90 days
        prediction = CovenantPrediction(
            covenant_id=covenant.id,
            prediction_date=pred['prediction_date'],
            predicted_value=pred['predicted_value'],
            breach_probability=pred['breach_probability'],
            days_to_potential_breach=prediction_result.get('days_to_breach'),
            confidence_score=pred['confidence_score']
        )
        db.add(prediction)
    
    # Update covenant status based on risk
    overall_risk = prediction_result.get('overall_risk', 'healthy')
    if covenant.status != 'breached':  # Don't override breach status
        covenant.status = overall_risk
    
    db.commit()
    
    # Generate alerts
    alert_service.generate_alerts_from_prediction(
        db=db,
        user_id=user_id,
        covenant_id=covenant.id,
        prediction_result=prediction_result
    )
    
    logger.info(f"Updated predictions for covenant {covenant.id}: {overall_risk}")
