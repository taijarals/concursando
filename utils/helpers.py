"""Helper functions for common tasks."""
from datetime import datetime, timedelta
from typing import Optional

def format_date(date: datetime, format_str: str = "%d/%m/%Y") -> str:
    """Format datetime object to string."""
    return date.strftime(format_str)

def get_time_ago(date: datetime) -> str:
    """Get human-readable time difference from now."""
    now = datetime.now()
    diff = now - date
    
    if diff.days == 0:
        if diff.seconds < 60:
            return "agora"
        elif diff.seconds < 3600:
            return f"há {diff.seconds // 60} minutos"
        else:
            return f"há {diff.seconds // 3600} horas"
    elif diff.days == 1:
        return "ontem"
    elif diff.days < 7:
        return f"há {diff.days} dias"
    elif diff.days < 30:
        return f"há {diff.days // 7} semanas"
    else:
        return f"há {diff.days // 30} meses"

def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)

def get_study_streak(dates: list) -> int:
    """Calculate study streak from a list of dates."""
    if not dates:
        return 0
    
    dates_sorted = sorted(dates, reverse=True)
    streak = 1
    
    for i in range(len(dates_sorted) - 1):
        current = dates_sorted[i]
        next_date = dates_sorted[i + 1]
        
        if (current - next_date).days == 1:
            streak += 1
        else:
            break
    
    return streak
