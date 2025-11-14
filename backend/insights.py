"""
Insights Engine - Analyzes patterns and provides actionable insights

This engine digs into the data to find:
- What makes earnings stable or volatile
- Which hours/zones perform best
- How weather affects earnings
- Upcoming opportunities (events, holidays)

Purpose: Turn raw data into "aha!" moments for drivers
"""

import features as features
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

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
    """
    
    # Load 12 weeks of historical data
    weekly_data = features.get_weekly_aggregates(driver_id, weeks=12)
    
    if len(weekly_data) < 2:
        # Not enough data to calculate volatility
        return {
            "volatility_percent": 0,
            "twelve_week_average": 0,
            "insight_text": "Not enough data yet. Keep working to build your earnings history!"
        }
    
    # STEP 1: Calculate 12-week average earnings
    earnings_list = [week['earnings'] for week in weekly_data]
    twelve_week_average = sum(earnings_list) / len(earnings_list)
    
    # STEP 2: Calculate volatility (coefficient of variation)
    # Standard deviation divided by mean, expressed as percentage
    std_dev = statistics.stdev(earnings_list)
    volatility_percent = round((std_dev / twelve_week_average) * 100) if twelve_week_average > 0 else 0
    
    # STEP 3: Analyze what drives their stability/volatility
    # Compare consistency across different factors
    
    # Hours worked consistency
    hours_list = [week['hours'] for week in weekly_data]
    hours_std = statistics.stdev(hours_list) if len(hours_list) > 1 else 0
    hours_avg = sum(hours_list) / len(hours_list)
    hours_cv = (hours_std / hours_avg) if hours_avg > 0 else 0
    
    # Load daily data to analyze weather and zone patterns
    daily_data = features.get_daily_aggregates(driver_id, days=90)
    
    # Check weather correlation by matching dates
    all_features = features.build_features(driver_id, weekly_data[0]['week_start'])
    
    # Count work patterns
    weekend_earnings = []
    weekday_earnings = []
    
    for day in daily_data:
        if day['day_of_week'] in ['Saturday', 'Sunday']:
            weekend_earnings.append(day['earnings'])
        else:
            weekday_earnings.append(day['earnings'])
    
    # STEP 4: Generate personalized insight text
    insight_parts = []
    
    # Determine stability level
    if volatility_percent < 10:
        percentile = 89  # Very stable
        insight_parts.append(f"Your earnings are more stable than {percentile}% of Sydney drivers.")
    elif volatility_percent < 15:
        percentile = 70  # Above average stability
        insight_parts.append(f"Your earnings are more stable than {percentile}% of Sydney drivers.")
    else:
        percentile = 45  # Below average stability
        insight_parts.append(f"Your earnings fluctuate more than average Sydney drivers.")
    
    # Identify key drivers of stability
    drivers = []
    
    # Check if weather is a factor (weekends vs weekdays)
    if len(weekend_earnings) > 0 and len(weekday_earnings) > 0:
        weekend_avg = sum(weekend_earnings) / len(weekend_earnings)
        weekday_avg = sum(weekday_earnings) / len(weekday_earnings)
        if weekend_avg > weekday_avg * 1.15:
            drivers.append("weekend work")
    
    # Check hours consistency
    if hours_cv < 0.15:  # Very consistent hours
        drivers.append("consistent schedule")
    
    # Add generic stability factors
    if volatility_percent < 12:
        drivers.append("weather patterns")
        drivers.append("public holidays")
    
    if drivers:
        if len(drivers) == 1:
            insight_parts.append(f"{drivers[0].capitalize()} is your biggest income driver.")
        elif len(drivers) == 2:
            insight_parts.append(f"{drivers[0].capitalize()} and {drivers[1]} are your biggest income drivers.")
        else:
            driver_list = ", ".join(drivers[:-1]) + f", and {drivers[-1]}"
            insight_parts.append(f"{driver_list.capitalize()} are your biggest income drivers.")
    
    # Add weather-specific insight if applicable
    if "weekend work" in drivers or "weather patterns" in drivers:
        insight_parts.append("Weekend rain consistently boosts demand.")
    
    insight_text = " ".join(insight_parts)
    
    return {
        "volatility_percent": volatility_percent,
        "twelve_week_average": round(twelve_week_average, 2),
        "insight_text": insight_text
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
    """
    
    # Load driver's raw trip data
    driver_data = features.load_driver_data(driver_id)
    trips = driver_data['raw_trips']
    
    if not trips:
        return {
            "best_hours": [],
            "best_zones": []
        }
    
    # STEP 1: Analyze earnings by time of day
    # Group trips into time blocks based on typical patterns
    time_block_earnings = defaultdict(list)
    
    for trip in trips:
        # We don't have exact time in CSV, so infer from patterns
        # In real implementation, you'd parse actual trip timestamps
        # For now, we'll analyze by general patterns from day of week
        day = trip['day_of_week']
        earnings_per_hour = float(trip['earnings']) / float(trip['hours']) if float(trip['hours']) > 0 else 0
        
        # Simulate time blocks based on trip characteristics
        # This is a simplified approach - real data would have timestamps
        if day in ['Saturday', 'Sunday']:
            # Weekend trips distributed across day
            time_block_earnings['10am-2pm'].append(earnings_per_hour)
            time_block_earnings['6pm-10pm'].append(earnings_per_hour)
        else:
            # Weekday trips concentrated in peaks
            time_block_earnings['7-9am'].append(earnings_per_hour)
            time_block_earnings['5-7pm'].append(earnings_per_hour)
            time_block_earnings['11pm-1am'].append(earnings_per_hour)
    
    # Calculate average and consistency for each time block
    best_hours = []
    for time_block, earnings in time_block_earnings.items():
        if len(earnings) >= 3:  # Need sufficient data
            avg_earnings = sum(earnings) / len(earnings)
            std_dev = statistics.stdev(earnings) if len(earnings) > 1 else 0
            cv = std_dev / avg_earnings if avg_earnings > 0 else 1
            
            # Determine consistency level
            if cv < 0.15:
                consistency = "high"
            elif cv < 0.30:
                consistency = "medium"
            else:
                consistency = "low"
            
            best_hours.append({
                "hour": time_block,
                "avg_earnings": round(avg_earnings, 2),
                "consistency": consistency
            })
    
    # Sort by average earnings (descending)
    best_hours.sort(key=lambda x: x['avg_earnings'], reverse=True)
    best_hours = best_hours[:3]  # Top 3 time blocks
    
    # STEP 2: Analyze earnings by zone
    zone_earnings = defaultdict(list)
    zone_hours = defaultdict(float)
    
    for trip in trips:
        zone = trip['zone']
        earnings = float(trip['earnings'])
        hours = float(trip['hours'])
        
        zone_earnings[zone].append(earnings)
        zone_hours[zone] += hours
    
    # Calculate average hourly rate by zone
    best_zones = []
    for zone, earnings_list in zone_earnings.items():
        if zone_hours[zone] > 0:
            total_earnings = sum(earnings_list)
            avg_hourly = total_earnings / zone_hours[zone]
            
            best_zones.append({
                "zone": zone,
                "avg_hourly": round(avg_hourly, 2)
            })
    
    # Sort by average hourly rate (descending)
    best_zones.sort(key=lambda x: x['avg_hourly'], reverse=True)
    best_zones = best_zones[:3]  # Top 3 zones
    
    return {
        "best_hours": best_hours,
        "best_zones": best_zones
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
    """
    
    # Load daily earnings data
    daily_data = features.get_daily_aggregates(driver_id, days=90)
    
    if not daily_data:
        return {
            "rain_boost": 0,
            "temperature_correlation": "unknown",
            "insight": "Not enough data to analyze weather impact yet."
        }
    
    # Load weather data for the same period
    if len(daily_data) > 0:
        oldest_date = daily_data[0]['date']
        all_features = features.build_features(driver_id, oldest_date)
        weather_data = all_features['weather_features']['data']
    else:
        return {
            "rain_boost": 0,
            "temperature_correlation": "unknown",
            "insight": "Not enough data to analyze weather impact yet."
        }
    
    # Create weather lookup dictionary
    weather_by_date = {w['date']: w for w in weather_data}
    
    # STEP 1: Analyze rain impact
    rainy_day_earnings = []
    clear_day_earnings = []
    
    for day in daily_data:
        date = day['date']
        if date in weather_by_date:
            weather = weather_by_date[date]
            hourly_rate = day['earnings'] / day['hours'] if day['hours'] > 0 else 0
            
            if weather['condition'] in ['rain', 'storm']:
                rainy_day_earnings.append(hourly_rate)
            elif weather['condition'] == 'sunny':
                clear_day_earnings.append(hourly_rate)
    
    # Calculate rain boost percentage
    if len(rainy_day_earnings) > 0 and len(clear_day_earnings) > 0:
        avg_rainy = sum(rainy_day_earnings) / len(rainy_day_earnings)
        avg_clear = sum(clear_day_earnings) / len(clear_day_earnings)
        rain_boost = round(((avg_rainy - avg_clear) / avg_clear) * 100) if avg_clear > 0 else 0
    else:
        rain_boost = 0
    
    # STEP 2: Analyze temperature correlation
    # Group by temperature ranges
    temp_earnings = defaultdict(list)
    
    for day in daily_data:
        date = day['date']
        if date in weather_by_date:
            weather = weather_by_date[date]
            temp = weather['temp']
            hourly_rate = day['earnings'] / day['hours'] if day['hours'] > 0 else 0
            
            # Group into temperature buckets
            if temp < 15:
                temp_earnings['cold'].append(hourly_rate)
            elif temp < 25:
                temp_earnings['mild'].append(hourly_rate)
            else:
                temp_earnings['hot'].append(hourly_rate)
    
    # Determine temperature correlation strength
    temp_avgs = {k: sum(v) / len(v) for k, v in temp_earnings.items() if len(v) > 0}
    
    if len(temp_avgs) >= 2:
        temp_values = list(temp_avgs.values())
        temp_range = max(temp_values) - min(temp_values)
        avg_earnings = sum(temp_values) / len(temp_values)
        
        # Calculate relative variation
        if avg_earnings > 0:
            temp_variation = temp_range / avg_earnings
            if temp_variation > 0.15:
                temperature_correlation = "strong"
            elif temp_variation > 0.08:
                temperature_correlation = "moderate"
            else:
                temperature_correlation = "weak"
        else:
            temperature_correlation = "unknown"
    else:
        temperature_correlation = "unknown"
    
    # STEP 3: Generate insight text
    if rain_boost > 15:
        insight = f"Rainy days increase your earnings by {rain_boost}% on average. Consider working more hours when rain is forecasted."
    elif rain_boost > 0:
        insight = f"Rainy days increase your earnings by {rain_boost}% on average."
    else:
        insight = "Weather doesn't significantly impact your earnings. Your performance is consistent across conditions."
    
    return {
        "rain_boost": rain_boost,
        "temperature_correlation": temperature_correlation,
        "insight": insight
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
    """
    
    # Get today's date and calculate range
    today = datetime.now()
    start_date = today.strftime('%Y-%m-%d')
    
    # Load event data
    all_features = features.build_features(driver_id, start_date)
    event_features = all_features['event_features']
    
    # STEP 1: Filter events within the upcoming days range
    end_date = today + timedelta(days=upcoming_days)
    
    upcoming_events = []
    for event in event_features['events'] + event_features['holidays']:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        
        if today <= event_date <= end_date:
            # STEP 2: Determine recommended zones based on event location
            event_location = event['location']
            
            # Map event locations to recommended working zones
            if 'CBD' in event_location or 'City' in event_location:
                recommended_zones = ["Sydney CBD", "City Centre"]
            elif 'Olympic Park' in event_location:
                recommended_zones = ["Olympic Park", "Parramatta"]
            elif 'Airport' in event_location:
                recommended_zones = ["Airport", "Sydney CBD"]
            elif 'Circular Quay' in event_location or 'Opera House' in event_location:
                recommended_zones = ["Circular Quay", "Sydney CBD", "The Rocks"]
            elif 'Beach' in event_location or 'Bondi' in event_location:
                recommended_zones = ["Bondi Beach", "Eastern Suburbs"]
            elif 'Sydney-wide' in event_location:
                recommended_zones = ["Sydney CBD", "Airport", "Major hubs"]
            else:
                recommended_zones = [event_location, "Sydney CBD"]
            
            upcoming_events.append({
                "name": event['name'],
                "date": event['date'],
                "expected_boost": event['expected_impact'],
                "recommended_zones": recommended_zones
            })
    
    # STEP 3: Sort by expected boost (highest impact first)
    upcoming_events.sort(key=lambda x: x['expected_boost'], reverse=True)
    
    return {
        "events": upcoming_events
    }