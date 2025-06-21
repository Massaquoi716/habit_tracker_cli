# tests/unit/test_habit_model.py
import pytest
import datetime
from datetime import timedelta
from freezegun import freeze_time
from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit
from src.data_model.completion import Completion

class TestCompletion:
    """Tests for the Completion class"""
    
    def test_completion_creation_defaults(self):
        """Test creating a completion with default values"""
        before = datetime.datetime.now()
        completion = Completion()
        after = datetime.datetime.now()
        
        assert isinstance(completion.id, str)
        assert before <= completion.timestamp <= after
        assert completion.notes is None
        assert completion.mood_score is None
    
    def test_completion_creation_custom_values(self):
        """Test creating a completion with custom values"""
        timestamp = datetime.datetime(2023, 1, 1, 12, 0)
        completion = Completion(
            timestamp=timestamp,
            notes="Test note",
            mood_score=3,
            _id="test-id"
        )
        
        assert completion.id == "test-id"
        assert completion.timestamp == timestamp
        assert completion.notes == "Test note"
        assert completion.mood_score == 3
    
    def test_completion_mood_score_validation(self):
        """Test mood score validation"""
        with pytest.raises(ValueError, match="Mood score must be between 1 and 5"):
            Completion(mood_score=0)
        with pytest.raises(ValueError, match="Mood score must be between 1 and 5"):
            Completion(mood_score=6)
        
        # Test valid scores
        for score in range(1, 6):
            Completion(mood_score=score)
    
    def test_completion_to_dict(self):
        """Test serialization to dictionary"""
        timestamp = datetime.datetime(2023, 1, 1, 12, 0)
        completion = Completion(
            timestamp=timestamp,
            notes="Test note",
            mood_score=3,
            _id="test-id"
        )
        
        expected = {
            "id": "test-id",
            "timestamp": "2023-01-01T12:00:00",
            "notes": "Test note",
            "mood_score": 3
        }
        assert completion.to_dict() == expected
    
    def test_completion_from_dict(self):
        """Test deserialization from dictionary"""
        data = {
            "id": "test-id",
            "timestamp": "2023-01-01T12:00:00",
            "notes": "Test note",
            "mood_score": 3
        }
        
        completion = Completion.from_dict(data)
        assert completion.id == "test-id"
        assert completion.timestamp == datetime.datetime(2023, 1, 1, 12, 0)
        assert completion.notes == "Test note"
        assert completion.mood_score == 3
    
    def test_completion_str_repr(self):
        """Test string representation"""
        completion = Completion(
            timestamp=datetime.datetime(2023, 1, 1, 12, 0),
            notes="Test note",
            mood_score=3
        )
        
        assert str(completion) == "Completed at 2023-01-01 12:00:00 Notes: 'Test note' Mood: 3/5"
        assert repr(completion).startswith("Completion(timestamp='2023-01-01T12:00:00'")
    
    def test_completion_equality(self):
        """Test equality comparison"""
        c1 = Completion(_id="same")
        c2 = Completion(_id="same")
        c3 = Completion(_id="different")
        
        assert c1 == c2
        assert c1 != c3
        assert c1 != "not a completion"

