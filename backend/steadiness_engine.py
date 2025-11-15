"""
Steadiness Engine - Production Implementation
Calculates income consistency and reliability scores for rideshare drivers

Core Philosophy: Predictable income > High but volatile income
A driver earning $800/week consistently can budget better than one earning $500-$1500/week

Statistical Foundation: Coefficient of Variation (CV)
CV = (std_dev / mean) × 100
Lower CV = Higher Steadiness = Better Financial Planning
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum
import statistics


class Period(Enum):
    """Time period aggregation options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendDirection(Enum):
    """Volatility trend directions"""
    IMPROVING = "improving"  # Volatility decreasing (getting more consistent)
    DECLINING = "declining"  # Volatility increasing (getting less consistent)
    STABLE = "stable"        # No significant change
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class DriverSession:
    """
    Represents a single driving session with all relevant metrics
    
    This is the atomic unit of data - everything else is aggregated from sessions
    """
    driver_id: str
    timestamp: datetime
    hours_worked: float
    earnings: float
    zones: List[str]  # e.g., ["CBD", "Airport", "Suburbs_North"]
    
    @property
    def earnings_per_hour(self) -> float:
        """Earnings rate for this session"""
        return self.earnings / self.hours_worked if self.hours_worked > 0 else 0.0
    
    @property
    def date(self) -> datetime:
        """Date of session (for convenience)"""
        return self.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)


@dataclass
class PeriodAggregate:
    """
    Aggregated data for a time period (day, week, or month)
    
    Used for calculating steadiness metrics across consistent time windows
    """
    period_key: Union[datetime, Tuple]
    period_label: str
    earnings: float = 0.0
    hours: float = 0.0
    sessions_count: int = 0
    zones: List[str] = field(default_factory=list)
    
    @property
    def earnings_per_hour(self) -> float:
        """Average earnings rate for this period"""
        return self.earnings / self.hours if self.hours > 0 else 0.0


