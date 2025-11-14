"""
Recommendation Engine - Combines all engines with user preferences to generate actionable recommendations

This is the "smart assistant" that pulls everything together:
- Takes forecast predictions (Forecast Engine)
- Considers stability patterns (Steadiness Engine)
- Uses insights about what works (Insights Engine)
- Factors in user's goals and preferences
- Outputs: "Here's what you should do this week"

This is what makes Steady actionable, not just informational
"""

import features as features
import forecast as forecast
import insights as insights
from datetime import datetime, timedelta
from collections import defaultdict

def get_weekly_recommendations(driver_id: str, week: str):
    """
    Returns personalized recommendations for the week
    
    The main value proposition: "Based on everything we know, 
    here are the top 3 things you should do this week to hit your goals"
    
    Args:
        driver_id: Unique identifier for the driver
        week: ISO date for the week (e.g., "2026-10-20")
    
    Returns:
        dict containing:
        - week: The target week
        - top_recommendations: Array of 3-5 prioritized actions
    """
    
    # STEP 1: Load all necessary data
    all_features = features.build_features(driver_id, week)
    preferences = all_features['preferences']
    weather_features = all_features['weather_features']
    event_features = all_features['event_features']
    
    # Get forecast for the week
    weekly_forecast = forecast.get_weekly_forecast(driver_id, week)
    
    # Get insights
    peak_hours = insights.get_peak_hours_analysis(driver_id)
    weather_impact = insights.get_weather_impact_analysis(driver_id)
    event_opportunities = insights.get_event_opportunities(driver_id, upcoming_days=14)
    
    # Get current progress toward goal
    goal_progress = get_goal_progress(driver_id)
    
    # STEP 2: Generate recommendations based on multiple factors
    recommendations = []
    
    # Convert week string to datetime for date calculations
    week_start = datetime.strptime(week, '%Y-%m-%d')
    week_end = week_start + timedelta(days=7)
    
    # RECOMMENDATION 1: Check for high-impact events
    for event in event_opportunities['events']:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        
        # If event is this week
        if week_start <= event_date < week_end:
            day_name = event_date.strftime('%A')
            
            # Determine time recommendation based on event type
            if 'Concert' in event['name'] or 'Festival' in event['name']:
                time_rec = "6-11pm"
            elif 'Marathon' in event['name'] or 'Sports' in event['name']:
                time_rec = "morning and evening"
            else:
                time_rec = "evening hours"
            
            # Calculate expected impact in dollars
            weekly_avg = all_features['weekly_aggregates'][-1]['earnings'] if all_features['weekly_aggregates'] else 1000
            expected_impact = round((event['expected_boost'] / 100) * (weekly_avg / 7))
            
            recommendations.append({
                "priority": "high",
                "type": "event",
                "title": f"Focus on {day_name} {time_rec}",
                "description": f"{event['name']} - expect {event['expected_boost']}% boost in {', '.join(event['recommended_zones'][:2])} area",
                "expected_impact": expected_impact
            })
            break  # Only recommend the highest-impact event
    
    # RECOMMENDATION 2: Check for rainy days (weather opportunities)
    rainy_days = []
    for day_weather in weather_features['data']:
        day_date = datetime.strptime(day_weather['date'], '%Y-%m-%d')
        if week_start <= day_date < week_end and day_weather['condition'] in ['rain', 'storm']:
            rainy_days.append(day_date)
    
    if rainy_days and weather_impact['rain_boost'] > 10:
        # Find the first rainy day
        first_rainy = min(rainy_days)
        day_name = first_rainy.strftime('%A')
        
        # Calculate expected boost in dollars
        weekly_avg = all_features['weekly_aggregates'][-1]['earnings'] if all_features['weekly_aggregates'] else 1000
        daily_avg = weekly_avg / 7
        expected_impact = round(daily_avg * (weather_impact['rain_boost'] / 100))
        
        recommendations.append({
            "priority": "medium",
            "type": "weather",
            "title": f"Rain expected on {day_name}",
            "description": f"Work morning and evening peaks for {weather_impact['rain_boost']}% earnings boost",
            "expected_impact": expected_impact
        })
    
    # RECOMMENDATION 3: Goal-based recommendation
    if not goal_progress['on_track']:
        # Driver is behind on their goal
        gap = goal_progress['remaining']
        days_left = goal_progress['days_left']
        
        # Suggest best performing time/zone to catch up
        if peak_hours['best_hours']:
            best_hour = peak_hours['best_hours'][0]
            hours_needed = round(gap / best_hour['avg_earnings'])
            
            recommendations.append({
                "priority": "high",
                "type": "goal",
                "title": f"Add {hours_needed} hours to reach your goal",
                "description": f"Work {best_hour['hour']} over the next {days_left} days to close the ${gap} gap",
                "expected_impact": gap
            })
        else:
            recommendations.append({
                "priority": "high",
                "type": "goal",
                "title": f"${gap} from your weekly goal",
                "description": f"Focus on your best-performing hours over the next {days_left} days",
                "expected_impact": gap
            })
    elif goal_progress['progress_percent'] > 90:
        # Driver is ahead and close to goal
        recommendations.append({
            "priority": "low",
            "type": "goal",
            "title": "You're ahead of schedule!",
            "description": f"Only ${goal_progress['remaining']} to go - maintain your current pace",
            "expected_impact": goal_progress['remaining']
        })
    
    # RECOMMENDATION 4: Best zone recommendation (if user working in suboptimal zones)
    if peak_hours['best_zones']:
        best_zone = peak_hours['best_zones'][0]
        preferred_zones = preferences['preferred_zones']
        
        # If best zone is not in their preferred zones, suggest it
        if best_zone['zone'] not in preferred_zones:
            recommendations.append({
                "priority": "medium",
                "type": "zone",
                "title": f"Try working in {best_zone['zone']}",
                "description": f"Your earnings average ${best_zone['avg_hourly']}/hour here - {round((best_zone['avg_hourly'] - 40) / 40 * 100)}% above your baseline",
                "expected_impact": round((best_zone['avg_hourly'] - 40) * 8)  # Assume 8 hour shift difference
            })
    
    # RECOMMENDATION 5: Peak hours reminder (if they have good data)
    if peak_hours['best_hours'] and len(recommendations) < 3:
        best_hour = peak_hours['best_hours'][0]
        recommendations.append({
            "priority": "medium",
            "type": "timing",
            "title": f"Maximize {best_hour['hour']} shifts",
            "description": f"Your best performing time with ${best_hour['avg_earnings']}/hour and {best_hour['consistency']} consistency",
            "expected_impact": round((best_hour['avg_earnings'] - 40) * 2)  # 2 hour shift boost
        })
    
    # STEP 3: Sort recommendations by priority and limit to top 3-5
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: (priority_order[x['priority']], -x['expected_impact']))
    
    # Take top 5 recommendations
    top_recommendations = recommendations[:5]
    
    return {
        "week": week,
        "top_recommendations": top_recommendations
    }

