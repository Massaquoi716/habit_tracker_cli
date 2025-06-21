import pytest
import datetime
from freezegun import freeze_time
from unittest.mock import Mock
from src.managers.habit_manager import HabitManager
from src.storage.storage_handler import StorageHandler
from src.data_model.habit import DailyHabit, WeeklyHabit
from src.data_model.completion import Completion

@pytest.fixture
def storage_handler(tmp_path):
    """Fixture for a temporary StorageHandler."""
    file_path = tmp_path / "habits.json"
    return StorageHandler(file_path=str(file_path))

@pytest.fixture
def habit_manager(storage_handler):
    """Fixture for a HabitManager with a storage handler."""
    return HabitManager(storage_handler)

@freeze_time("2023-01-10")
def test_add_habit_daily(habit_manager, storage_handler):
    """Test adding a daily habit."""
    success, message = habit_manager.add_habit("daily", "Exercise")
    assert success
    assert message == "Created daily habit 'Exercise'."
    assert len(habit_manager.get_all_habits()) == 1
    assert isinstance(habit_manager.get_habit_by_name("Exercise"), DailyHabit)
    assert storage_handler.load_habits()[0].name == "Exercise"

@freeze_time("2023-01-10")
def test_add_habit_weekly(habit_manager, storage_handler):
    """Test adding a weekly habit with a specific due weekday."""
    success, message = habit_manager.add_habit("weekly", "Read", due_weekday=2)  # Wednesday
    assert success
    assert message == "Created weekly habit 'Read'."
    assert len(habit_manager.get_all_habits()) == 1
    assert isinstance(habit_manager.get_habit_by_name("Read"), WeeklyHabit)
    assert storage_handler.load_habits()[0].due_weekday == 2

def test_add_habit_duplicate(habit_manager):
    """Test adding a duplicate habit fails."""
    habit_manager.add_habit("daily", "Exercise")
    success, message = habit_manager.add_habit("daily", "Exercise")
    assert not success
    assert message == "Habit 'Exercise' already exists."
    assert len(habit_manager.get_all_habits()) == 1

def test_add_habit_invalid_type(habit_manager):
    """Test adding a habit with invalid type fails."""
    success, message = habit_manager.add_habit("monthly", "Invalid")
    assert not success
    assert message == "Unknown habit type. Choose 'daily' or 'weekly'."

@freeze_time("2023-01-10")
def test_check_off_habit(habit_manager, storage_handler):
    """Test checking off a habit."""
    habit_manager.add_habit("daily", "Exercise")
    success, message = habit_manager.check_off_habit("Exercise", notes="Great workout", mood_score=4)
    assert success
    assert message == "Checked off habit 'Exercise'."
    habit = habit_manager.get_habit_by_name("Exercise")
    assert len(habit.get_completion_records()) == 1
    completion = habit.get_completion_records()[0]
    assert completion.notes == "Great workout"
    assert completion.mood_score == 4
    assert completion.timestamp.date() == datetime.date(2023, 1, 10)
    saved_habits = storage_handler.load_habits()
    assert len(saved_habits[0].get_completion_records()) == 1

def test_check_off_nonexistent_habit(habit_manager):
    """Test checking off a nonexistent habit fails."""
    success, message = habit_manager.check_off_habit("Nonexistent")
    assert not success
    assert message == "No habit named 'Nonexistent'."

@freeze_time("2023-01-10")
def test_delete_habit(habit_manager, storage_handler):
    """Test deleting a habit."""
    habit_manager.add_habit("daily", "Exercise")
    success, message = habit_manager.delete_habit("Exercise")
    assert success
    assert message == "Deleted habit 'Exercise'."
    assert len(habit_manager.get_all_habits()) == 0
    assert len(storage_handler.load_habits()) == 0

def test_delete_nonexistent_habit(habit_manager):
    """Test deleting a nonexistent habit fails."""
    success, message = habit_manager.delete_habit("Nonexistent")
    assert not success
    assert message == "No habit named 'Nonexistent'."

@freeze_time("2023-01-10")
def test_break_streak(habit_manager, storage_handler):
    """Test breaking a habit's streak."""
    habit_manager.add_habit("daily", "Exercise")
    habit_manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 9))
    habit_manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 10))
    success, message = habit_manager.break_streak("Exercise")
    assert success
    assert message == "Streak for 'Exercise' has been reset."
    habit = habit_manager.get_habit_by_name("Exercise")
    assert len(habit.get_completion_records()) == 0
    assert len(storage_handler.load_habits()[0].get_completion_records()) == 0

def test_break_streak_nonexistent(habit_manager):
    """Test breaking streak for nonexistent habit fails."""
    success, message = habit_manager.break_streak("Nonexistent")
    assert not success
    assert message == "No habit named 'Nonexistent'."

@freeze_time("2023-01-10")
def test_get_all_habits_sorted(habit_manager):
    """Test getting all habits sorted alphabetically."""
    habit_manager.add_habit("daily", "Zumba")
    habit_manager.add_habit("weekly", "Aerobics")
    habit_manager.add_habit("daily", "Meditation")
    habits = habit_manager.get_all_habits()
    assert len(habits) == 3
    assert [h.name for h in habits] == ["Aerobics", "Meditation", "Zumba"]

def test_all_habits_alias(habit_manager):
    """Test that all_habits is an alias for get_all_habits."""
    habit_manager.add_habit("daily", "Exercise")
    assert habit_manager.all_habits() == habit_manager.get_all_habits()

@freeze_time("2023-01-10")
def test_analytics_delegation(habit_manager):
    """Test analytics methods delegate correctly."""
    habit_manager.add_habit("daily", "Exercise")
    habit_manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 1))
    habit_manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 2))
    habit_manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 3))
    
    max_streak, longest = habit_manager.get_longest_streak_overall()
    assert max_streak == 3
    assert ("Exercise", "daily") in longest
    
    max_streak, longest = habit_manager.get_longest_streak_daily()
    assert max_streak == 3
    assert "Exercise" in longest
    
    max_streak, longest = habit_manager.get_longest_streak_weekly()
    assert max_streak == 0
    assert longest == []
    
    current_streaks = habit_manager.get_current_streaks()
    assert current_streaks == {}  # Not current, as last check-off is Jan 3