"""
Feature Builder - Prepares and aggregates features from CSV data sources

This is the data loader layer that sits between raw CSV files and the engines 
(Extract, Transform, Load) pipeline

Should Handles all file I/O and data parsing
Provides clean, structured data to forecast, insights, steadiness, and recommendation engines
The other engines should NOT read CSVs directly, (they instead utilize these functions)
"""

import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

#Directory where all CSV files are stored created by data_gen.py
DATA_DIR="data" 

def load_driver_data(driver_id: str):
    """
    Loads driver's historical data from CSV
    
    Arg: driver_id: Unique identifier (e.g., "driver1", "driver2")
    
    Return: dict with driver profile and aggregate stats
    """
    filename=f"{DATA_DIR}/{driver_id}.csv"
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Driver data for: {filename} was not found :(")
    
    trips=[]
    total_earnings=0
    total_hours=0
    total_rating=0
    earliest_date=None 
    
    with open(filename, 'r') as f: #don't need to close file
        reader=csv.DictReader(f)
        for row in reader:
            #Parse and accumulate data
            earnings=float(row['earnings'])
            hours=float(row['hours'])
            rating=float(row['rating'])
            date=datetime.strptime(row['date'], '%Y-%m-%d')
            
            total_earnings+=earnings
            total_hours+=hours
            total_rating+=rating
            
            if earliest_date is None or date < earliest_date:
                earliest_date=date
            
            trips.append(row)
    
    num_trips=len(trips)
    avg_rating=total_rating/num_trips if num_trips > 0 else 0
    
    return {
        "driver_id": driver_id,
        "total_trips": num_trips,
        "total_earnings": round(total_earnings, 2),
        "total_hours": round(total_hours, 2),
        "avg_rating": round(avg_rating, 2),
        "avg_hourly_rate": round(total_earnings / total_hours, 2) if total_hours > 0 else 0,
        "member_since": earliest_date.strftime('%Y-%m-%d') if earliest_date else None,
        "raw_trips": trips  #Include raw data for engines to analyze
    }

def load_weather_data(location: str, date_range: dict):
    """
    Loads weather data for location and date range
    
    Args:
        location: City/area 
        date_range: Dict with start date and number of days
                    e.g., {"start": "2026-10-20", "days": 14}
    
    Returns: dict with structured array of daily weather conditions
    """
    filename=f"{DATA_DIR}/weather.csv"
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Weather data not for {filename} not found :(")
    
    start_date=datetime.strptime(date_range['start'], '%Y-%m-%d')
    end_date=start_date + timedelta(days=date_range['days'])
    
    weather_data = []
    
    with open(filename, 'r') as f:
        reader=csv.DictReader(f)
        for row in reader:
            row_date=datetime.strptime(row['date'], '%Y-%m-%d')
            
            #Filter by location and date range
            if row['location'].strip() == location and start_date <= row_date < end_date:
                weather_data.append({
                    "date": row['date'],
                    "condition": row['condition'].strip(),
                    "temp": int(row['temp']),
                    "humidity": int(row['humidity'])
                })
    
    return {
        "location": location,
        "data": sorted(weather_data, key=lambda x: x['date'])
    }

def load_event_data(location: str, date_range: dict):
    """
    Loads holiday and event data
    
    Args:
        location: City/area 
        date_range: Dict with start date and number of days
    
    Returns: dict with events and holidays
    """
    filename=f"{DATA_DIR}/events.csv"
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Event data for {filename} not found :(")
    
    start_date=datetime.strptime(date_range['start'], '%Y-%m-%d')
    end_date=start_date + timedelta(days=date_range['days'])
    
    events=[]
    holidays=[]
    
    with open(filename, 'r') as f:
        reader=csv.DictReader(f)
        for row in reader:
            event_date=datetime.strptime(row['date'], '%Y-%m-%d')
            
            #Filter by date range
            if start_date <= event_date < end_date:
                event_obj={
                    "name": row['name'].strip(),
                    "date": row['date'],
                    "type": row['type'].strip(),
                    "location": row['location'].strip(),
                    "expected_impact": int(row['expected_impact'])
                }
                
                if row['type'].strip() == 'holiday':
                    holidays.append(event_obj)
                else:
                    events.append(event_obj)
    
    return {
        "events": sorted(events, key=lambda x: x['date']),
        "holidays": sorted(holidays, key=lambda x: x['date'])
    }

def get_user_preferences(driver_id: str):
    """
    Returns user's preferences from CSV
    
    Args:
        driver_id: Unique identifier for the driver
    
    Returns:dict with user preferences and goals
    """
    filename=f"{DATA_DIR}/preferences.csv"
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Preferences data from {filename} nor found :(")
    
    with open(filename, 'r') as f:
        reader=csv.DictReader(f)
        for row in reader:
            if row['driver_id'].strip() == driver_id:
                #Parse comma-separated zones
                preferred_zones=[z.strip() for z in row['preferred_zones'].split(',')]
                
                return {
                    "driver_id": driver_id,
                    "income_floor": int(row['income_floor']),
                    "preferred_zones": preferred_zones,
                    "preferred_hours": row['preferred_hours'].strip(),
                    "weekly_goal": int(row['weekly_goal']),
                    "monthly_goal": int(row['monthly_goal'])
                }
    
    # Return default if driver not found
    return {
        "driver_id": driver_id,
        "income_floor": 800,
        "preferred_zones": ["Sydney CBD", "Airport"],
        "preferred_hours": "7-9am,5-8pm",
        "weekly_goal": 4800,
        "monthly_goal": 19200
    }

def get_weekly_aggregates(driver_id: str, weeks: int = 12):
    """
    Aggregates driver data by week
    
    Args:
        driver_id: Unique identifier for the driver
        weeks: Number of recent weeks to analyze
    
    Returns: list of dicts with weekly aggregates
    """
    driver_data=load_driver_data(driver_id)
    trips=driver_data['raw_trips']
    
    #Group trips by week
    weekly_data=defaultdict(lambda: {
        'earnings': 0,
        'hours': 0,
        'trips': 0,
        'ratings': []
    })
    
    for trip in trips:
        date=datetime.strptime(trip['date'], '%Y-%m-%d')
        #Get week start (Monday)
        week_start=date - timedelta(days=date.weekday())
        week_key=week_start.strftime('%Y-%m-%d')
        
        weekly_data[week_key]['earnings'] += float(trip['earnings'])
        weekly_data[week_key]['hours'] += float(trip['hours'])
        weekly_data[week_key]['trips'] += 1
        weekly_data[week_key]['ratings'].append(float(trip['rating']))
    
    #Convert to sorted list and take most recent weeks
    weekly_list=[]
    for week_start, data in sorted(weekly_data.items(), reverse=True)[:weeks]:
        weekly_list.append({
            'week_start': week_start,
            'earnings': round(data['earnings'], 2),
            'hours': round(data['hours'], 2),
            'trips': data['trips'],
            'avg_rating': round(sum(data['ratings']) / len(data['ratings']), 2)
        })
    
    return list(reversed(weekly_list))  #Return in chronological order

def get_daily_aggregates(driver_id: str, days: int = 90):
    """
    Aggregates driver data by day
    
    Args:
        driver_id: Unique identifier for the driver
        days: Number of recent days to analyze
    
    Returns: list of dicts with daily aggregates
    """
    driver_data=load_driver_data(driver_id)
    trips=driver_data['raw_trips']
    
    #Group trips by day
    daily_data=defaultdict(lambda: {
        'earnings': 0,
        'hours': 0,
        'trips': 0,
        'ratings': [],
        'zones': []
    })
    
    for trip in trips:
        date=trip['date']
        daily_data[date]['earnings'] += float(trip['earnings'])
        daily_data[date]['hours'] += float(trip['hours'])
        daily_data[date]['trips'] += 1
        daily_data[date]['ratings'].append(float(trip['rating']))
        daily_data[date]['zones'].append(trip['zone'])
        daily_data[date]['day_of_week'] = trip['day_of_week']
    
    #Convert to sorted list and take most recent days
    daily_list=[]
    for date, data in sorted(daily_data.items(), reverse=True)[:days]:
        daily_list.append({
            'date': date,
            'earnings': round(data['earnings'], 2),
            'hours': round(data['hours'], 2),
            'trips': data['trips'],
            'avg_rating': round(sum(data['ratings']) / len(data['ratings']), 2),
            'zones': data['zones'],
            'day_of_week': data['day_of_week']
        })
    
    return list(reversed(daily_list))  #Return in chronological order

def build_features(driver_id: str, date: str):
    """
    Aggregates all data sources into feature set for engines
    
    Args:
        driver_id: Unique identifier for the driver
        date: Starting date for time-based data (e.g., "2026-10-20")
    
    Returns: dict containing all data sources in structured format
    """
    return {
        "driver_features": load_driver_data(driver_id),
        "weather_features": load_weather_data("Sydney", {"start": date, "days": 14}),
        "event_features": load_event_data("Sydney", {"start": date, "days": 14}),
        "preferences": get_user_preferences(driver_id),
        "weekly_aggregates": get_weekly_aggregates(driver_id, weeks=12),
        "daily_aggregates": get_daily_aggregates(driver_id, days=90)
    }