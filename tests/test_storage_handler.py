import pytest
import datetime
from pathlib import Path
from src.storage.storage_handler import StorageHandler
from src.data_model.habit import DailyHabit, WeeklyHabit
from src.data_model.completion import Completion

@pytest.fixture
def storage_handler(tmp_path):
    """Fixture for a temporary StorageHandler."""
    file_path = tmp_path / "habits.json"
    return StorageHandler(file_path=str(file_path))

def test_save_and_load_empty(storage_handler):
    """Test saving and loading an empty list of habits."""
    storage_handler.save_habits([])
    habits = storage_handler.load_habits()
    assert habits == []

def test_save_and_load_daily_habit(storage_handler):
    """Test saving and loading a daily habit with completions."""
    habit = DailyHabit("Exercise")
    habit.check_off(
        completion_time=datetime.datetime(2023, 1, 1),
        notes="Great workout",
        mood_score=4
    )
    storage_handler.save_habits([habit])
    loaded = storage_handler.load_habits()
    
    assert len(loaded) == 1
    assert loaded[0].name == "Exercise"
    assert isinstance(loaded[0], DailyHabit)
    assert loaded[0].id == habit.id
    assert len(loaded[0].get_completion_records()) == 1
    completion = loaded[0].get_completion_records()[0]
    assert completion.notes == "Great workout"
    assert completion.mood_score == 4
    assert completion.timestamp.date() == datetime.date(2023, 1, 1)

def test_save_and_load_weekly_habit(storage_handler):
    """Test saving and loading a weekly habit with completions."""
    habit = WeeklyHabit("Read", due_weekday=2)
    habit.check_off(
        completion_time=datetime.datetime(2023, 1, 4),  # Wednesday
        notes="Finished a chapter",
        mood_score=5
    )
    storage_handler.save_habits([habit])
    loaded = storage_handler.load_habits()
    
    assert len(loaded) == 1
    assert loaded[0].name == "Read"
    assert isinstance(loaded[0], WeeklyHabit)
    assert loaded[0].due_weekday == 2
    assert loaded[0].id == habit.id
    assert len(loaded[0].get_completion_records()) == 1
    completion = loaded[0].get_completion_records()[0]
    assert completion.notes == "Finished a chapter"
    assert completion.mood_score == 5
    assert completion.timestamp.date() == datetime.date(2023, 1, 4)

def test_load_nonexistent_file(storage_handler):
    """Test loading from a nonexistent file returns empty list."""
    file_path = Path(storage_handler._file_path)
    if file_path.exists():
        file_path.unlink()
    habits = storage_handler.load_habits()
    assert habits == []

def test_load_corrupted_file(storage_handler):
    """Test loading a corrupted JSON file returns empty list."""
    file_path = Path(storage_handler._file_path)
    file_path.write_text("{invalid json")
    habits = storage_handler.load_habits()
    assert habits == []

def test_save_and_load_multiple_habits(storage_handler):
    """Test saving and loading multiple habits."""
    habits = [
        DailyHabit("Exercise"),
        WeeklyHabit("Read", due_weekday=1),
        DailyHabit("Meditate")
    ]
    habits[0].check_off(datetime.datetime(2023, 1, 1))
    habits[1].check_off(datetime.datetime(2023, 1, 3))
    storage_handler.save_habits(habits)
    loaded = storage_handler.load_habits()
    
    assert len(loaded) == 3
    assert {h.name for h in loaded} == {"Exercise", "Read", "Meditate"}
    assert len([h for h in loaded if isinstance(h, DailyHabit)]) == 2
    assert len([h for h in loaded if isinstance(h, WeeklyHabit)]) == 1
    assert any(h.name == "Exercise" and len(h.get_completion_records()) == 1 for h in loaded)

def test_invalid_habit_data(storage_handler):
    """Test loading invalid habit data skips bad entries."""
    invalid_data = [
        {"type": "UnknownHabit", "name": "Invalid", "creation_date": "2023-01-01T00:00:00"},
        {"type": "DailyHabit", "name": "Exercise", "creation_date": "2023-01-01T00:00:00"}
    ]
    with storage_handler._file_path.open("w", encoding="utf-8") as f:
        import json
        json.dump(invalid_data, f)
    loaded = storage_handler.load_habits()
    assert len(loaded) == 1
    assert loaded[0].name == "Exercise"
    assert isinstance(loaded[0], DailyHabit)