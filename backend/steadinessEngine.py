"""
Steadiness Engine - Calculates income consistency and reliability scores

The core metric: How predictable/stable are a driver's earnings?
This is different from total earnings - you can earn a lot but inconsistently

Steadiness = Key to financial planning and peace of mind
A driver with 72% steadiness knows they can reliably budget their expenses

"""

def get_steadiness_score(driver_id: str, period: str = "weekly"):
    """
    Returns steadiness/consistency score (0-100)
    
    Powers the circular progress chart in Image 1 showing "72%"
    and "More consistent than 72% of Sydney drivers"
    
    Args:
        driver_id: Unique identifier for the driver
        period: Time period to analyze ("daily", "weekly", "monthly")
    
    Returns:
        dict containing:
        - score: 0-100 steadiness rating (higher = more consistent)
        - percentile: Where they rank vs other drivers
        - comparison_text: Human-readable comparison
        - period: What timeframe was analyzed
    
    How score is calculated (real implementation):
    1. Calculate coefficient of variation (CV) of earnings
       CV = standard_deviation / mean
    2. Lower CV = higher steadiness score
    3. Score = 100 - (CV × some scaling factor)
    4. Compare to all drivers to get percentile ranking
    
    Example:
    - Driver A: $800-$850/week (tight range) → High steadiness (85%)
    - Driver B: $500-$1200/week (wide range) → Low steadiness (45%)
    
    Why it matters: Steadier income = easier to plan bills, rent, savings
    """
    return {
        "score": 72,  # 72 out of 100 steadiness score
        "percentile": 72,  # Better than 72% of similar drivers
        # Comparison text shown in UI
        "comparison_text": "More consistent than 72% of Sydney drivers",
        "period": period  # "weekly", "daily", etc.
    }

def get_consistency_breakdown(driver_id: str):
    """
    Returns detailed breakdown of consistency factors
    
    Digs deeper: WHY is someone's steadiness score what it is?
    Breaks down into components: hours worked, earnings rate, and location choices
    
    Args:
        driver_id: Unique identifier for the driver
    
    Returns:
        dict with individual consistency scores for:
        - hour_consistency: Do they work similar hours each week?
        - earnings_consistency: Do they earn similar $/hour each shift?
        - zone_consistency: Do they work in the same areas?
        - overall_score: Combined steadiness score
    
    Use case: Driver has low steadiness - this shows which factor to improve
    
    Real implementation:
    1. Hour consistency: Std dev of hours worked per week
    2. Earnings consistency: Std dev of $ per hour worked
    3. Zone consistency: Entropy of zone distribution
       (low entropy = work same zones, high entropy = all over)
    
    Example insight: "Your hours are consistent (78%) but you work in too 
    many different zones (65%). Focus on your top 2-3 zones to improve."
    """
    return {
        # How consistent are their working hours week-to-week?
        # High score = similar hours each week
        "hour_consistency": 78,
        
        # How consistent are earnings per hour?
        # High score = earning similar rate regardless of when they work
        "earnings_consistency": 72,
        
        # How consistent are the zones they work in?
        # High score = stick to same profitable zones
        "zone_consistency": 65,
        
        # Overall steadiness (from get_steadiness_score)
        "overall_score": 72
    }

def get_volatility_trend(driver_id: str, weeks: int = 12):
    """
    Returns historical volatility over time
    
    Shows whether steadiness is improving or getting worse
    Answers: "Am I getting more consistent over time?"
    
    Args:
        driver_id: Unique identifier for the driver
        weeks: How many weeks to analyze (default 12)
    
    Returns:
        dict containing:
        - current_volatility: Current volatility percentage
        - trend: Array of historical volatility measurements
        - direction: "improving", "stable", or "declining"
    
    Real implementation:
    1. Calculate rolling volatility for each week (use 4-week window)
    2. Track how volatility changes over time
    3. Determine if trend is up/down/flat
    
    Why this matters:
    - Improving trend = driver learning optimal hours/zones
    - Declining trend = might need to adjust strategy
    
    Visualization: Could be shown as a line chart in "Trends" section
    """
    return {
        "current_volatility": 9,  # Current weekly earnings volatility (9%)
        
        # Historical volatility measurements
        # Shows driver's steadiness improving over time (12% → 9%)
        "trend": [
            {"week": "Aug 1", "volatility": 12},   # Started less consistent
            {"week": "Aug 15", "volatility": 11},  # Improving
            {"week": "Sep 1", "volatility": 10},   # Still improving
            {"week": "Sep 15", "volatility": 9},   # More stable now
            {"week": "Oct 1", "volatility": 9}     # Maintaining
        ],
        
        # Overall trend direction
        # "improving" = volatility decreasing (becoming more steady)
        # "declining" = volatility increasing (becoming less steady)
        # "stable" = no significant change
        "direction": "improving"
    }