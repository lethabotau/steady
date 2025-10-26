#feature_builder - prepares and clusters features from csv data sources

def load_driver_data(driver_id: str):
    """load driver data from csv"""

    #dummy return value
    return {

        """
        Loads driver's historical data from CSV
    
        In real implementation:
        1. Open driverN.csv (e.g., driver1.csv, driver2.csv)
        2. Parse CSV rows (each row = one trip)
        3. Calculate aggregate statistics
        4. Return formatted dictionary
    
        CSV example
        date,trips,earnings,hours,rating
        2024-10-01,12,145,5.5,4.8
        2024-10-02,15,178,6.2,4.9
    
        driver_id: Unique identifier (matches CSV filename)
    
        dict with driver profile and aggregate stats
        
        """

        "driverID": driver_id, 
        "total_trips": 1247, 
        "total_earnings": 42350,
        "avg_rating": 4.8,
        "member_since": "2024-03-15" 

    }

def load_weather_data(location: str, date_range: dict):
    """
    Loads weather data for location and date range
    
    In real implementation:
    1.Call weather API (or read from cached weather.csv)
    2.Filter to date range needed
    3.Return structured weather conditions
    
    Weather CSV example:
    date,location,condition,temp,humidity,windSpeed
    2024-10-01,Cape Town,sunny,22,65,15
    2024-10-02,Gaborone,rain,18,85,25
        
    Used by: 
    -Forecast Engine: Factor weather into predictions
    -Insights Engine: Analyze weather-earnings correlation
    -Recommendation Engine: Suggest working on rainy days
    """
    # Dummy data - real version would call API or read CSV
    return {
        "location": location,
        "data": [
            {"date": "2026-10-20", "condition": "rain", "temp": 18},
            {"date": "2026-10-21", "condition": "sunny", "temp": 22},
            {"date": "2026-10-22", "condition": "cloudy", "temp": 20}
        ]
    }

def load_event_data(location: str, date_range: dict):
    """
Feature Builder - Prepares and aggregates features from CSV data sources

This is the "data loader" layer that sits between raw CSV files and the engines
Think of it as the ETL (Extract, Transform, Load) pipeline

Data sources (from architecture doc):
- Uber Dummy Data (driverX.csv): Historical trip/earnings data
- Weather API (weather.csv): Weather conditions by date
- Holiday/Event APIs: Special events and holidays
- Geodata: Zone/location information
- User Targets & Preferences: User-configured settings

Job: Load, clean, and format data for the engines to consume
"""

def load_driver_data(driver_id: str):
    """
    Loads driver's historical data from CSV
    
    In real implementation:
    1. Open driverX.csv (e.g., driver1.csv, driver2.csv)
    2. Parse CSV rows (each row = one trip or one day's summary)
    3. Calculate aggregate statistics
    4. Return formatted dictionary
    
    CSV might look like:
    date,trips,earnings,hours,rating
    2024-10-01,12,145,5.5,4.8
    2024-10-02,15,178,6.2,4.9
    ...
    
    Args:
        driver_id: Unique identifier (matches CSV filename)
    
    Returns:
        dict with driver profile and aggregate stats
        
    Used by: All engines need this basic profile data
    """
    # Dummy data - in real version, would read from CSV like this:
    # import pandas as pd
    # df = pd.read_csv(f'data/{driver_id}.csv')
    # return {
    #     "total_trips": len(df),
    #     "total_earnings": df['earnings'].sum(),
    #     etc...
    # }
    
    return {
        "driver_id": driver_id,  # Unique identifier
        "total_trips": 1247,  # COUNT aggregation: number of trip records
        "total_earnings": 42350,  # SUM aggregation: total $ earned
        "avg_rating": 4.8,  # AVERAGE aggregation: mean customer rating
        "member_since": "2024-03-15"  # MIN aggregation: earliest date in CSV
    }

