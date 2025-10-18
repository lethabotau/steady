"""
Data Generator - Creates dummy CSV files for testing Steady backend

Run this script to generate all the CSV files needed for Phase 1:
- Driver historical data (driverX.csv)
- Weather data (weather.csv)
- Events data (events.csv)
- User preferences (preferences.csv)

Usage:
    python datagen.py

This will create a 'data/' folder with all CSV files
"""

import csv
import random
from datetime import datetime, timedelta
import os

# Configuration
NUM_DRIVERS = 3  # Generate data for 3 drivers
WEEKS_OF_HISTORY = 16  # 4 months of historical data
DATA_DIR = "data"

# Sydney zones for realistic location data
SYDNEY_ZONES = [
    "Sydney CBD", "Bondi Beach", "Airport", "Parramatta", 
    "North Sydney", "Manly", "Newtown", "Olympic Park"
]

# Weather conditions with probabilities (Sydney climate)
WEATHER_CONDITIONS = [
    ("sunny", 0.5),  # 50% chance
    ("cloudy", 0.3),  # 30% chance
    ("rain", 0.15),   # 15% chance
    ("storm", 0.05)   # 5% chance
]

def create_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"✓ Created {DATA_DIR}/ directory")

def weighted_choice(choices):
    """Select item based on weighted probabilities"""
    items, weights = zip(*choices)
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for item, weight in zip(items, weights):
        cumulative += weight
        if r <= cumulative:
            return item
    return items[-1]

def generate_driver_data(driver_id, num_weeks):
    """
    Generate realistic driver earnings CSV
    
    Patterns included:
    - Weekday vs weekend variations (weekends earn more)
    - Weather impact (rain = +25% earnings)
    - Time-based trends (gradual improvement over time)
    - Random variance for realism
    - Zone-specific earnings
    """
    filename = f"{DATA_DIR}/driver{driver_id}.csv"
    
    # Driver-specific baseline (some drivers earn more than others)
    base_earnings_per_hour = random.randint(35, 55)
    
    # Starting date (16 weeks ago from today)
    start_date = datetime.now() - timedelta(weeks=num_weeks)
    
    rows = []
    trip_id = 1
    
    # Generate data for each week
    for week in range(num_weeks):
        for day in range(7):  # 7 days per week
            current_date = start_date + timedelta(weeks=week, days=day)
            day_of_week = current_date.strftime("%A")
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Skip some days randomly (drivers don't work every day)
            if random.random() < 0.2:  # 20% chance to skip a day
                continue
            
            # Hours worked varies by day
            # Weekends: 6-10 hours, Weekdays: 4-8 hours
            is_weekend = day_of_week in ["Saturday", "Sunday"]
            if is_weekend:
                hours = round(random.uniform(6, 10), 1)
            else:
                hours = round(random.uniform(4, 8), 1)
            
            # Earnings calculation with realistic patterns
            earnings_per_hour = base_earnings_per_hour
            
            # Weekend boost (15% more)
            if is_weekend:
                earnings_per_hour *= 1.15
            
            # Weather boost (loaded from weather data later, simulated here)
            # 15% chance of rain day
            if random.random() < 0.15:
                earnings_per_hour *= 1.25  # Rain = 25% boost
            
            # Gradual improvement over time (driver getting better)
            time_multiplier = 1 + (week * 0.01)  # 1% improvement per week
            earnings_per_hour *= time_multiplier
            
            # Add random variance (±15%)
            earnings_per_hour *= random.uniform(0.85, 1.15)
            
            # Calculate total earnings for the day
            total_earnings = round(earnings_per_hour * hours, 2)
            
            # Number of trips (roughly 1 trip per 25 minutes)
            num_trips = int(hours * 2.4)
            
            # Generate individual trips
            for _ in range(num_trips):
                trip_earnings = round(total_earnings / num_trips, 2)
                zone = random.choice(SYDNEY_ZONES)
                rating = round(random.uniform(4.5, 5.0), 1)
                
                rows.append({
                    "date": date_str,
                    "trip_id": f"T{trip_id:04d}",
                    "earnings": trip_earnings,
                    "hours": round(hours / num_trips, 2),
                    "rating": rating,
                    "zone": zone,
                    "day_of_week": day_of_week
                })
                trip_id += 1
    
    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "trip_id", "earnings", "hours", "rating", "zone", "day_of_week"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Generated {filename} with {len(rows)} trips")

def generate_weather_data(num_weeks):
    """
    Generate weather CSV for Sydney
    
    Patterns:
    - Realistic Sydney weather distribution
    - Seasonal variations (warmer in summer, cooler in winter)
    - Temperature ranges appropriate for Sydney
    """
    filename = f"{DATA_DIR}/weather.csv"
    
    start_date = datetime.now() - timedelta(weeks=num_weeks)
    rows = []
    
    # Generate weather for each day
    for day in range(num_weeks * 7):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Select weather condition based on probabilities
        condition = weighted_choice(WEATHER_CONDITIONS)
        
        # Temperature based on condition and season
        month = current_date.month
        # Sydney temps: Summer (Dec-Feb) 18-27°C, Winter (Jun-Aug) 8-17°C
        if month in [12, 1, 2]:  # Summer
            base_temp = random.randint(20, 28)
        elif month in [6, 7, 8]:  # Winter
            base_temp = random.randint(10, 18)
        else:  # Spring/Autumn
            base_temp = random.randint(15, 23)
        
        # Adjust temp based on condition
        if condition == "rain" or condition == "storm":
            temp = base_temp - random.randint(2, 5)
        else:
            temp = base_temp
        
        # Humidity (higher when rainy)
        if condition in ["rain", "storm"]:
            humidity = random.randint(75, 95)
        else:
            humidity = random.randint(50, 75)
        
        rows.append({
            "date": date_str,
            "location": "Sydney",
            "condition": condition,
            "temp": temp,
            "humidity": humidity
        })
    
    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "location", "condition", "temp", "humidity"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Generated {filename} with {len(rows)} days of weather")

def generate_events_data():
    """
    Generate upcoming events and holidays CSV
    
    Includes:
    - Sports events (AFL, NRL, Cricket)
    - Entertainment (concerts, festivals)
    - Public holidays
    """
    filename = f"{DATA_DIR}/events.csv"
    
    # Future events (next 60 days)
    today = datetime.now()
    
    events = [
        # Sports events
        {"date": (today + timedelta(days=7)).strftime("%Y-%m-%d"), "name": "Sydney Marathon", "type": "sports", "location": "City Centre", "expected_impact": 35},
        {"date": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "name": "NRL Final", "type": "sports", "location": "Olympic Park", "expected_impact": 40},
        {"date": (today + timedelta(days=21)).strftime("%Y-%m-%d"), "name": "Cricket Match", "type": "sports", "location": "SCG", "expected_impact": 30},
        
        # Entertainment
        {"date": (today + timedelta(days=12)).strftime("%Y-%m-%d"), "name": "Concert - Accor Stadium", "type": "entertainment", "location": "Olympic Park", "expected_impact": 28},
        {"date": (today + timedelta(days=25)).strftime("%Y-%m-%d"), "name": "Vivid Festival Opening", "type": "entertainment", "location": "Circular Quay", "expected_impact": 45},
        {"date": (today + timedelta(days=35)).strftime("%Y-%m-%d"), "name": "Opera House Concert", "type": "entertainment", "location": "Circular Quay", "expected_impact": 25},
        
        # Holidays
        {"date": (today + timedelta(days=45)).strftime("%Y-%m-%d"), "name": "Public Holiday", "type": "holiday", "location": "Sydney-wide", "expected_impact": 20},
    ]
    
    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "name", "type", "location", "expected_impact"])
        writer.writeheader()
        writer.writerows(events)
    
    print(f"✓ Generated {filename} with {len(events)} events")