def get_daily_recommendations(driver_id: str, date: str):
    """
    Returns recommendations for a specific day
    
    More granular than weekly - answers "What should I do TODAY?"
    Shows best time blocks and zones for that specific day
    
    Args:
        driver_id: Unique identifier for the driver
        date: ISO date string (e.g., "2026-10-20")
    
    Returns:
        dict containing:
        - date: The target date
        - recommendations: Array of time-block suggestions
    """
    
    # STEP 1: Load necessary data
    all_features = features.build_features(driver_id, date)
    weather_features = all_features['weather_features']
    event_features = all_features['event_features']
    
    # Get daily forecast
    daily_forecast = forecast.get_daily_forecast(driver_id, date)
    
    # Get insights
    peak_hours = insights.get_peak_hours_analysis(driver_id)
    
    # STEP 2: Check weather for today
    today_weather = next((w for w in weather_features['data'] if w['date'] == date), None)
    weather_multiplier = 1.0
    weather_note = ""
    
    if today_weather:
        if today_weather['condition'] in ['rain', 'storm']:
            weather_multiplier = 1.25
            weather_note = "Rainy weather boost"
        elif today_weather['condition'] == 'sunny':
            weather_note = "Clear weather"
    
    # STEP 3: Check for events today
    events_today = [e for e in event_features['events'] + event_features['holidays'] 
                    if e['date'] == date]
    
    event_zones = []
    event_boost = 1.0
    if events_today:
        event = events_today[0]  # Take the first/biggest event
        event_zones = event['recommended_zones']
        event_boost = 1.0 + (event['expected_impact'] / 100)
    
    # STEP 4: Generate time-block recommendations
    recommendations = []
    
    # Get day of week to determine patterns
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    day_of_week = date_obj.strftime('%A')
    is_weekend = day_of_week in ['Saturday', 'Sunday']
    
    # Use peak hours analysis + daily forecast
    if peak_hours['best_hours']:
        for hour_block in peak_hours['best_hours'][:2]:  # Top 2 time blocks
            # Find corresponding zone
            zone = peak_hours['best_zones'][0]['zone'] if peak_hours['best_zones'] else "Sydney CBD"
            
            # Override zone if there's an event
            if event_zones:
                zone = event_zones[0]
            
            # Calculate expected earnings with weather and event multipliers
            base_earnings = hour_block['avg_earnings']
            expected_earnings = round(base_earnings * weather_multiplier * event_boost)
            
            # Build reason string
            reasons = []
            if hour_block['consistency'] == 'high':
                reasons.append("Consistent high performance")
            if weather_note:
                reasons.append(weather_note)
            if events_today:
                reasons.append(f"{events_today[0]['name']}")
            
            reason = " + ".join(reasons) if reasons else "Peak earning hours"
            
            recommendations.append({
                "time": hour_block['hour'],
                "zone": zone,
                "expected_earnings": expected_earnings,
                "reason": reason
            })
    else:
        # Fallback recommendations based on day type
        if is_weekend:
            recommendations = [
                {
                    "time": "10am-2pm",
                    "zone": "Bondi Beach",
                    "expected_earnings": round(45 * weather_multiplier * event_boost),
                    "reason": "Weekend lunch and tourist activity"
                },
                {
                    "time": "7pm-11pm",
                    "zone": "Sydney CBD",
                    "expected_earnings": round(52 * weather_multiplier * event_boost),
                    "reason": "Weekend evening entertainment"
                }
            ]
        else:
            recommendations = [
                {
                    "time": "7-9am",
                    "zone": "Sydney CBD",
                    "expected_earnings": round(48 * weather_multiplier * event_boost),
                    "reason": "Morning commute rush"
                },
                {
                    "time": "5-8pm",
                    "zone": "Sydney CBD",
                    "expected_earnings": round(52 * weather_multiplier * event_boost),
                    "reason": "Evening rush hour"
                }
            ]
    
    return {
        "date": date,
        "recommendations": recommendations
    }

