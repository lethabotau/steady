"""
Insights Engine - Analyzes patterns and provides actionable insights

This engine digs into the data to find:
- What makes earnings stable or volatile
- Which hours/zones perform best
- How weather affects earnings
- Upcoming opportunities (events, holidays)

Purpose: Turn raw data into "aha!" moments for drivers
"""

def get_income_stability_metrics(driver_id: str):
    """
    Returns volatility and stability metrics
    
    This powers the "Income Stability" section in Image 2
    Shows the "± 9%" volatility and "$865" 12-week average
    Plus the "Why this matters" insight box
    
    Args:
        driver_id: Unique identifier for the driver
    
    Returns:
        dict containing:
        - volatility_percent: How much earnings fluctuate (lower = more stable)
        - twelve_week_average: Average weekly earnings over 12 weeks
        - insight_text: Human explanation of what drives their stability
    
    Volatility calculation (real implementation):
    1. Calculate standard deviation of weekly earnings
    2. Divide by mean earnings
    3. Express as percentage
    
    Example: If driver averages $850/week with $76.50 std dev
    → volatility = (76.50 / 850) × 100 = 9%
    
    Lower volatility = more predictable income (better for budgeting)
    """
    return {
        "volatility_percent": 9,  # How much earnings vary week-to-week
        "twelve_week_average": 865,  # Mean weekly earnings over 12 weeks
        # Insight explains WHY their earnings are stable/unstable
        # In real version, this would be generated based on actual analysis
        "insight_text": "Your earnings are more stable than 89% of Sydney drivers. Weather patterns and public holidays are your biggest income drivers, with weekend rain consistently boosting demand."
    }

def get_peak_hours_analysis(driver_id: str):
    """
    Returns best performing hours and zones
    
    Answers: "When and where should I work to maximize earnings?"
    
    Args:
        driver_id: Unique identifier for the driver
    
    Returns:
        dict containing:
        - best_hours: Time blocks with highest avg earnings
        - best_zones: Geographic areas with highest earnings
    
    Real implementation would:
    1. Group driver's trips by hour and calculate avg earnings
    2. Rank hours by performance
    3. Calculate consistency (std deviation) for each hour
    4. Do same analysis by geographic zone
    
    Use case: Driver planning their schedule for the week
    """
    return {
        # Best performing time blocks
        # Ranked by average earnings per hour worked
        "best_hours": [
            {
                "hour": "7-9am",  # Time block
                "avg_earnings": 45,  # Average $ per hour in this block
                "consistency": "high"  # How reliable is this time (low variation)
            },
            {
                "hour": "5-7pm",  # Evening rush
                "avg_earnings": 52,  # Highest earner
                "consistency": "high"  # Very reliable
            },
            {
                "hour": "11pm-1am",  # Late night
                "avg_earnings": 38,  # Good earnings
                "consistency": "medium"  # More variable (depends on events/weekend)
            }
        ],
        # Best performing geographic zones
        # Based on historical trips in each area
        "best_zones": [
            {"zone": "Sydney CBD", "avg_hourly": 48},  # Downtown: consistent
            {"zone": "Bondi Beach", "avg_hourly": 42},  # Tourist area: good
            {"zone": "Airport", "avg_hourly": 55}  # Highest: airport runs pay well
        ]
    }

def get_weather_impact_analysis(driver_id: str):
    """
    Returns correlation between weather and earnings
    
    Answers: "How does rain/heat affect my earnings?"
    Many drivers notice they earn more when it rains - this quantifies it
    
    Args:
        driver_id: Unique identifier for the driver
    
    Returns:
        dict containing:
        - rain_boost: Percentage increase in earnings on rainy days
        - temperature_correlation: How temperature affects demand
        - insight: Human-readable summary
    
    Real implementation would:
    1. Match driver's trip data with weather data by date
    2. Compare earnings on rainy vs clear days
    3. Calculate correlation coefficients
    4. Generate insight based on strength of correlation
    
    Why this matters: Drivers can plan to work more hours on predicted rainy days
    """
    return {
        "rain_boost": 23,  # Percentage increase on rainy days (23% more earnings)
        "temperature_correlation": "moderate",  # "weak", "moderate", or "strong"
        # Human explanation of the pattern
        "insight": "Rainy days increase your earnings by 23% on average"
    }

def get_event_opportunities(driver_id: str, upcoming_days: int = 14):
    """
    Returns upcoming events that could boost earnings
    
    Answers: "What special opportunities are coming up?"
    Events like concerts, sports, festivals create surge pricing and high demand
    
    Args:
        driver_id: Unique identifier for the driver
        upcoming_days: How far ahead to look (default 14 days)
    
    Returns:
        dict containing array of events with:
        - Event details (name, date, type)
        - Expected earnings boost (percentage)
        - Recommended zones to work
    
    Real implementation would:
    1. Query event APIs for upcoming events in driver's area
    2. Look up historical earnings impact from similar past events
    3. Predict boost based on event size/type
    4. Recommend best zones based on event location
    
    Use case: "There's a concert Friday - should I work that night?"
    """
    return {
        "events": [
            {
                "name": "Sydney Marathon",  # Event name
                "date": "2026-10-25",  # When it happens
                "expected_boost": 35,  # Expected 35% increase in earnings
                # Where to position yourself for this event
                "recommended_zones": ["City Centre", "Eastern Suburbs"]
            },
            {
                "name": "Concert - Accor Stadium",
                "date": "2026-10-30",
                "expected_boost": 28,  # 28% boost expected
                "recommended_zones": ["Olympic Park"]  # Near the venue
            }
        ]
    }