def generate_preferences_data(num_drivers):
    """
    Generate user preferences CSV
    
    Each driver has:
    - Income floor (minimum weekly target)
    - Preferred zones (where they like to work)
    - Preferred hours (when they like to work)
    - Weekly and monthly goals
    """
    filename = f"{DATA_DIR}/preferences.csv"
    
    rows = []
    
    for driver_id in range(1, num_drivers + 1):
        # Random but realistic preferences
        income_floor = random.choice([700, 800, 900, 1000])
        weekly_goal = random.choice([4000, 4500, 5000, 5500])
        monthly_goal = weekly_goal * 4
        
        # Random 2-3 preferred zones
        num_zones = random.randint(2, 3)
        preferred_zones = ",".join(random.sample(SYDNEY_ZONES, num_zones))
        
        # Preferred hours (morning/evening/full day)
        hour_preferences = random.choice([
            "7-9am,5-8pm",  # Morning and evening peaks
            "6-10am,4-9pm",  # Extended peaks
            "10am-4pm",      # Day shift
            "6pm-12am"       # Evening/night shift
        ])
        
        rows.append({
            "driver_id": f"driver{driver_id}",
            "income_floor": income_floor,
            "preferred_zones": preferred_zones,
            "preferred_hours": hour_preferences,
            "weekly_goal": weekly_goal,
            "monthly_goal": monthly_goal
        })
    
    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["driver_id", "income_floor", "preferred_zones", "preferred_hours", "weekly_goal", "monthly_goal"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Generated {filename} with {len(rows)} driver preferences")

def main():
    """Generate all CSV files"""
    print("=" * 50)
    print("Steady Data Generator")
    print("=" * 50)
    print()
    
    # Create data directory
    create_data_directory()
    print()
    
    # Generate all data files
    print("Generating CSV files...")
    print()
    
    # Driver data (one CSV per driver)
    for driver_id in range(1, NUM_DRIVERS + 1):
        generate_driver_data(driver_id, WEEKS_OF_HISTORY)
    
    # Shared data files
    generate_weather_data(WEEKS_OF_HISTORY)
    generate_events_data()
    generate_preferences_data(NUM_DRIVERS)
    
    print()
    print("=" * 50)
    print("✓ All CSV files generated successfully!")
    print(f"✓ Data stored in '{DATA_DIR}/' directory")
    print("=" * 50)
    print()
    print("You can now run the backend server:")
    print("  python server.py")

if __name__ == "__main__":
    main()