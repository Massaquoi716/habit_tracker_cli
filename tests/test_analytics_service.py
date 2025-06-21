import pytest
import datetime
from datetime import timedelta
from freezegun import freeze_time
from src.analytics.analytics_service import AnalyticsService
from src.data_model.habit import DailyHabit, WeeklyHabit
from src.data_model.completion import Completion

class TestAnalyticsService:
    """Tests for the AnalyticsService class"""
    
    @freeze_time("2023-01-10")
    def test_get_unique_periods_daily(self):
        """Test getting unique daily periods"""
        timestamps = [
            datetime.datetime(2023, 1, 1, 12, 0),
            datetime.datetime(2023, 1, 1, 14, 0),  # Same day
            datetime.datetime(2023, 1, 2, 10, 0),
            datetime.datetime(2023, 1, 3, 9, 0),
            datetime.datetime(2023, 1, 3, 15, 0)   # Same day
        ]
        
        result = AnalyticsService._get_unique_periods(timestamps, "daily")
        assert len(result) == 3
        assert result[0].date() == datetime.date(2023, 1, 1)
        assert result[1].date() == datetime.date(2023, 1, 2)
        assert result[2].date() == datetime.date(2023, 1, 3)
    
    @freeze_time("2023-01-10")
    def test_get_unique_periods_weekly(self):
        """Test getting unique weekly periods"""
        timestamps = [
            datetime.datetime(2023, 1, 2, 12, 0),  # Monday week 1
            datetime.datetime(2023, 1, 3, 10, 0),  # Tuesday week 1
            datetime.datetime(2023, 1, 9, 9, 0),   # Monday week 2
            datetime.datetime(2023, 1, 10, 15, 0)  # Tuesday week 2
        ]
        
        result = AnalyticsService._get_unique_periods(timestamps, "weekly")
        assert len(result) == 2
        assert result[0].isocalendar()[:2] == (2023, 1)
        assert result[1].isocalendar()[:2] == (2023, 2)
    
    @freeze_time("2023-01-10")
    def test_get_longest_streak_daily(self):
        """Test calculating longest streak for daily habits"""
        timestamps = [
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 3),
            datetime.datetime(2023, 1, 4),
            datetime.datetime(2023, 1, 5)
        ]
        assert AnalyticsService.get_longest_streak(timestamps, "daily") == 5
        
        timestamps = [
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 4),
            datetime.datetime(2023, 1, 5),
            datetime.datetime(2023, 1, 6)
        ]
        assert AnalyticsService.get_longest_streak(timestamps, "daily") == 3  # Corrected from 2
        
        assert AnalyticsService.get_longest_streak([], "daily") == 0
    
    @freeze_time("2023-01-10")
    def test_get_longest_streak_weekly(self):
        """Test calculating longest streak for weekly habits"""
        timestamps = [
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 9),
            datetime.datetime(2023, 1, 16)
        ]
        assert AnalyticsService.get_longest_streak(timestamps, "weekly") == 3
        
        timestamps = [
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 9),
            datetime.datetime(2023, 1, 23)
        ]
        assert AnalyticsService.get_longest_streak(timestamps, "weekly") == 2
        
        timestamps = [
            datetime.datetime(2022, 12, 26),
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 9)
        ]
        assert AnalyticsService.get_longest_streak(timestamps, "weekly") == 3
    
    @freeze_time("2023-01-10")
    def test_get_current_streak_daily(self):
        """Test calculating current streak for daily habits"""
        timestamps = [
            datetime.datetime(2023, 1, 5),
            datetime.datetime(2023, 1, 6),
            datetime.datetime(2023, 1, 8),
            datetime.datetime(2023, 1, 9),
            datetime.datetime(2023, 1, 10, 9, 0)
        ]
        assert AnalyticsService.get_current_streak(timestamps, "daily") == 3
        
        timestamps = [
            datetime.datetime(2023, 1, 8),
            datetime.datetime(2023, 1, 6),
            datetime.datetime(2023, 1, 5)
        ]
        assert AnalyticsService.get_current_streak(timestamps, "daily") == 0
        
        assert AnalyticsService.get_current_streak([], "daily") == 0
    
    @freeze_time("2023-01-10")
    def test_get_current_streak_weekly(self):
        """Test calculating current streak for weekly habits"""
        timestamps = [
            datetime.datetime(2023, 1, 2),
            datetime.datetime(2023, 1, 9)
        ]
        assert AnalyticsService.get_current_streak(timestamps, "weekly") == 2
        
        timestamps = [
            datetime.datetime(2023, 1, 2)
        ]
        assert AnalyticsService.get_current_streak(timestamps, "weekly") == 0
        
        timestamps = [
            datetime.datetime(2023, 1, 9)
        ]
        assert AnalyticsService.get_current_streak(timestamps, "weekly") == 1
    
    @freeze_time("2023-01-10")
    def test_get_overall_longest_streak(self):
        """Test finding the overall longest streak across all habits"""
        habits = []
        
        daily = DailyHabit("Exercise")
        for day in range(1, 6):
            daily.check_off(datetime.datetime(2023, 1, day))
        habits.append(daily)
        
        weekly = WeeklyHabit("Read")
        for week in range(1, 4):
            weekly.check_off(datetime.datetime(2023, 1, week * 7 - 5))
        habits.append(weekly)
        
        max_streak, longest = AnalyticsService.get_overall_longest_streak(habits)
        assert max_streak == 5
        assert ("Exercise", "daily") in longest
    
    @freeze_time("2023-01-10")
    def test_get_longest_streak_by_periodicity(self):
        """Test finding longest streak for specific periodicity"""
        habits = []
        
        daily1 = DailyHabit("Exercise")
        for day in range(1, 6):
            daily1.check_off(datetime.datetime(2023, 1, day))
        habits.append(daily1)
        
        daily2 = DailyHabit("Meditate")
        for day in range(3, 7):
            daily2.check_off(datetime.datetime(2023, 1, day))
        habits.append(daily2)
        
        weekly = WeeklyHabit("Read")
        for week in range(1, 4):
            weekly.check_off(datetime.datetime(2023, 1, week * 7 - 5))
        habits.append(weekly)
        
        max_streak, longest = AnalyticsService.get_longest_streak_by_periodicity(habits, "daily")
        assert max_streak == 5
        assert "Exercise" in longest
        
        max_streak, longest = AnalyticsService.get_longest_streak_by_periodicity(habits, "weekly")
        assert max_streak == 3
        assert "Read" in longest
    
    @freeze_time("2023-01-10")
    def test_get_current_streaks_all_habits(self):
        """Test getting current streaks for all habits"""
        habits = []
        
        daily = DailyHabit("Exercise")
        for day in [5, 6, 8, 9, 10]:
            daily.check_off(datetime.datetime(2023, 1, day))
        habits.append(daily)
        
        weekly = WeeklyHabit("Read")
        for week in [1, 2]:
            weekly.check_off(datetime.datetime(2023, 1, week * 7 - 5))
        habits.append(weekly)
        
        daily2 = DailyHabit("Meditate")
        daily2.check_off(datetime.datetime(2023, 1, 5))
        habits.append(daily2)
        
        results = AnalyticsService.get_current_streaks_all_habits(habits)
        assert results == {
            "Exercise": 3,
            "Read": 2
        }