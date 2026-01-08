from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """
    ML prediction engine for covenant breach forecasting.
    Uses linear regression with R² confidence scoring.
    """
    
    def predict_breach_date(
        self, 
        historical_values: List[Dict], 
        threshold_value: Optional[float],
        threshold_operator: Optional[str]
    ) -> Optional[Dict]:
        """
        Predict when a covenant will breach based on historical trend.
        
        Args:
            historical_values: List of {"date": "2024-01-01", "value": 3.5}
            threshold_value: Covenant threshold (e.g., 4.0 for Debt/EBITDA)
            threshold_operator: 'less_than', 'greater_than', 'less_or_equal', 'greater_or_equal', 'equal'
        
        Returns:
            {
                "predicted_breach_date": "2024-06-15",
                "days_until_breach": 47,
                "confidence": 0.85,
                "current_trajectory": "improving|deteriorating|stable",
                "predicted_value_at_breach": 4.2
            }
            or None if no breach predicted in next 365 days
        """
        
        if len(historical_values) < 3:
            logger.info("Insufficient data for prediction (need at least 3 measurements)")
            return None
        
        if threshold_value is None or threshold_operator is None:
            logger.info("Missing threshold information, cannot predict breach")
            return None
        
        try:
            # Convert dates to numeric (days since first measurement)
            sorted_data = sorted(historical_values, key=lambda x: x['date'])
            first_date = datetime.fromisoformat(sorted_data[0]['date'])
            
            X = []  # Days since first measurement
            y = []  # Covenant values
            
            for item in sorted_data:
                date = datetime.fromisoformat(item['date'])
                days_diff = (date - first_date).days
                X.append([days_diff])
                y.append(item['value'])
            
            # Train linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate R² score (confidence metric)
            r_squared = model.score(X, y)
            
            # Get slope for trajectory analysis
            slope = model.coef_[0]
            
            # Determine trajectory
            if abs(slope) < 0.01:  # Very small slope
                trajectory = "stable"
            elif threshold_operator in ['less_than', 'less_or_equal']:
                trajectory = "deteriorating" if slope > 0 else "improving"
            else:  # greater_than or greater_or_equal
                trajectory = "deteriorating" if slope < 0 else "improving"
            
            # Predict breach date (check next 365 days)
            current_date = datetime.fromisoformat(sorted_data[-1]['date'])
            last_days = X[-1][0]
            
            for future_days in range(1, 366):
                predicted_value = model.predict([[last_days + future_days]])[0]
                
                breach_occurred = self._check_breach(
                    predicted_value, 
                    threshold_value, 
                    threshold_operator
                )
                
                if breach_occurred:
                    breach_date = current_date + timedelta(days=future_days)
                    return {
                        "predicted_breach_date": breach_date.date().isoformat(),
                        "days_until_breach": future_days,
                        "confidence": round(min(r_squared, 0.99), 2),  # Cap at 99%
                        "current_trajectory": trajectory,
                        "predicted_value_at_breach": round(predicted_value, 4)
                    }
            
            # No breach predicted in next year
            logger.info("No breach predicted in next 365 days")
            return None
            
        except Exception as e:
            logger.error(f"Error in prediction calculation: {e}")
            return None
    
    def _check_breach(self, actual_value: float, threshold_value: float, operator: str) -> bool:
        """Check if value breaches threshold based on operator"""
        if operator == 'less_than':
            return actual_value >= threshold_value
        elif operator == 'greater_than':
            return actual_value <= threshold_value
        elif operator == 'less_or_equal':
            return actual_value > threshold_value
        elif operator == 'greater_or_equal':
            return actual_value < threshold_value
        elif operator == 'equal':
            tolerance = threshold_value * 0.05  # 5% tolerance
            return abs(actual_value - threshold_value) > tolerance
        
        return False

prediction_service = PredictionService()
