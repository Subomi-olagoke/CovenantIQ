from decimal import Decimal
from typing import Optional

def calculate_distance_to_breach(
    actual_value: float, 
    threshold_value: float, 
    operator: str
) -> float:
    """
    Calculate distance to breach.
    Positive values = safe, negative values = breach.
    
    Args:
        actual_value: Current measurement value
        threshold_value: Covenant threshold
        operator: Threshold operator (less_than, greater_than, etc.)
        
    Returns:
        Distance to breach (positive = safe margin, negative = breach amount)
    """
    if operator in ['less_than', 'less_or_equal']:
        # Value must stay below threshold
        # Distance = threshold - actual (positive = room to grow, negative = breach)
        return threshold_value - actual_value
    elif operator in ['greater_than', 'greater_or_equal']:
        # Value must stay above threshold  
        # Distance = actual - threshold (positive = cushion above, negative = breach)
        return actual_value - threshold_value
    elif operator == 'equal':
        # Value must equal threshold (within 5% tolerance)
        return 0.0
    
    return 0.0

def determine_measurement_status(
    actual_value: float,
    threshold_value: float,
    operator: str
) -> str:
    """
    Determine covenant measurement status.
    
    Returns:
        'compliant', 'warning', or 'breach'
    """
    distance = calculate_distance_to_breach(actual_value, threshold_value, operator)
    
    if distance < 0:
        return 'breach'
    elif distance < (threshold_value * 0.1):  # Within 10% of threshold
        return 'warning'
    else:
        return 'compliant'
