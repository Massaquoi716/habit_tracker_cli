import datetime
from typing import List, Optional, Dict, Tuple

from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit
from src.storage.storage_handler import StorageHandler
from src.analytics.analytics_service import AnalyticsService


class HabitManager:
    """
    Orchestrates habit operations: creation, retrieval, check‑off, deletion,
    streak resets, and analytics, persisting changes via StorageHandler.
    """

    def __init__(self, storage_handler: StorageHandler):
        self._storage = storage_handler
        # Load existing habits (empty list if no data)
        self._habits: List[BaseHabit] = self._storage.load_habits()

    def add_habit(
        self,
        habit_type: str,
        name: str,
        due_weekday: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Create and persist a new habit.

        Args:
            habit_type: 'daily' or 'weekly'
            name: unique habit name
            due_weekday: for weekly habits, 0=Mon…6=Sun

        Returns:
            (success, message)
        """
        if self.get_habit_by_name(name):
            return False, f"Habit '{name}' already exists."

        habit_type = habit_type.lower()
        try:
            if habit_type == "daily":
                habit = DailyHabit(name=name)
            elif habit_type == "weekly":
                due = due_weekday if due_weekday is not None else 0
                habit = WeeklyHabit(name=name, due_weekday=due)
            else:
                return False, "Unknown habit type. Choose 'daily' or 'weekly'."

            self._habits.append(habit)
            self._storage.save_habits(self._habits)
            return True, f"Created {habit_type} habit '{name}'."
        except Exception as e:
            return False, f"Error creating habit: {e}"

    def get_habit_by_name(self, name: str) -> Optional[BaseHabit]:
        """Case‑insensitive lookup of a habit by its name."""
        for h in self._habits:
            if h.name.lower() == name.lower():
                return h
        return None

    def get_all_habits(self) -> List[BaseHabit]:
        """Return all habits sorted alphabetically by name."""
        return sorted(self._habits, key=lambda h: h.name.lower())

    all_habits = get_all_habits  # alias for CLI convenience

    def check_off_habit(
        self,
        name: str,
        time: Optional[datetime.datetime] = None,
        notes: Optional[str] = None,
        mood_score: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Mark a habit as completed.

        Returns:
            (success, message)
        """
        habit = self.get_habit_by_name(name)
        if not habit:
            return False, f"No habit named '{name}'."
        try:
            habit.check_off(time, notes, mood_score)
            self._storage.save_habits(self._habits)
            return True, f"Checked off habit '{name}'."
        except Exception as e:
            return False, f"Error checking off: {e}"

    def delete_habit(self, name: str) -> Tuple[bool, str]:
        """
        Remove a habit entirely.

        Returns:
            (success, message)
        """
        original = len(self._habits)
        self._habits = [h for h in self._habits if h.name.lower() != name.lower()]
        if len(self._habits) < original:
            self._storage.save_habits(self._habits)
            return True, f"Deleted habit '{name}'."
        return False, f"No habit named '{name}'."

    def break_streak(self, name: str) -> Tuple[bool, str]:
        """
        Reset a habit's streak by clearing its completions.

        Returns:
            (success, message)
        """
        habit = self.get_habit_by_name(name)
        if not habit:
            return False, f"No habit named '{name}'."
        habit.reset_completions()
        self._storage.save_habits(self._habits)
        return True, f"Streak for '{name}' has been reset."

    # === Analytics Delegation ===

    def get_longest_streak_overall(self) -> Tuple[Optional[int], Optional[str]]:
        """Longest streak across all habits."""
        return AnalyticsService.get_overall_longest_streak(self._habits)

    def get_longest_streak_daily(self) -> Tuple[Optional[int], Optional[str]]:
        """Longest streak among daily habits."""
        return AnalyticsService.get_longest_streak_by_periodicity(self._habits, "daily")

    def get_longest_streak_weekly(self) -> Tuple[Optional[int], Optional[str]]:
        """Longest streak among weekly habits."""
        return AnalyticsService.get_longest_streak_by_periodicity(self._habits, "weekly")

    def get_current_streaks(self) -> Dict[str, int]:
        """Current active streaks for all habits."""
        return AnalyticsService.get_current_streaks_all_habits(self._habits)