def get_goal_progress(driver_id: str):
    """
    Returns progress towards user's income goal
    
    Powers the "Weekly Goal" progress bar in Image 1
    Shows "$200 of $400" and "87% complete with 2 days left"
    
    Args:
        driver_id: Unique identifier for the driver
    
    Returns:
        dict containing:
        - goal_amount: User's target (set in preferences)
        - current_amount: What they've earned so far this period
        - remaining: Gap to goal
        - progress_percent: Visual for progress bar
        - days_left: Time remaining in period
        - on_track: Boolean - are they on pace?
        - recommendation: Encouraging message with next steps
    """
    
    # STEP 1: Load user preferences to get goal
    preferences = features.get_user_preferences(driver_id)
    weekly_goal = preferences['weekly_goal']
    
    # STEP 2: Calculate current week's earnings
    # Get all daily data and filter to current week
    daily_data = features.get_daily_aggregates(driver_id, days=90)
    
    # Determine current week boundaries (Monday to Sunday)
    today = datetime.now()
    days_since_monday = today.weekday()  # Monday = 0, Sunday = 6
    week_start = today - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=7)
    
    # Sum earnings for current week
    current_amount = 0
    for day in daily_data:
        day_date = datetime.strptime(day['date'], '%Y-%m-%d')
        if week_start <= day_date < today:
            current_amount += day['earnings']
    
    current_amount = round(current_amount, 2)
    
    # STEP 3: Calculate remaining amount and days
    remaining = round(weekly_goal - current_amount, 2)
    days_left = 6 - days_since_monday  # Days left until Sunday
    
    if days_left < 0:
        days_left = 0
    
    # STEP 4: Calculate progress percentage
    progress_percent = round((current_amount / weekly_goal) * 100) if weekly_goal > 0 else 0
    if progress_percent > 100:
        progress_percent = 100
    
    # STEP 5: Determine if on track
    # Calculate required daily rate vs actual daily rate
    days_worked = days_since_monday if days_since_monday > 0 else 1
    actual_daily_rate = current_amount / days_worked
    required_daily_rate = weekly_goal / 7
    
    on_track = actual_daily_rate >= (required_daily_rate * 0.9)  # Within 10% is considered "on track"
    
    # STEP 6: Generate personalized recommendation message
    if progress_percent >= 100:
        recommendation = f"Goal achieved! You've earned ${current_amount} this week."
    elif progress_percent >= 90:
        recommendation = f"Almost there! Just ${remaining} more to reach your goal."
    elif on_track:
        recommendation = f"You're on track! {progress_percent}% complete with {days_left} days left."
    else:
        # Behind pace - calculate catch-up needed
        if days_left > 0:
            daily_catch_up = round(remaining / days_left, 2)
            recommendation = f"Need ${remaining} more. Focus on earning ${daily_catch_up}/day to catch up."
        else:
            recommendation = f"Week ending. You earned ${current_amount} of your ${weekly_goal} goal."
    
    return {
        "goal_amount": weekly_goal,
        "current_amount": current_amount,
        "remaining": remaining if remaining > 0 else 0,
        "progress_percent": progress_percent,
        "days_left": days_left,
        "on_track": on_track,
        "recommendation": recommendation
    }

