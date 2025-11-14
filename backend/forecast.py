"""
Forecast Engine - Predicts future earnings based on historical data, weather, and events

This engine analyzes:
- Historical earnings patterns (from driverX.csv)
- Weather conditions (from weather.csv)
- Upcoming events/holidays (from events.csv)
- Time-based trends (seasonality, day-of-week patterns)

Output: Earnings predictions with confidence intervals
"""

import features as features
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

def get_weekly_forecast(driver_id: str, target_week: str):
    """
    Returns weekly earnings forecast with confidence interval
    
    This is what powers the main forecast card on the Home tab (Image 1)
    showing "$930 + $60" and "Likely to rise significantly next week"
    
    Args:
        driver_id: Unique identifier for the driver (e.g., "driver1")
        target_week: ISO date string for the week to forecast (e.g., "2026-10-06")
    
    Returns:
        dict containing:
        - forecast: Predicted earnings amount ($930 in mockup)
        - change: Dollar change from previous week (+$60)
        - change_direction: "up" or "down" (determines arrow icon)
        - confidence_interval: Range of likely outcomes (for uncertainty visualization)
        - likelihood_text: Human-readable confidence statement
    """
    
    # Load all necessary data sources
    all_features = features.build_features(driver_id, target_week)
    weekly_data = all_features['weekly_aggregates']
    weather_features = all_features['weather_features']
    event_features = all_features['event_features']
    
    # STEP 1: Calculate baseline from recent history (last 4 weeks average)
    recent_weeks = weekly_data[-4:] if len(weekly_data) >= 4 else weekly_data
    baseline_earnings = sum(w['earnings'] for w in recent_weeks) / len(recent_weeks)
    
    # STEP 2: Calculate trend multiplier (is driver improving over time?)
    # Compare first half vs second half of historical data
    if len(weekly_data) >= 8:
        first_half_avg = sum(w['earnings'] for w in weekly_data[:4]) / 4
        second_half_avg = sum(w['earnings'] for w in weekly_data[-4:]) / 4
        trend_multiplier = second_half_avg / first_half_avg if first_half_avg > 0 else 1.0
    else:
        trend_multiplier = 1.0
    
    # STEP 3: Apply weather boost
    # Count rainy days in target week and apply earnings boost
    weather_multiplier = 1.0
    rainy_days = sum(1 for day in weather_features['data'] if day['condition'] in ['rain', 'storm'])
    if rainy_days > 0:
        # Each rainy day adds ~3.5% boost (25% boost distributed across 7 days)
        weather_multiplier = 1.0 + (rainy_days * 0.035)
    
    # STEP 4: Apply event boost
    # Check for events in target week and add expected impact
    event_multiplier = 1.0
    target_date = datetime.strptime(target_week, '%Y-%m-%d')
    week_end = target_date + timedelta(days=7)
    
    for event in event_features['events'] + event_features['holidays']:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        if target_date <= event_date < week_end:
            # Convert expected_impact percentage to multiplier
            # Events typically boost only 1-2 days, so divide impact by 7
            event_multiplier += (event['expected_impact'] / 100) / 7
    
    # STEP 5: Calculate final forecast
    forecast_amount = baseline_earnings * trend_multiplier * weather_multiplier * event_multiplier
    forecast_amount = round(forecast_amount, 2)
    
    # STEP 6: Calculate change from most recent week
    most_recent_earnings = weekly_data[-1]['earnings'] if weekly_data else 0
    change = round(forecast_amount - most_recent_earnings, 2)
    change_direction = "up" if change >= 0 else "down"
    
    # STEP 7: Calculate confidence interval
    # Use standard deviation of recent weeks to estimate uncertainty
    if len(recent_weeks) >= 3:
        earnings_list = [w['earnings'] for w in recent_weeks]
        std_dev = statistics.stdev(earnings_list)
    else:
        std_dev = baseline_earnings * 0.10  # Default to 10% if not enough data
    
    # 95% confidence interval (approximately ±2 standard deviations)
    confidence_interval = {
        "lower": round(forecast_amount - (1.5 * std_dev), 2),
        "upper": round(forecast_amount + (1.5 * std_dev), 2)
    }
    
    # STEP 8: Generate likelihood text based on factors
    likelihood_parts = []
    if abs(change) > 50:
        if change > 0:
            likelihood_parts.append("rise significantly")
        else:
            likelihood_parts.append("decrease")
    else:
        likelihood_parts.append("remain stable")
    
    # Add reason for change
    if rainy_days >= 2:
        likelihood_parts.append("due to rainy weather")
    elif event_multiplier > 1.02:
        likelihood_parts.append("due to upcoming events")
    
    likelihood_text = "Likely to " + " ".join(likelihood_parts) + " next week"
    
    return {
        "week": target_week,
        "forecast": forecast_amount,
        "change": change,
        "change_direction": change_direction,
        "confidence_interval": confidence_interval,
        "likelihood_text": likelihood_text
    }

