from sqlalchemy.orm import Session
from models.alert import Alert
from typing import Dict, Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class AlertService:
    @staticmethod
    def generate_alerts_from_prediction(
        db: Session,
        user_id: UUID,
        covenant_id: UUID,
        prediction_result: Dict
    ) -> list:
        """
        Generate alerts based on prediction results.
        
        Args:
            db: Database session
            user_id: User ID to notify
            covenant_id: Covenant ID
            prediction_result: Prediction result dictionary
            
        Returns:
            List of created alerts
        """
        alerts = []
        days_to_breach = prediction_result.get('days_to_breach')
        
        if not days_to_breach:
            return alerts
        
        # Critical alert: < 30 days to breach
        if days_to_breach < 30:
            alert = Alert(
                user_id=user_id,
                covenant_id=covenant_id,
                alert_type='breach_warning',
                severity='critical',
                message=f'CRITICAL: Covenant breach predicted in {days_to_breach} days. Immediate action required.',
                is_read=False
            )
            db.add(alert)
            alerts.append(alert)
            logger.info(f"Created critical alert for covenant {covenant_id}")
        
        # Warning alert: 30-90 days to breach
        elif days_to_breach < 90:
            alert = Alert(
                user_id=user_id,
                covenant_id=covenant_id,
                alert_type='breach_warning',
                severity='warning',
                message=f'WARNING: Covenant approaching breach in {days_to_breach} days. Monitor closely.',
                is_read=False
            )
            db.add(alert)
            alerts.append(alert)
            logger.info(f"Created warning alert for covenant {covenant_id}")
        
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Error creating alerts: {e}")
            db.rollback()
        
        return alerts
    
    @staticmethod
    def create_measurement_alert(
        db: Session,
        user_id: UUID,
        covenant_id: UUID,
        is_compliant: bool,
        actual_value: float,
        threshold_value: float
    ):
        """Create alert when measurement indicates compliance issue"""
        if not is_compliant:
            alert = Alert(
                user_id=user_id,
                covenant_id=covenant_id,
                alert_type='breach_occurred',
                severity='critical',
                message=f'BREACH DETECTED: Actual value {actual_value} violates threshold {threshold_value}',
                is_read=False
            )
            db.add(alert)
            try:
                db.commit()
                logger.info(f"Created breach alert for covenant {covenant_id}")
            except Exception as e:
                logger.error(f"Error creating breach alert: {e}")
                db.rollback()

alert_service = AlertService()