class SteadinessEngine:
    """
    Core engine for calculating driver income consistency metrics
    
    Key Metrics:
    1. Steadiness Score (0-100): Overall consistency rating
    2. Consistency Breakdown: Hours, Earnings Rate, Zone consistency
    3. Volatility Trend: How consistency changes over time
    
    Statistical Methods:
    - Coefficient of Variation for earnings consistency
    - Standard deviation analysis for hours
    - Shannon Entropy for zone diversity
    - Rolling window volatility for trend analysis
    """
    
    # Tuning parameters (calibrated for rideshare economics)
    CV_SCALING_FACTOR = 2.5  # Converts CV to 0-100 score
    MAX_CV_FOR_SCORING = 40  # CV above 40% scores as 0
    MIN_SESSIONS_FOR_ANALYSIS = 4  # Minimum data points needed
    ROLLING_WINDOW_WEEKS = 4  # Window size for volatility trends
    
    # Percentile thresholds for text generation
    PERCENTILE_EXCEPTIONAL = 90
    PERCENTILE_GOOD = 75
    PERCENTILE_AVERAGE = 50
    PERCENTILE_NEEDS_WORK = 25
    
    def __init__(self, city: str = "Sydney"):
        """
        Initialize the Steadiness Engine
        
        Args:
            city: City name for comparative analysis (e.g., "Sydney", "Melbourne")
        """
        self.city = city
        self._session_cache: Dict[str, List[DriverSession]] = {}
        self._percentile_cache: Dict[str, List[float]] = {}
        
    def load_driver_sessions(self, driver_id: str, sessions: List[DriverSession]):
        """
        Load session data for a driver
        
        Args:
            driver_id: Unique driver identifier
            sessions: List of DriverSession objects
        """
        # Sort by timestamp for chronological analysis
        self._session_cache[driver_id] = sorted(sessions, key=lambda s: s.timestamp)
    
    def load_bulk_sessions(self, sessions_by_driver: Dict[str, List[DriverSession]]):
        """
        Load sessions for multiple drivers (for percentile calculations)
        
        Args:
            sessions_by_driver: Dict mapping driver_id to their sessions
        """
        for driver_id, sessions in sessions_by_driver.items():
            self.load_driver_sessions(driver_id, sessions)
    
    # =========================================================================
    # CORE METRIC: STEADINESS SCORE
    # =========================================================================
    
    def get_steadiness_score(self, driver_id: str, period: str = "weekly") -> Dict:
        """
        Calculate overall steadiness/consistency score (0-100)
        
        This is the headline metric shown in the UI circular progress chart.
        
        Algorithm:
        1. Aggregate sessions into time periods (daily/weekly/monthly)
        2. Calculate coefficient of variation (CV) of earnings
        3. Convert CV to 0-100 score (lower CV = higher score)
        4. Compare to all other drivers for percentile ranking
        
        Args:
            driver_id: Driver to analyze
            period: Aggregation period ("daily", "weekly", "monthly")
        
        Returns:
            {
                "score": 72,  # 0-100 steadiness rating
                "percentile": 72,  # Better than 72% of drivers
                "comparison_text": "More consistent than 72% of Sydney drivers",
                "period": "weekly",
                "cv": 28.5,  # Raw coefficient of variation
                "sample_size": 12,  # Number of periods analyzed
                "mean_earnings": 850.0,  # Average earnings per period
                "std_dev": 242.25  # Standard deviation
            }
        """
        # Validate inputs
        if driver_id not in self._session_cache:
            return self._empty_steadiness_response(period, "No session data found")
        
        sessions = self._session_cache[driver_id]
        
        # Filter to recent sessions (last 90 days for good sample size)
        cutoff_date = datetime.now() - timedelta(days=90)
        recent_sessions = [s for s in sessions if s.timestamp >= cutoff_date]
        
        if len(recent_sessions) < self.MIN_SESSIONS_FOR_ANALYSIS:
            return self._empty_steadiness_response(
                period, 
                f"Need at least {self.MIN_SESSIONS_FOR_ANALYSIS} sessions"
            )
        
        # Aggregate sessions by period
        aggregates = self._aggregate_by_period(recent_sessions, period)
        
        if len(aggregates) < 2:
            return self._empty_steadiness_response(
                period,
                f"Need at least 2 {period} periods"
            )
        
        # Extract earnings for statistical analysis
        earnings_list = [agg.earnings for agg in aggregates]
        
        # Calculate coefficient of variation
        mean_earnings = statistics.mean(earnings_list)
        std_dev = statistics.stdev(earnings_list)
        cv = (std_dev / mean_earnings * 100) if mean_earnings > 0 else 0
        
        # Convert CV to 0-100 steadiness score
        score = self._cv_to_steadiness_score(cv)
        
        # Calculate percentile ranking
        percentile = self._calculate_percentile(driver_id, score, period)
        
        # Generate human-readable comparison text
        comparison_text = self._generate_comparison_text(percentile)
        
        return {
            "score": score,
            "percentile": percentile,
            "comparison_text": comparison_text,
            "period": period,
            "cv": round(cv, 1),
            "sample_size": len(aggregates),
            "mean_earnings": round(mean_earnings, 2),
            "std_dev": round(std_dev, 2),
            "earnings_range": {
                "min": round(min(earnings_list), 2),
                "max": round(max(earnings_list), 2)
            }
        }
    
    def _cv_to_steadiness_score(self, cv: float) -> int:
        """
        Convert coefficient of variation to 0-100 steadiness score
        
        Scoring Logic:
        - CV of 0% (perfectly consistent) → 100 score
        - CV of 40%+ (highly variable) → 0 score
        - Linear interpolation between
        
        Args:
            cv: Coefficient of variation as percentage
            
        Returns:
            Integer score from 0-100
        """
        # Cap CV at maximum for scoring
        cv_capped = min(cv, self.MAX_CV_FOR_SCORING)
        
        # Linear transformation: 0% CV = 100 score, 40% CV = 0 score
        score = 100 - (cv_capped * self.CV_SCALING_FACTOR)
        
        # Ensure bounds
        return max(0, min(100, int(round(score))))
    
    def _calculate_percentile(self, driver_id: str, score: float, 
                             period: str) -> int:
        """
        Calculate percentile ranking vs other drivers in same city
        
        Args:
            driver_id: Driver being analyzed
            score: Their steadiness score
            period: Time period used
            
        Returns:
            Percentile (0-100) representing "better than X% of drivers"
        """
        # Calculate scores for all other drivers
        cache_key = f"{self.city}_{period}"
        
        if cache_key not in self._percentile_cache:
            all_scores = []
            
            for other_id in self._session_cache.keys():
                if other_id == driver_id:
                    continue
                
                # Get their steadiness score
                result = self.get_steadiness_score(other_id, period)
                if result["score"] > 0:  # Valid score
                    all_scores.append(result["score"])
            
            self._percentile_cache[cache_key] = all_scores
        
        comparison_scores = self._percentile_cache[cache_key]
        
        if not comparison_scores:
            return 50  # Default to median if no comparison data
        
        # Count drivers with lower scores
        lower_count = sum(1 for s in comparison_scores if s < score)
        
        # Calculate percentile
        percentile = (lower_count / len(comparison_scores)) * 100
        
        return int(round(percentile))
    
    def _generate_comparison_text(self, percentile: int) -> str:
        """
        Generate human-readable comparison text based on percentile
        
        Args:
            percentile: Driver's percentile ranking (0-100)
            
        Returns:
            Comparison text for UI display
        """
        if percentile >= self.PERCENTILE_EXCEPTIONAL:
            return f"Exceptionally consistent - top 10% of {self.city} drivers"
        elif percentile >= self.PERCENTILE_GOOD:
            return f"More consistent than {percentile}% of {self.city} drivers"
        elif percentile >= self.PERCENTILE_AVERAGE:
            return f"More consistent than {percentile}% of {self.city} drivers"
        elif percentile >= self.PERCENTILE_NEEDS_WORK:
            return f"Room to improve consistency - {percentile}th percentile in {self.city}"
        else:
            return f"High income variability - focus on building routine"
    
    def _empty_steadiness_response(self, period: str, reason: str) -> Dict:
        """Return empty steadiness response with error reason"""
        return {
            "score": 0,
            "percentile": 0,
            "comparison_text": reason,
            "period": period,
            "cv": 0,
            "sample_size": 0,
            "mean_earnings": 0,
            "std_dev": 0,
            "earnings_range": {"min": 0, "max": 0}
        }
    
    # =========================================================================
    # BREAKDOWN: COMPONENT CONSISTENCY ANALYSIS
    # =========================================================================
    
    def get_consistency_breakdown(self, driver_id: str) -> Dict:
        """
        Analyze WHY a driver has their steadiness score
        
        Breaks down overall consistency into 3 components:
        1. Hour Consistency - Do they work similar hours each week?
        2. Earnings Consistency - Do they earn similar $/hour?
        3. Zone Consistency - Do they work in the same areas?
        
        Use Case: Driver sees low steadiness score (45%). This breakdown shows:
        "Your hours are consistent (78%) but you work too many different zones (30%).
        Focus on your top 2-3 zones to improve predictability."
        
        Args:
            driver_id: Driver to analyze
            
        Returns:
            {
                "hour_consistency": 78,
                "earnings_consistency": 72,
                "zone_consistency": 65,
                "overall_score": 72,
                "insights": ["Your hours are consistent...", "Focus on..."],
                "details": {...}  # Raw metrics for transparency
            }
        """
        if driver_id not in self._session_cache:
            return self._empty_breakdown_response("No session data")
        
        sessions = self._session_cache[driver_id]
        
        # Filter recent sessions (90 days)
        cutoff = datetime.now() - timedelta(days=90)
        recent = [s for s in sessions if s.timestamp >= cutoff]
        
        if len(recent) < self.MIN_SESSIONS_FOR_ANALYSIS:
            return self._empty_breakdown_response("Insufficient data")
        
        # Aggregate by week for hour analysis
        weekly = self._aggregate_by_period(recent, "weekly")
        
        if len(weekly) < 2:
            return self._empty_breakdown_response("Need at least 2 weeks")
        
        # 1. HOUR CONSISTENCY
        # Measures: How consistent are weekly hours worked?
        weekly_hours = [w.hours for w in weekly]
        hours_cv = self._calculate_cv(weekly_hours)
        hour_consistency = self._cv_to_steadiness_score(hours_cv)
        
        # 2. EARNINGS CONSISTENCY (PER HOUR)
        # Measures: How consistent is earnings rate across sessions?
        eph_values = [s.earnings_per_hour for s in recent if s.hours_worked > 0]
        eph_cv = self._calculate_cv(eph_values)
        earnings_consistency = self._cv_to_steadiness_score(eph_cv)
        
        # 3. ZONE CONSISTENCY
        # Measures: Do they stick to same zones or work everywhere?
        zone_consistency, zone_entropy = self._calculate_zone_consistency(recent)
        
        # 4. OVERALL SCORE
        overall_result = self.get_steadiness_score(driver_id, "weekly")
        overall_score = overall_result["score"]
        
        # 5. GENERATE ACTIONABLE INSIGHTS
        insights = self._generate_breakdown_insights(
            hour_consistency, 
            earnings_consistency, 
            zone_consistency,
            weekly_hours,
            eph_values
        )
        
        return {
            "hour_consistency": hour_consistency,
            "earnings_consistency": earnings_consistency,
            "zone_consistency": zone_consistency,
            "overall_score": overall_score,
            "insights": insights,
            "details": {
                "hours_cv": round(hours_cv, 1),
                "eph_cv": round(eph_cv, 1),
                "zone_entropy": round(zone_entropy, 2),
                "avg_weekly_hours": round(statistics.mean(weekly_hours), 1),
                "avg_eph": round(statistics.mean(eph_values), 2),
                "unique_zones_worked": len(set(z for s in recent for z in s.zones)),
                "weeks_analyzed": len(weekly)
            }
        }
    
    def _calculate_cv(self, values: List[float]) -> float:
        """
        Calculate coefficient of variation
        
        CV = (standard_deviation / mean) × 100
        
        Returns:
            CV as percentage
        """
        if len(values) < 2:
            return 0.0
        
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0
        
        std_dev = statistics.stdev(values)
        return (std_dev / mean_val) * 100
    
    def _calculate_zone_consistency(self, sessions: List[DriverSession]) -> Tuple[int, float]:
        """
        Calculate zone consistency using Shannon Entropy
        
        Logic:
        - Driver works same 2 