class TestBaseHabit:
    """Tests for the BaseHabit class"""
    
    def test_base_habit_creation(self):
        """Test basic habit creation"""
        habit = BaseHabit("Test Habit")
        
        assert habit.name == "Test Habit"
        assert isinstance(habit.id, str)
        assert isinstance(habit.creation_date, datetime.datetime)
        assert habit.get_completion_records() == []
    
    def test_base_habit_creation_with_completions(self):
        """Test habit creation with existing completions"""
        completions = [
            Completion(datetime.datetime(2023, 1, 1)),
            Completion(datetime.datetime(2023, 1, 2))
        ]
        habit = BaseHabit(
            "Test Habit",
            creation_date=datetime.datetime(2023, 1, 1),
            _id="test-id",
            completion_records=completions
        )
        
        assert habit.id == "test-id"
        assert habit.creation_date == datetime.datetime(2023, 1, 1)
        assert len(habit.get_completion_records()) == 2
        assert habit.get_completion_records()[0].timestamp == datetime.datetime(2023, 1, 1)
    
    def test_base_habit_name_validation(self):
        """Test habit name validation"""
        with pytest.raises(ValueError, match="Habit name cannot be empty"):
            BaseHabit("")
        with pytest.raises(ValueError, match="Habit name cannot be empty"):
            BaseHabit(None)
    
    def test_base_habit_check_off(self):
        """Test recording completions"""
        habit = BaseHabit("Test Habit")
        
        # Default completion
        c1 = habit.check_off()
        assert len(habit.get_completion_records()) == 1
        assert c1 in habit.get_completion_records()
        
        # Custom completion
        timestamp = datetime.datetime(2023, 1, 1, 12, 0)
        c2 = habit.check_off(timestamp, "Note", 3)
        assert len(habit.get_completion_records()) == 2
        assert c2.timestamp == timestamp
        assert c2.notes == "Note"
        assert c2.mood_score == 3
    
    def test_base_habit_reset_completions(self):
        """Test resetting completions"""
        habit = BaseHabit("Test Habit")
        habit.check_off()
        habit.check_off()
        
        assert len(habit.get_completion_records()) == 2
        habit.reset_completions()
        assert len(habit.get_completion_records()) == 0
    
    def test_base_habit_to_dict(self):
        """Test serialization to dictionary"""
        habit = BaseHabit(
            "Test Habit",
            creation_date=datetime.datetime(2023, 1, 1),
            _id="test-id"
        )
        habit.check_off(datetime.datetime(2023, 1, 2), "Note", 3)
        
        result = habit.to_dict()
        assert result["id"] == "test-id"
        assert result["name"] == "Test Habit"
        assert result["creation_date"] == "2023-01-01T00:00:00"
        assert result["type"] == "BaseHabit"
        assert len(result["completion_records"]) == 1
        assert result["completion_records"][0]["notes"] == "Note"
    
    def test_base_habit_str_repr(self):
        """Test string representation"""
        habit = BaseHabit("Test Habit", creation_date=datetime.datetime(2023, 1, 1))
        
        assert str(habit) == "BaseHabit('Test Habit', created 2023-01-01)"
        assert repr(habit).startswith("BaseHabit(name='Test Habit'")
    
    def test_base_habit_abstract_methods(self):
        """Test abstract methods raise NotImplementedError"""
        habit = BaseHabit("Test Habit")
        
        with pytest.raises(NotImplementedError):
            habit.periodicity
        with pytest.raises(NotImplementedError):
            habit.is_completed_for_period()
        with pytest.raises(NotImplementedError):
            habit.is_due_and_not_completed()
        with pytest.raises(NotImplementedError):
            habit.is_broken()

class TestDailyHabit:
    """Tests for the DailyHabit class"""
    
    @freeze_time("2023-01-10")
    def test_daily_habit_properties(self):
        """Test basic daily habit properties"""
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 1))
        
        assert habit.periodicity == "daily"
        
        # Test with proper dictionary data
        test_data = {
            "name": "Test Habit",
            "creation_date": "2023-01-01T00:00:00",
            "completion_records": []
        }
        assert isinstance(DailyHabit.from_dict(test_data), DailyHabit)
    
    @freeze_time("2023-01-10")
    def test_daily_habit_is_completed_for_period(self):
        """Test checking if habit is completed for current day"""
        habit = DailyHabit("Daily Test")
        
        # Not completed
        assert not habit.is_completed_for_period()
        
        # Completed today
        habit.check_off(datetime.datetime(2023, 1, 10, 12, 0))
        assert habit.is_completed_for_period()
        
        # Completed yesterday but not today
        habit.check_off(datetime.datetime(2023, 1, 9, 12, 0))
        assert habit.is_completed_for_period()  # Still true because of today's completion
    
    @freeze_time("2023-01-10 12:00:00")
    def test_daily_habit_is_due_and_not_completed(self):
        """Test checking if habit is due and not completed"""
        # Habit created today, not completed - should be due
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 10))
        assert habit.is_due_and_not_completed()  # Changed expectation
        
        # Habit created yesterday, not completed - should be due
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 9))
        assert habit.is_due_and_not_completed()
        
        # Habit created yesterday, completed today - not due
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 9))
        habit.check_off(datetime.datetime(2023, 1, 10, 10, 0))
        assert not habit.is_due_and_not_completed()
    
    @freeze_time("2023-01-10")
    def test_daily_habit_is_broken(self):
        """Test checking if habit streak is broken"""
        # Never completed, created more than 1 day ago
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 1))
        assert habit.is_broken()
        
        # Completed yesterday, not today
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 1))
        habit.check_off(datetime.datetime(2023, 1, 9))
        assert habit.is_broken()
        
        # Completed today
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 1))
        habit.check_off(datetime.datetime(2023, 1, 10))
        assert not habit.is_broken()
        
        # Completed yesterday and today
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 1))
        habit.check_off(datetime.datetime(2023, 1, 9))
        habit.check_off(datetime.datetime(2023, 1, 10))
        assert not habit.is_broken()
        
        # Created today, never completed
        habit = DailyHabit("Daily Test", creation_date=datetime.datetime(2023, 1, 10))
        assert not habit.is_broken()

