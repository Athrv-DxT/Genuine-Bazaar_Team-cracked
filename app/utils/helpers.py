"""
Helper utility functions
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd


def filter_data_by_time_range(
    data: List[Any],
    time_range_days: int,
    timestamp_field: str = "timestamp",
) -> List[Any]:
    """Filter data by time range"""
    if not data:
        return []
    
    cutoff_date = datetime.now() - timedelta(days=time_range_days)
    
    filtered = []
    for item in data:
        timestamp = getattr(item, timestamp_field, None)
        if timestamp and timestamp >= cutoff_date:
            filtered.append(item)
    
    return filtered


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Normalize score to 0-1 range"""
    if max_val == min_val:
        return 0.0
    return max(0.0, min(1.0, (score - min_val) / (max_val - min_val)))


def group_by_time_period(
    data: List[Any],
    timestamp_field: str = "timestamp",
    period: str = "D",  # D=day, W=week, M=month
) -> Dict[str, List[Any]]:
    """Group data by time period"""
    if not data:
        return {}
    
    # Convert to DataFrame
    df_data = []
    for item in data:
        timestamp = getattr(item, timestamp_field, None)
        if timestamp:
            df_data.append({
                "timestamp": timestamp,
                "item": item,
            })
    
    if not df_data:
        return {}
    
    df = pd.DataFrame(df_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    
    # Group by period
    grouped = df.groupby(pd.Grouper(freq=period))
    
    result = {}
    for period_key, group in grouped:
        result[period_key.isoformat()] = group["item"].tolist()
    
    return result