def get_optimal_schedule(driver_id: str, target_income: int, available_hours: int):
    """
    Suggests optimal schedule to reach target income
    
    The "planner" feature: User says "I want to make $930 this week 
    working 40 hours" and this tells them exactly when/how to work
    
    Args:
        driver_id: Unique identifier for the driver
        target_income: How much they want to earn (e.g., 930)
        available_hours: How many hours they can work (e.g., 40)
    
    Returns:
        dict containing:
        - target: Their income goal
        - schedule: Day-by-day plan with hours and expected earnings
        - total_expected: Projected total if they follow the plan
        - confidence: How reliable is this schedule ("high", "medium", "low")
    """
    
    # STEP 1: Load necessary data
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_str = week_start.strftime('%Y-%m-%d')
    
    all_features = features.build_features(driver_id, week_str)
    weekly_data = all_features['weekly_aggregates']
    
    # Get insights for best hours and weather
    peak_hours = insights.get_peak_hours_analysis(driver_id)
    weather_impact = insights.get_weather_impact_analysis(driver_id)
    event_opportunities = insights.get_event_opportunities(driver_id, upcoming_days=7)
    
    # STEP 2: Calculate average hourly rate
    if weekly_data:
        recent_weeks = weekly_data[-4:] if len(weekly_data) >= 4 else weekly_data
        total_earnings = sum(w['earnings'] for w in recent_weeks)
        total_hours = sum(w['hours'] for w in recent_weeks)
        base_hourly_rate = total_earnings / total_hours if total_hours > 0 else 40
    else:
        base_hourly_rate = 40
    
    # STEP 3: Build day-by-day schedule optimized for earnings
    schedule = []
    total_expected = 0
    hours_allocated = 0
    
    # Create 7-day schedule (Monday to Sunday)
    for day_offset in range(7):
        day_date = week_start + timedelta(days=day_offset)
        day_name = day_date.strftime('%A')
        date_str = day_date.strftime('%Y-%m-%d')
        
        # Skip if we've allocated all available hours
        if hours_allocated >= available_hours:
            continue
        
        # Determine hours for this day (distribute available hours across week)
        is_weekend = day_name in ['Saturday', 'Sunday']
        
        # Prioritize weekend and event days
        daily_forecast = forecast.get_daily_forecast(driver_id, date_str)
        
        # Check for events on this day
        events_today = [e for e in event_opportunities['events'] if e['date'] == date_str]
        has_event = len(events_today) > 0
        
        # Allocate hours based on opportunity
        remaining_hours = available_hours - hours_allocated
        if has_event:
            # Allocate more hours on event days
            day_hours = min(10, remaining_hours)
        elif is_weekend:
            # More hours on weekends
            day_hours = min(8, remaining_hours)
        else:
            # Moderate hours on weekdays
            day_hours = min(6, remaining_hours)
        
        if day_hours <= 0:
            continue
        
        # STEP 4: Calculate expected earnings with boosts
        hourly_rate = base_hourly_rate
        
        # Apply weather boost if applicable
        if weather_impact['rain_boost'] > 10:
            # Assume some days will be rainy (simplified)
            if day_offset % 3 == 0:  # Every 3rd day might be rainy
                hourly_rate *= (1 + weather_impact['rain_boost'] / 100)
        
        # Apply event boost
        if has_event:
            event = events_today[0]
            hourly_rate *= (1 + event['expected_boost'] / 100)
        
        # Weekend boost
        if is_weekend:
            hourly_rate *= 1.15
        
        # Calculate expected for this day
        day_expected = round(hourly_rate * day_hours)
        
        # STEP 5: Determine optimal hours for this day
        if peak_hours['best_hours']:
            if is_weekend:
                time_blocks = "10am-2pm, 8pm-12am"
            else:
                time_blocks = "7-9am, 5-8pm"
        else:
            if is_weekend:
                time_blocks = "10am-6pm"
            else:
                time_blocks = "7-9am, 5-8pm"
        
        schedule.append({
            "day": day_name,
            "hours": time_blocks,
            "expected": day_expected
        })
        
        total_expected += day_expected
        hours_allocated += day_hours
        
        # Stop if we've reached target income
        if total_expected >= target_income:
            break
    
    # STEP 6: Determine confidence level
    # Based on historical consistency
    if weekly_data and len(weekly_data) >= 4:
        earnings_list = [w['earnings'] for w in weekly_data[-4:]]
        avg = sum(earnings_list) / len(earnings_list)
        std_dev = (sum((x - avg) ** 2 for x in earnings_list) / len(earnings_list)) ** 0.5
        cv = std_dev / avg if avg > 0 else 0
        
        if cv < 0.10:
            confidence = "high"
        elif cv < 0.20:
            confidence = "medium"
        else:
            confidence = "low"
    else:
        confidence = "medium"
    
    return {
        "target": target_income,
        "schedule": schedule,
        "total_expected": round(total_expected, 2),
        "confidence": confidence
    }