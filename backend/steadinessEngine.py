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
        - Driver works same 2 zones every day → Low entropy → High consistency (85%)
        - Driver works in 10+ different zones → High entropy → Low consistency (30%)
        
        Shannon Entropy Formula:
        H = -Σ(p(i) × log2(p(i))) where p(i) = probability of zone i
        
        Args:
            sessions: List of driver sessions
            
        Returns:
            Tuple of (consistency_score, raw_entropy)
        """
        # Collect all zones worked
        all_zones = []
        for session in sessions:
            all_zones.extend(session.zones)
        
        if not all_zones:
            return 0, 0.0
        
        # Count zone frequency
        zone_counts = Counter(all_zones)
        total_zone_visits = len(all_zones)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in zone_counts.values():
            probability = count / total_zone_visits
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        # Normalize entropy to 0-1 scale
        # Maximum entropy = log2(number of unique zones)
        unique_zones = len(zone_counts)
        max_entropy = np.log2(unique_zones) if unique_zones > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Convert to consistency score (invert - low entropy = high consistency)
        # 0 entropy (always same zone) = 100 score
        # Max entropy (all zones equally) = 0 score
        consistency_score = int(100 * (1 - normalized_entropy))
        
        return consistency_score, entropy
    
    def _generate_breakdown_insights(self, hour_score: int, earnings_score: int,
                                     zone_score: int, weekly_hours: List[float],
                                     eph_values: List[float]) -> List[str]:
        """
        Generate actionable insights based on consistency component scores
        
        Args:
            hour_score: Hour consistency score (0-100)
            earnings_score: Earnings consistency score (0-100)
            zone_score: Zone consistency score (0-100)
            weekly_hours: List of weekly hours worked
            eph_values: List of earnings per hour values
            
        Returns:
            List of insight strings for UI display
        """
        insights = []
        
        # Create score map for analysis
        scores = {
            "hours": hour_score,
            "earnings": earnings_score,
            "zones": zone_score
        }
        
        # Find weakest and strongest areas
        weakest_area = min(scores.items(), key=lambda x: x[1])
        strongest_area = max(scores.items(), key=lambda x: x[1])
        
        # INSIGHT 1: Address weakest area
        if weakest_area[1] < 60:
            if weakest_area[0] == "hours":
                avg_hours = statistics.mean(weekly_hours)
                insights.append(
                    f"📊 Your hours vary significantly week-to-week ({weakest_area[1]}% consistency). "
                    f"Try working ~{int(avg_hours)} hours consistently each week to improve predictability."
                )
            elif weakest_area[0] == "earnings":
                avg_eph = statistics.mean(eph_values)
                insights.append(
                    f"💰 Your earnings per hour fluctuate ({weakest_area[1]}% consistency). "
                    f"Target ${avg_eph:.0f}/hour by focusing on peak demand times (6-9am, 5-10pm)."
                )
            else:  # zones
                insights.append(
                    f"📍 You work in too many different zones ({weakest_area[1]}% consistency). "
                    f"Identify your top 2-3 most profitable zones and focus there for better stability."
                )
        
        # INSIGHT 2: Praise strongest area
        if strongest_area[1] >= 75:
            area_name = {
                "hours": "working hours",
                "earnings": "earnings rate", 
                "zones": "zone selection"
            }[strongest_area[0]]
            
            insights.append(
                f"✅ Excellent {area_name} consistency ({strongest_area[1]}%)! "
                f"This stability makes financial planning much easier."
            )
        
        # INSIGHT 3: Overall strategy recommendation
        all_scores_list = list(scores.values())
        avg_score = statistics.mean(all_scores_list)
        
        if avg_score >= 75:
            insights.append(
                f"🌟 Strong consistency across all factors (avg {int(avg_score)}%). "
                f"Maintain your current routine for reliable income."
            )
        elif avg_score >= 60:
            # Identify top 2 zones if zone consistency is weak
            insights.append(
                f"💡 You're on the right track. Focus on improving your {weakest_area[0]} "
                f"consistency to reach the top 25% of drivers."
            )
        else:
            insights.append(
                f"🎯 Consider creating a weekly routine: same hours, same zones, same strategy. "
                f"Consistency = predictability = peace of mind."
            )
        
        # INSIGHT 4: Specific actionable tip based on combination
        if hour_score < 60 and zone_score < 60:
            insights.append(
                f"💡 Quick win: Choose 2-3 zones and commit to 20-30 hours/week there. "
                f"Track results for 3 weeks to find your optimal routine."
            )
        elif earnings_score < 60 and hour_score >= 70:
            insights.append(
                f"💡 You have consistent hours but variable earnings. "
                f"Try shifting your schedule to peak demand times for better $/hour."
            )
        
        return insights if insights else ["Keep tracking your data to identify improvement opportunities."]
    
    def _empty_breakdown_response(self, reason: str) -> Dict:
        """Return empty breakdown response with error reason"""
        return {
            "hour_consistency": 0,
            "earnings_consistency": 0,
            "zone_consistency": 0,
            "overall_score": 0,
            "insights": [reason],
            "details": {
                "hours_cv": 0,
                "eph_cv": 0,
                "zone_entropy": 0,
                "avg_weekly_hours": 0,
                "avg_eph": 0,
                "unique_zones_worked": 0,
                "weeks_analyzed": 0
            }
        }
    
    # =========================================================================
    # AGGREGATION: Convert sessions to time periods
    # =========================================================================
    
    def _aggregate_by_period(self, sessions: List[DriverSession], 
                            period: str) -> List[PeriodAggregate]:
        """
        Aggregate individual sessions into time periods
        
        Converts raw sessions into daily/weekly/monthly summaries for analysis.
        
        Args:
            sessions: List of DriverSession objects
            period: "daily", "weekly", or "monthly"
            
        Returns:
            List of PeriodAggregate objects, sorted chronologically
        """
        if not sessions:
            return []
        
        # Dictionary to accumulate data by period
        period_map = defaultdict(lambda: {
            "earnings": 0.0,
            "hours": 0.0,
            "sessions_count": 0,
            "zones": []
        })
        
        for session in sessions:
            # Determine period key based on aggregation level
            if period == "daily":
                period_key = session.date
                label = session.date.strftime("%b %d")
                
            elif period == "weekly":
                # ISO week format (Monday = start of week)
                iso_cal = session.timestamp.isocalendar()
                period_key = (iso_cal[0], iso_cal[1])  # (year, week_number)
                # Label as "Week of [Monday date]"
                monday = session.timestamp - timedelta(days=session.timestamp.weekday())
                label = f"Week of {monday.strftime('%b %d')}"
                
            elif period == "monthly":
                period_key = (session.timestamp.year, session.timestamp.month)
                label = session.timestamp.strftime("%B %Y")
                
            else:
                raise ValueError(f"Invalid period: {period}. Use 'daily', 'weekly', or 'monthly'")
            
            # Accumulate data for this period
            period_map[period_key]["earnings"] += session.earnings
            period_map[period_key]["hours"] += session.hours_worked
            period_map[period_key]["sessions_count"] += 1
            period_map[period_key]["zones"].extend(session.zones)
            period_map[period_key]["label"] = label
        
        # Convert to PeriodAggregate objects
        aggregates = []
        for key in sorted(period_map.keys()):
            data = period_map[key]
            agg = PeriodAggregate(
                period_key=key,
                period_label=data["label"],
                earnings=data["earnings"],
                hours=data["hours"],
                sessions_count=data["sessions_count"],
                zones=data["zones"]
            )
            aggregates.append(agg)
        
        return aggregates
    
    # =========================================================================
    # VOLATILITY TREND: Historical consistency analysis
    # =========================================================================
    
    def get_volatility_trend(self, driver_id: str, weeks: int = 12) -> Dict:
        """
        Analyze how steadiness changes over time
        
        Shows whether a driver is becoming MORE or LESS consistent.
        Uses rolling window to track volatility trends.
        
        Real-world insight:
        - "Started at 12% volatility in August, now at 9% - you're improving!"
        - "Your volatility increased from 8% to 15% - what changed?"
        
        Args:
            driver_id: Driver to analyze
            weeks: How many weeks of history to analyze (default 12)
        
        Returns:
            {
                "current_volatility": 9,
                "trend": [
                    {"week": "Week of Aug 1", "volatility": 12},
                    {"week": "Week of Aug 15", "volatility": 11},
                    ...
                ],
                "direction": "improving",  # or "declining", "stable"
                "change_pct": -25.0,  # -25% = volatility decreased by 25%
                "summary": "Your consistency has improved by 25% over 12 weeks"
            }
        """
        if driver_id not in self._session_cache:
            return self._empty_volatility_response("No session data")
        
        sessions = self._session_cache[driver_id]
        
        # Filter to requested time window
        cutoff = datetime.now() - timedelta(weeks=weeks)
        recent = [s for s in sessions if s.timestamp >= cutoff]
        
        if len(recent) < self.MIN_SESSIONS_FOR_ANALYSIS:
            return self._empty_volatility_response("Insufficient data")
        
        # Aggregate by week
        weekly = self._aggregate_by_period(recent, "weekly")
        
        # Need at least ROLLING_WINDOW_WEEKS weeks for rolling analysis
        if len(weekly) < self.ROLLING_WINDOW_WEEKS:
            return self._empty_volatility_response(
                f"Need at least {self.ROLLING_WINDOW_WEEKS} weeks"
            )
        
        # Calculate rolling volatility using sliding window
        volatility_trend = []
        window_size = self.ROLLING_WINDOW_WEEKS
        
        for i in range(len(weekly) - window_size + 1):
            # Get window of weeks
            window = weekly[i:i + window_size]
            window_earnings = [w.earnings for w in window]
            
            # Calculate CV (volatility) for this window
            cv = self._calculate_cv(window_earnings)
            
            # Use the last week's label for this window
            week_label = window[-1].period_label
            
            volatility_trend.append({
                "week": week_label,
                "volatility": round(cv, 1)
            })
        
        # Current volatility (most recent window)
        current_volatility = volatility_trend[-1]["volatility"] if volatility_trend else 0
        
        # Determine trend direction
        if len(volatility_trend) >= 2:
            first_volatility = volatility_trend[0]["volatility"]
            last_volatility = volatility_trend[-1]["volatility"]
            
            # Calculate percentage change
            if first_volatility > 0:
                change_pct = ((last_volatility - first_volatility) / first_volatility) * 100
            else:
                change_pct = 0
            
            # Determine direction (5% threshold for "stable")
            if abs(change_pct) < 5:
                direction = TrendDirection.STABLE.value
            elif change_pct < 0:  # Volatility decreased = consistency improved
                direction = TrendDirection.IMPROVING.value
            else:  # Volatility increased = consistency declined
                direction = TrendDirection.DECLINING.value
        else:
            change_pct = 0
            direction = TrendDirection.INSUFFICIENT_DATA.value
        
        # Generate summary text
        summary = self._generate_volatility_summary(
            direction, 
            change_pct, 
            current_volatility, 
            weeks
        )
        
        return {
            "current_volatility": round(current_volatility, 1),
            "trend": volatility_trend,
            "direction": direction,
            "change_pct": round(change_pct, 1),
            "summary": summary,
            "weeks_analyzed": len(weekly)
        }
    
    def _generate_volatility_summary(self, direction: str, change_pct: float,
                                     current_volatility: float, weeks: int) -> str:
        """
        Generate human-readable summary of volatility trend
        
        Args:
            direction: Trend direction ("improving", "declining", "stable")
            change_pct: Percentage change in volatility
            current_volatility: Current volatility percentage
            weeks: Number of weeks analyzed
            
        Returns:
            Summary text for UI display
        """
        if direction == TrendDirection.IMPROVING.value:
            return (
                f"📈 Excellent! Your income consistency improved by {abs(change_pct):.0f}% "
                f"over {weeks} weeks. Current volatility: {current_volatility:.1f}%"
            )
        elif direction == TrendDirection.DECLINING.value:
            return (
                f"📉 Your income became {abs(change_pct):.0f}% less consistent over {weeks} weeks. "
                f"Review your recent schedule changes to identify what shifted."
            )
        elif direction == TrendDirection.STABLE.value:
            return (
                f"➡️ Your income consistency has been stable over {weeks} weeks "
                f"at ~{current_volatility:.1f}% volatility. Maintain your routine!"
            )
        else:
            return "Need more data to analyze trend"
    
    def _empty_volatility_response(self, reason: str) -> Dict:
        """Return empty volatility response with error reason"""
        return {
            "current_volatility": 0,
            "trend": [],
            "direction": TrendDirection.INSUFFICIENT_DATA.value,
            "change_pct": 0,
            "summary": reason,
            "weeks_analyzed": 0
        }


# Global engine instance
_engine = SteadinessEngine(city="Sydney")

def get_steadiness_score(driver_id: str, period: str = "weekly"):
    """
    Module-level wrapper for server.py
    """
    import features
    
    # Load and cache sessions if not already loaded
    if driver_id not in _engine._session_cache:
        sessions = features.load_driver_sessions_for_steadiness(driver_id)
        _engine.load_driver_sessions(driver_id, sessions)
    
    return _engine.get_steadiness_score(driver_id, period)

def get_consistency_breakdown(driver_id: str):
    """
    Module-level wrapper for server.py
    """
    import features
    
    # Load and cache sessions if not already loaded
    if driver_id not in _engine._session_cache:
        sessions = features.load_driver_sessions_for_steadiness(driver_id)
        _engine.load_driver_sessions(driver_id, sessions)
    
    return _engine.get_consistency_breakdown(driver_id)

def get_volatility_trend(driver_id: str, weeks: int = 12):
    """
    Module-level wrapper for server.py
    """
    import features
    
    # Load and cache sessions if not already loaded
    if driver_id not in _engine._session_cache:
        sessions = features.load_driver_sessions_for_steadiness(driver_id)
        _engine.load_driver_sessions(driver_id, sessions)
    
    return _engine.get_volatility_trend(driver_id, weeks)