class TestWeeklyHabit:
    """Tests for the WeeklyHabit class"""
    
    @freeze_time("2023-01-10")  # Tuesday (week 2)
    def test_weekly_habit_properties(self):
        """Test basic weekly habit properties"""
        habit = WeeklyHabit("Weekly Test", due_weekday=0)  # Monday
        
        assert habit.periodicity == "weekly"
        assert habit.due_weekday == 0
        
        # Test with proper dictionary data
        test_data = {
            "name": "Test Habit",
            "creation_date": "2023-01-01T00:00:00",
            "due_weekday": 0,
            "completion_records": []
        }
        assert isinstance(WeeklyHabit.from_dict(test_data), WeeklyHabit)
    
    def test_weekly_habit_due_weekday_validation(self):
        """Test due weekday validation"""
        with pytest.raises(ValueError, match="due_weekday must be 0"):
            WeeklyHabit("Test", due_weekday=-1)
        with pytest.raises(ValueError, match="due_weekday must be 0"):
            WeeklyHabit("Test", due_weekday=7)
        
        # Test valid weekdays
        for day in range(0, 7):
            WeeklyHabit("Test", due_weekday=day)
    
    @freeze_time("2023-01-10")  # Tuesday (week 2)
    def test_weekly_habit_is_completed_for_period(self):
        """Test checking if habit is completed for current week"""
        habit = WeeklyHabit("Weekly Test", due_weekday=0)  # Monday
        
        # Not completed
        assert not habit.is_completed_for_period()
        
        # Completed this week
        habit.check_off(datetime.datetime(2023, 1, 9))  # Monday
        assert habit.is_completed_for_period()
        
        # Completed last week but not this week
        habit = WeeklyHabit("Weekly Test", due_weekday=0)
        habit.check_off(datetime.datetime(2023, 1, 2))  # Monday last week
        assert not habit.is_completed_for_period()
    
    @freeze_time("2023-01-10 12:00:00")  # Tuesday (week 2)
    def test_weekly_habit_is_due_and_not_completed(self):
        """Test checking if habit is due and not completed"""
        # Habit created this week, not completed - should be due after due weekday
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 9)  # Monday this week
        )
        assert habit.is_due_and_not_completed()  # Changed expectation (Tuesday after Monday)
        
        # Habit created last week, not completed this week - should be due
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 2)  # Monday last week
        )
        assert habit.is_due_and_not_completed()
        
        # Habit created last week, completed this week - not due
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 2)  # Monday last week
        )
        habit.check_off(datetime.datetime(2023, 1, 9))  # Monday this week
        assert not habit.is_due_and_not_completed()
    
    @freeze_time("2023-01-10")  # Tuesday (week 2)
    def test_weekly_habit_is_broken(self):
        """Test checking if habit streak is broken"""
        # Never completed, created more than 1 week ago
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 1)  # Sunday week 52
        )
        assert habit.is_broken()
        
        # Completed last week, not this week
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 1)
        )
        habit.check_off(datetime.datetime(2023, 1, 2))  # Monday week 1
        assert habit.is_broken()
        
        # Completed this week
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 1)
        )
        habit.check_off(datetime.datetime(2023, 1, 9))  # Monday week 2
        assert not habit.is_broken()
        
        # Created this week, never completed
        habit = WeeklyHabit(
            "Weekly Test",
            due_weekday=0,  # Monday
            creation_date=datetime.datetime(2023, 1, 9)  # Monday week 2
        )
        assert not habit.is_broken()