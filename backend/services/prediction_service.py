from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.model = LinearRegression()
    
    def predict_covenant_breach(
        self, 
        measurements: List[Dict],
        threshold_value: Optional[float],
        threshold_operator: Optional[str],
        days_forward: int = 90
    ) -> Dict:
        """
        Predict future covenant values and breach probability.
        
        Args:
            measurements: List of dicts with 'measurement_date' and 'actual_value'
            threshold_value: Covenant threshold value
            threshold_operator: Comparison operator (>, <, >=, <=, =)
            days_forward: Number of days to predict forward
            
        Returns:
            Dictionary with predictions and breach analysis
        """
        if len(measurements) < 3:
            return self._conservative_prediction(measurements, threshold_value, threshold_operator)
        
        try:
            # Prepare time series data
            df = pd.DataFrame(measurements)
            df['measurement_date'] = pd.to_datetime(df['measurement_date'])
            df = df.sort_values('measurement_date')
            
            # Calculate days from start
            df['days_from_start'] = (df['measurement_date'] - df['measurement_date'].min()).dt.days
            
            X = df[['days_from_start']].values
            y = df['actual_value'].values.astype(float)
            
            # Fit linear regression
            self.model.fit(X, y)
            
            # Predict next N days
            last_day = int(X[-1][0])
            last_date = df['measurement_date'].max()
            
            future_days = np.array([[last_day + i] for i in range(1, days_forward + 1)])
            predictions = self.model.predict(future_days)
            
            # Calculate breach conditions
            breach_predictions = self._check_breach_conditions(
                predictions, threshold_value, threshold_operator
            ) if threshold_value is not None else [False] * len(predictions)
            
            # Find first breach date
            days_to_breach = None
            for i, will_breach in enumerate(breach_predictions):
                if will_breach:
                    days_to_breach = i + 1
                    break
            
            # Generate prediction results
            prediction_list = []
            for i, pred in enumerate(predictions):
                pred_date = last_date + timedelta(days=i+1)
                prediction_list.append({
                    'prediction_date': pred_date.date(),
                    'predicted_value': float(pred),
                    'breach_probability': self._calculate_breach_probability(i, days_to_breach),
                    'confidence_score': self._calculate_confidence(y, predictions, i)
                })
            
            # Determine overall risk
            overall_risk = 'healthy'
            if days_to_breach:
                if days_to_breach < 30:
                    overall_risk = 'critical'
                elif days_to_breach < 90:
                    overall_risk = 'warning'
            
            return {
                'predictions': prediction_list,
                'days_to_breach': days_to_breach,
                'overall_risk': overall_risk,
                'trend': 'increasing' if self.model.coef_[0] > 0 else 'decreasing'
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return self._conservative_prediction(measurements, threshold_value, threshold_operator)
    
    def _check_breach_conditions(
        self, 
        values: np.ndarray, 
        threshold: float, 
        operator: str
    ) -> List[bool]:
        """Check if predicted values breach covenant threshold"""
        if operator == '>':
            return (values < threshold).tolist()
        elif operator == '<':
            return (values > threshold).tolist()
        elif operator == '>=':
            return (values < threshold).tolist()
        elif operator == '<=':
            return (values > threshold).tolist()
        elif operator == '=':
            tolerance = threshold * 0.05  # 5% tolerance
            return (np.abs(values - threshold) > tolerance).tolist()
        return [False] * len(values)
    
    def _calculate_breach_probability(self, day_index: int, days_to_breach: Optional[int]) -> float:
        """Calculate probability of breach for a given prediction day"""
        if days_to_breach is None:
            return 0.0
        
        if day_index >= days_to_breach:
            # After predicted breach, probability increases
            return min(95.0, 50.0 + (day_index - days_to_breach) * 2)
        else:
            # Before predicted breach, probability increases as we approach
            return (day_index / days_to_breach) * 50.0
    
    def _calculate_confidence(self, historical: np.ndarray, predictions: np.ndarray, index: int) -> float:
        """Calculate confidence score based on data quality and trend consistency"""
        # Base confidence on amount of historical data
        data_confidence = min(90.0, 50.0 + len(historical) * 5)
        
        # Adjust based on prediction distance
        distance_penalty = index * 0.5
        
        final_confidence = max(50.0, data_confidence - distance_penalty)
        return round(final_confidence, 2)
    
    def _conservative_prediction(
        self, 
        measurements: List[Dict],
        threshold_value: Optional[float],
        threshold_operator: Optional[str]
    ) -> Dict:
        """Return conservative prediction when insufficient data"""
        return {
            'predictions': [],
            'days_to_breach': None,
            'overall_risk': 'healthy',
            'trend': 'insufficient_data',
            'message': 'Insufficient historical data for reliable predictions (minimum 3 measurements required)'
        }

prediction_service = PredictionService()
