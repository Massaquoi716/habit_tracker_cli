import pytest
from unittest.mock import patch, Mock
from io import StringIO
import datetime
import questionary
from freezegun import freeze_time
from src.cli.user_interface import UserInterface
from src.managers.habit_manager import HabitManager
from src.storage.storage_handler import StorageHandler
from src.data_model.habit import DailyHabit, WeeklyHabit

@pytest.fixture
def storage_handler(tmp_path):
    """Fixture for a temporary StorageHandler."""
    file_path = tmp_path / "habits.json"
    return StorageHandler(file_path=str(file_path))

@pytest.fixture
def habit_manager(storage_handler):
    """Fixture for a HabitManager with a storage handler."""
    return HabitManager(storage_handler)

@pytest.fixture
def ui(habit_manager):
    """Fixture for a UserInterface instance."""
    return UserInterface(habit_manager)

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_add_habit_flow_daily(mock_stdout, ui):
    """Test adding a daily habit through the CLI."""
    with patch("questionary.text") as mock_text, patch("questionary.select") as mock_select:
        mock_text.return_value.ask.return_value = "Exercise"
        mock_select.return_value.ask.return_value = "daily"
        
        ui.add_habit_flow()
        
        output = mock_stdout.getvalue()
        assert "✅ Created daily habit 'Exercise'." in output
        habit = ui.manager.get_habit_by_name("Exercise")
        assert habit is not None
        assert isinstance(habit, DailyHabit)

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_add_habit_flow_weekly(mock_stdout, ui):
    """Test adding a weekly habit through the CLI."""
    with patch("questionary.text") as mock_text, patch("questionary.select") as mock_select:
        mock_text.return_value.ask.return_value = "Read"
        # Mock two select calls: habit type and weekday
        select1 = Mock()
        select1.ask.return_value = "weekly"
        select2 = Mock()
        select2.ask.return_value = "Wednesday"
        mock_select.side_effect = [select1, select2]
        
        ui.add_habit_flow()
        
        output = mock_stdout.getvalue()
        assert "✅ Created weekly habit 'Read'." in output
        habit = ui.manager.get_habit_by_name("Read")
        assert habit is not None
        assert isinstance(habit, WeeklyHabit)
        assert habit.due_weekday == 2

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_add_habit_flow_duplicate(mock_stdout, ui):
    """Test adding a duplicate habit name."""
    ui.manager.add_habit("daily", "Exercise")
    with patch("questionary.text") as mock_text, patch("questionary.select") as mock_select:
        mock_text.return_value.ask.return_value = "Exercise"
        mock_select.return_value.ask.return_value = "daily"
        
        ui.add_habit_flow()
        
        output = mock_stdout.getvalue()
        assert "❌ Habit 'Exercise' already exists." in output

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_check_off_flow(mock_stdout, ui):
    """Test checking off a habit through the CLI."""
    ui.manager.add_habit("daily", "Exercise")
    with patch("questionary.select") as mock_select, patch("questionary.text") as mock_text:
        # Mock two select calls: habit name and mood score
        select1 = Mock()
        select1.ask.return_value = "Exercise"
        select2 = Mock()
        select2.ask.return_value = "4"
        mock_select.side_effect = [select1, select2]
        mock_text.return_value.ask.return_value = "Great workout"
        
        ui.check_off_flow()
        
        output = mock_stdout.getvalue()
        assert "✅ Checked off habit 'Exercise'." in output
        habit = ui.manager.get_habit_by_name("Exercise")
        assert len(habit.get_completion_records()) == 1
        completion = habit.get_completion_records()[0]
        assert completion.notes == "Great workout"
        assert completion.mood_score == 4

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_check_off_flow_no_habits(mock_stdout, ui):
    """Test checking off when no habits exist."""
    ui.check_off_flow()
    
    output = mock_stdout.getvalue()
    assert "⚠️ No habits found." in output

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_view_habits(mock_stdout, ui):
    """Test viewing all habits."""
    ui.manager.add_habit("daily", "Exercise")
    ui.manager.add_habit("weekly", "Read", due_weekday=1)
    
    ui.view_habits()
    
    output = mock_stdout.getvalue()
    assert "- DailyHabit('Exercise', created 2023-01-10)" in output
    assert "- WeeklyHabit('Read', created 2023-01-10)" in output

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_view_habits_empty(mock_stdout, ui):
    """Test viewing habits when none exist."""
    ui.view_habits()
    
    output = mock_stdout.getvalue()
    assert "⚠️ No habits to show." in output

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_view_streaks(mock_stdout, ui):
    """Test viewing streaks."""
    ui.manager.add_habit("daily", "Exercise")
    ui.manager.add_habit("weekly", "Read", due_weekday=1)
    ui.manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 8))
    ui.manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 9))
    ui.manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 10))
    ui.manager.check_off_habit("Read", datetime.datetime(2023, 1, 2))
    ui.manager.check_off_habit("Read", datetime.datetime(2023, 1, 9))
    
    ui.view_streaks()
    
    output = mock_stdout.getvalue()
    assert "📊 Longest Streak (Any): Exercise (3 days)" in output
    assert "📊 Longest Daily:        Exercise (3 days)" in output
    assert "📊 Longest Weekly:       Read (2 weeks)" in output
    assert "🔥 Current Streaks:" in output
    assert "Exercise: 3" in output
    assert "Read: 2" in output

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_delete_habit_flow(mock_stdout, ui):
    """Test deleting a habit through the CLI."""
    ui.manager.add_habit("daily", "Exercise")
    with patch("questionary.select") as mock_select, patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "Exercise"
        mock_confirm.return_value.ask.return_value = True
        
        ui.delete_habit_flow()
        
        output = mock_stdout.getvalue()
        assert "🗑️ Deleted habit 'Exercise'." in output
        assert ui.manager.get_habit_by_name("Exercise") is None

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_delete_habit_no_confirm(mock_stdout, ui):
    """Test deleting a habit without confirmation."""
    ui.manager.add_habit("daily", "Exercise")
    with patch("questionary.select") as mock_select, patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "Exercise"
        mock_confirm.return_value.ask.return_value = False
        
        ui.delete_habit_flow()
        
        output = mock_stdout.getvalue()
        assert "🗑️ Deleted habit 'Exercise'." not in output
        assert ui.manager.get_habit_by_name("Exercise") is not None

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_break_streak_flow(mock_stdout, ui):
    """Test breaking a habit's streak through the CLI."""
    ui.manager.add_habit("daily", "Exercise")
    ui.manager.check_off_habit("Exercise", datetime.datetime(2023, 1, 9))
    with patch("questionary.select") as mock_select, patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "Exercise"
        mock_confirm.return_value.ask.return_value = True
        
        ui.break_streak_flow()
        
        output = mock_stdout.getvalue()
        assert "🧨 Streak for 'Exercise' has been reset." in output
        habit = ui.manager.get_habit_by_name("Exercise")
        assert len(habit.get_completion_records()) == 0

@freeze_time("2023-01-10")
@patch("sys.stdout", new_callable=StringIO)
def test_exit(mock_stdout, ui):
    """Test exiting the CLI."""
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "🚪 Exit"
        
        ui.start()
        
        output = mock_stdout.getvalue()
        assert "👋 Goodbye!" in output