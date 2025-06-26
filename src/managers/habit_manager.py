import datetime
from typing import List, Optional, Dict, Tuple

from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit
from src.storage.storage_handler import StorageHandler
from src.analytics.analytics_service import AnalyticsService

class HabitManager:
    """
    Orchestrates habit operations including creation, retrieval, check-off, deletion,
    streak resets, and analytics, while persisting changes via StorageHandler.

    This class acts as the central controller for habit management in the Habit Tracker
    CLI Application. It interacts with StorageHandler for data persistence (e.g., to
    `data/habits.json`) and delegates analytics to AnalyticsService. It maintains a list
    of BaseHabit instances (including DailyHabit and WeeklyHabit) and provides methods
    to manipulate and analyze them.

    Attributes:
        _storage (StorageHandler): The storage handler for loading/saving habits.
        _habits (List[BaseHabit]): The in-memory list of habit instances.

    Usage:
        - Initialize with a StorageHandler instance.
        - Use methods like add_habit(), check_off_habit(), and get_longest_streak_overall()
          to manage and analyze habits.
    """

    def __init__(self, storage_handler: StorageHandler):
        """
        Initialize the HabitManager with a storage handler.

        Args:
            storage_handler (StorageHandler): The instance to handle habit persistence.

        Raises:
            ValueError: If storage_handler is None.

        Notes:
            - Loads existing habits from storage on initialization (empty list if no data).
        """
        if storage_handler is None:
            raise ValueError("StorageHandler instance cannot be None.")
        self._storage = storage_handler
        # Load existing habits from storage, default to empty list if none
        self._habits: List[BaseHabit] = self._storage.load_habits()

    def add_habit(
        self,
        habit_type: str,
        name: str,
        due_weekday: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Create and persist a new habit of the specified type.

        Args:
            habit_type (str): The type of habit, 'daily' or 'weekly' (case-insensitive).
            name (str): The unique name of the habit.
            due_weekday (Optional[int]): The due day for weekly habits (0=Mon, 6=Sun).
                Defaults to None (ignored for daily habits).

        Returns:
            Tuple[bool, str]: A tuple (success_flag, message) indicating the operation's
                success and a descriptive message.

        Raises:
            ValueError: If habit_type is invalid or due_weekday is out of range (via WeeklyHabit).

        Notes:
            - Checks for duplicate names (case-insensitive).
            - Persists the new habit to storage on success.
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
        """
        Retrieve a habit by its name with case-insensitive matching.

        Args:
            name (str): The name of the habit to find.

        Returns:
            Optional[BaseHabit]: The matching habit instance, or None if not found.
        """
        for h in self._habits:
            if h.name.lower() == name.lower():
                return h
        return None

    def get_all_habits(self) -> List[BaseHabit]:
        """
        Retrieve all habits, sorted alphabetically by name.

        Returns:
            List[BaseHabit]: A sorted list of all habit instances.

        Notes:
            - Sorting is case-insensitive for user-friendly display.
        """
        return sorted(self._habits, key=lambda h: h.name.lower())

    all_habits = get_all_habits  # Alias for CLI convenience, no additional documentation needed

    def check_off_habit(
        self,
        name: str,
        time: Optional[datetime.datetime] = None,
        notes: Optional[str] = None,
        mood_score: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Mark a habit as completed with optional details.

        Args:
            name (str): The name of the habit to check off.
            time (Optional[datetime.datetime]): The completion time. Defaults to now if None.
            notes (Optional[str]): User notes about the completion. Defaults to None.
            mood_score (Optional[int]): Mood rating (1-5). Defaults to None.

        Returns:
            Tuple[bool, str]: A tuple (success_flag, message) indicating the operation's
                success and a descriptive message.

        Raises:
            ValueError: If mood_score is invalid (via Completion).

        Notes:
            - Persists the updated habit list to storage on success.
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
        Remove a habit from the manager and persist the change.

        Args:
            name (str): The name of the habit to delete.

        Returns:
            Tuple[bool, str]: A tuple (success_flag, message) indicating the operation's
                success and a descriptive message.

        Notes:
            - Uses list comprehension to filter out the habit (case-insensitive).
            - Persists the updated list to storage on success.
        """
        original = len(self._habits)
        self._habits = [h for h in self._habits if h.name.lower() != name.lower()]
        if len(self._habits) < original:
            self._storage.save_habits(self._habits)
            return True, f"Deleted habit '{name}'."
        return False, f"No habit named '{name}'."

    def break_streak(self, name: str) -> Tuple[bool, str]:
        """
        Reset a habit's streak by clearing its completions and persist the change.

        Args:
            name (str): The name of the habit to reset.

        Returns:
            Tuple[bool, str]: A tuple (success_flag, message) indicating the operation's
                success and a descriptive message.

        Notes:
            - Persists the updated habit list to storage on success.
        """
        habit = self.get_habit_by_name(name)
        if not habit:
            return False, f"No habit named '{name}'."
        habit.reset_completions()
        self._storage.save_habits(self._habits)
        return True, f"Streak for '{name}' has been reset."

    # === Analytics Delegation ===

    def get_longest_streak_overall(self) -> Tuple[Optional[int], Optional[List[Tuple[str, str]]]]:
        """
        Retrieve the longest streak across all habits.

        Returns:
            Tuple[Optional[int], Optional[List[Tuple[str, str]]]]: A tuple containing the
                maximum streak length and a list of (habit_name, periodicity) tuples for
                habits with that streak, or (None, None) if no habits.

        Notes:
            - Delegates to AnalyticsService.get_overall_longest_streak.
        """
        return AnalyticsService.get_overall_longest_streak(self._habits)

    def get_longest_streak_daily(self) -> Tuple[Optional[int], Optional[List[str]]]:
        """
        Retrieve the longest streak among daily habits.

        Returns:
            Tuple[Optional[int], Optional[List[str]]]: A tuple containing the maximum streak
                length and a list of habit names with that streak, or (None, None) if no
                daily habits.

        Notes:
            - Delegates to AnalyticsService.get_longest_streak_by_periodicity with "daily".
        """
        return AnalyticsService.get_longest_streak_by_periodicity(self._habits, "daily")

    def get_longest_streak_weekly(self) -> Tuple[Optional[int], Optional[List[str]]]:
        """
        Retrieve the longest streak among weekly habits.

        Returns:
            Tuple[Optional[int], Optional[List[str]]]: A tuple containing the maximum streak
                length and a list of habit names with that streak, or (None, None) if no
                weekly habits.

        Notes:
            - Delegates to AnalyticsService.get_longest_streak_by_periodicity with "weekly".
        """
        return AnalyticsService.get_longest_streak_by_periodicity(self._habits, "weekly")

    def get_current_streaks(self) -> Dict[str, int]:
        """
        Retrieve current active streaks for all habits.

        Returns:
            Dict[str, int]: A dictionary mapping habit names to their current streak lengths.

        Notes:
            - Delegates to AnalyticsService.get_current_streaks_all_habits.
            - Only includes habits with active streaks (> 0).
        """
        return AnalyticsService.get_current_streaks_all_habits(self._habits)