def load_weather_data(location: str, date_range: dict):
    """
    Loads weather data for location and date range
    
    In real implementation:
    1. Call weather API (or read from cached weather.csv)
    2. Filter to date range needed
    3. Return structured weather conditions
    
    Weather CSV might look like:
    date,location,condition,temp_c,humidity,wind_speed
    2024-10-01,Sydney,sunny,22,65,15
    2024-10-02,Sydney,rain,18,85,25
    ...
    
    Args:
        location: City/area (e.g., "Sydney")
        date_range: Dict with start date and number of days
                    e.g., {"start": "2026-10-20", "days": 14}
    
    Returns:
        dict with structured array of daily weather conditions
        Structure ensures all engines can easily parse and use the data
        
    Used by: 
    - Forecast Engine: Factor weather into earnings predictions
    - Insights Engine: Analyze weather-earnings correlation
    - Recommendation Engine: Suggest working on rainy days for boost
    """
    # Dummy data - real version would call API or read CSV like:
    # import requests
    # response = requests.get(f'https://api.weather.com/{location}')
    # parse response and format into structure below
    
    return {
        "location": location,
        # Array of daily weather forecasts in consistent structure
        "data": [
            {
                "date": "2026-10-20",  # ISO format date
                "condition": "rain",  # Standardized: "sunny", "rain", "cloudy", "storm"
                "temp": 18  # Temperature in Celsius (integer)
            },
            {
                "date": "2026-10-21",
                "condition": "sunny",
                "temp": 22
            },
            {
                "date": "2026-10-22",
                "condition": "cloudy",
                "temp": 20
            }
        ]
    }

def load_event_data(location: str, date_range: dict):
    """
    Loads holiday and event data
    
    In real implementation:
    1.Query event APIs (Ticketmaster, Eventbrite, local event calendars)
    2.Check holiday calendars for event (public holidays, school holidays)
    3.Filter date range and location
    4.Return structured list of events
    
    Why events matter:
    -Concerts/sports = surge pricing and high demand
    -Public holidays = different traffic patterns
    -School holidays = family travel spikes
        
    Used by:
    - Forecast Engine: Boost predictions for event days
    - Insights Engine: Show upcoming opportunities
    - Recommendation Engine: Alert driver to work during events
    """
    # Dummy data - real version would call multiple APIs:
    # events_response = requests.get('https://api.ticketmaster.com/...')
    # holidays_response = requests.get('https://api.holidays.com/...')
    # Combine and structure the data
    return {
        "events": [
            {"name": "Sydney Marathon", "date": "2026-10-25", "type": "sports"},
            {"name": "Concert", "date": "2026-10-30", "type": "entertainment"}
        ],
        "holidays": []
    }

def get_user_preferences(driver_id: str):
    """
    Returns user's preferences
    
    In real implementation:
    1.Load from preferences.csv or user database
    2.Return user's configured settings
    
    Preferences CSV example:
    driver_id,income_floor,preferred_zones,preferred_hours,weekly_goal
    driver1,800,"Sydney CBD,Bondi Beach","7-9am,5-8pm",4800
    driver2,1000,"Airport,City","6-10am,4-9pm",5200
    
    Why preferences matter:
    -Personalize recommendations (don't suggest zones they dislike)
    -Track goal progress (motivate to hit targets)
    -Respect constraints (some drivers only work mornings)
        
    Used by:
    - Recommendation Engine: Filter suggestions to user's preferences
    - Forecast Engine: Consider user's typical working pattern
    - All engines: Personalize outputs to individual driver
    """
    return {
        "income_floor": 800,  # Minimum weekly target
        "preferred_zones": ["Cape Town CBD", "Clifton 4th", "Airport"],
        "preferred_hours": ["7-9am", "5-8pm"],
        "weekly_goal": 4800,
        "monthly_goal": 20000
    }

def build_features(driver_id: str, date: str):
    """
    Aggregates all data sources into feature set for engines
    
    This is the "master loader" that pulls everything together
    Think of it as preparing a complete data package for the engines
    
    Instead of each engine calling individual loaders, they call this
    once and get everything they need in one structured object
    
    Args:
        driver_id: Unique identifier for the driver
        date: Starting date for time-based data (e.g., "2026-10-20")
    
    Returns:
        dict containing all data sources in structured format:
        -Driver's historical data and profile
        -Weather forecast for next 14 days
        -Events happening in next 14 days
        -User's preferences and goals
        
    Used by:
    -Called by server routes before passing to engines
    -Ensures all engines work with same data snapshot
    -Makes engines simpler (they don't need to know about data loading)
    
    Real implementation:
    This would be called at the start of each API request to prepare
    a complete data context for whatever analysis is needed
    """
    return {
        "driver_features": load_driver_data(driver_id),
        "weather_features": load_weather_data("Gaborone", {"start": date, "days": 14}),
        "event_features": load_event_data("Gaborone", {"start": date, "days": 14}),
        "preferences": get_user_preferences(driver_id)
    }