def get_forecast_chart_data(driver_id: str, weeks: int = 8):
    """
    Returns time series data for forecast visualization
    
    This powers the line chart in Image 2 showing earnings over time
    with both historical (solid line) and forecast (dashed line) data
    
    Args:
        driver_id: Unique identifier for the driver
        weeks: How many historical weeks to return (default 8)
    
    Returns:
        dict containing:
        - historical: Array of past weekly earnings (actual data)
        - forecast: Array of future predictions (starts from last historical point)
        - forecast_range: Label for confidence interval shading
    """
    
    # Load historical weekly data
    weekly_data = features.get_weekly_aggregates(driver_id, weeks=weeks)
    
    # STEP 1: Format historical data for chart
    historical = []
    for week in weekly_data:
        # Convert date to readable format (e.g., "Oct 18")
        date_obj = datetime.strptime(week['week_start'], '%Y-%m-%d')
        date_label = date_obj.strftime("%b %d")
        
        historical.append({
            "date": date_label,
            "value": week['earnings']
        })
    
    # STEP 2: Generate forecast for next 2 weeks
    forecast_data = []
    
    if len(weekly_data) > 0:
        # Start from the last historical point
        last_week = weekly_data[-1]
        last_date = datetime.strptime(last_week['week_start'], '%Y-%m-%d')
        last_earnings = last_week['earnings']
        
        # Add the overlap point (connects historical to forecast line)
        forecast_data.append({
            "date": last_date.strftime("%b %d"),
            "value": last_earnings
        })
        
        # Forecast next week
        next_week_date = last_date + timedelta(weeks=1)
        next_week_str = next_week_date.strftime('%Y-%m-%d')
        next_week_forecast = get_weekly_forecast(driver_id, next_week_str)
        
        forecast_data.append({
            "date": next_week_date.strftime("%b %d"),
            "value": next_week_forecast['forecast']
        })
    
    return {
        "historical": historical,
        "forecast": forecast_data,
        "forecast_range": "Forecast range"
    }

def get_daily_forecast(driver_id: str, date: str):
    """
    Returns hourly earnings forecast for a specific day
    
    Used for detailed daily planning - shows which hours are most profitable
    Helps drivers decide when to work on a specific day
    
    Args:
        driver_id: Unique identifier for the driver
        date: ISO date string (e.g., "2026-10-20")
    
    Returns:
        dict containing:
        - date: The day being forecasted
        - total_forecast: Expected total earnings for the full day
        - hourly: Array of hour-by-hour predictions
    """
    
    # Load driver's historical daily data
    daily_data = features.get_daily_aggregates(driver_id, days=90)
    all_features = features.build_features(driver_id, date)
    
    # Determine day of week for the target date
    target_date = datetime.strptime(date, '%Y-%m-%d')
    day_of_week = target_date.strftime('%A')
    
    # STEP 1: Calculate baseline hourly earnings for similar days
    # Filter historical data for same day of week
    similar_days = [d for d in daily_data if d['day_of_week'] == day_of_week]
    
    if similar_days:
        avg_daily_earnings = sum(d['earnings'] for d in similar_days) / len(similar_days)
        avg_daily_hours = sum(d['hours'] for d in similar_days) / len(similar_days)
        base_hourly_rate = avg_daily_earnings / avg_daily_hours if avg_daily_hours > 0 else 40
    else:
        # Default if no historical data for this day
        base_hourly_rate = 40
        avg_daily_earnings = 150
    
    # STEP 2: Check weather for the target date
    weather_data = all_features['weather_features']['data']
    target_weather = next((w for w in weather_data if w['date'] == date), None)
    
    weather_multiplier = 1.0
    if target_weather and target_weather['condition'] in ['rain', 'storm']:
        weather_multiplier = 1.25  # 25% boost for rain
    
    # STEP 3: Check for events on target date
    event_features = all_features['event_features']
    events_today = [e for e in event_features['events'] + event_features['holidays'] 
                    if e['date'] == date]
    
    event_multiplier = 1.0
    if events_today:
        # Average the impact of all events
        avg_impact = sum(e['expected_impact'] for e in events_today) / len(events_today)
        event_multiplier = 1.0 + (avg_impact / 100)
    
    # STEP 4: Define hourly patterns (typical demand throughout the day)
    # Weekend vs weekday have different patterns
    is_weekend = day_of_week in ['Saturday', 'Sunday']
    
    if is_weekend:
        # Weekend pattern: steadier throughout day, peak late evening
        hourly_patterns = [
            {"hour": "6am", "multiplier": 0.7},
            {"hour": "9am", "multiplier": 0.9},
            {"hour": "12pm", "multiplier": 1.0},
            {"hour": "3pm", "multiplier": 0.95},
            {"hour": "6pm", "multiplier": 1.1},
            {"hour": "9pm", "multiplier": 1.2},
        ]
    else:
        # Weekday pattern: morning and evening peaks
        hourly_patterns = [
            {"hour": "6am", "multiplier": 0.6},
            {"hour": "9am", "multiplier": 1.15},  # Morning rush
            {"hour": "12pm", "multiplier": 1.0},  # Lunch
            {"hour": "3pm", "multiplier": 0.75},  # Afternoon lull
            {"hour": "6pm", "multiplier": 1.2},   # Evening rush (peak)
            {"hour": "9pm", "multiplier": 0.8},
        ]
    
    # STEP 5: Calculate earnings for each hour block
    hourly_forecast = []
    total_forecast = 0
    
    for pattern in hourly_patterns:
        # Base rate * time-of-day multiplier * weather * events
        hourly_earnings = (base_hourly_rate * pattern['multiplier'] * 
                          weather_multiplier * event_multiplier)
        hourly_earnings = round(hourly_earnings, 2)
        
        hourly_forecast.append({
            "hour": pattern['hour'],
            "earnings": hourly_earnings
        })
        
        total_forecast += hourly_earnings
    
    return {
        "date": date,
        "total_forecast": round(total_forecast, 2),
        "hourly": hourly_forecast
    }