import datetime
from typing import List, Dict, Tuple, Optional
from datetime import timedelta

from src.data_model.habit import BaseHabit

class AnalyticsService:
    """
    A service class for computing habit analytics using functional programming principles.
    This class provides static methods to calculate streaks (longest and current) for habits
    based on their completion timestamps, supporting both daily and weekly periodicities.
    All methods are stateless and immutable, adhering to functional programming paradigms.

    Attributes:
        None (static methods only, no class-level state).

    Usage:
        - Import and call static methods with appropriate habit data (e.g., timestamps, periodicity).
        - Designed to work with BaseHabit instances from src.data_model.habit.
    """

    @staticmethod
    def _get_unique_periods(timestamps: List[datetime.datetime], periodicity: str) -> List[datetime.datetime]:
        """
        Extract unique periods from a list of timestamps based on the specified periodicity.

        Args:
            timestamps (List[datetime.datetime]): List of completion timestamps.
            periodicity (str): Type of periodicity, either "daily" or "weekly".

        Returns:
            List[datetime.datetime]: List of unique period start times, sorted chronologically.

        Raises:
            ValueError: If an invalid periodicity is provided.

        Notes:
            - For "daily", uniqueness is based on (year, month, day).
            - For "weekly", uniqueness is based on (year, week number) using ISO calendar.
        """
        seen = set()
        result = []
        for ts in sorted(timestamps):
            if periodicity == "daily":
                key = (ts.year, ts.month, ts.day)
            elif periodicity == "weekly":
                key = ts.isocalendar()[:2]  # (year, week)
            else:
                raise ValueError(f"Invalid periodicity: {periodicity}. Use 'daily' or 'weekly'.")
            if key not in seen:
                seen.add(key)
                result.append(ts)
        return result

    @staticmethod
    def get_longest_streak(timestamps: List[datetime.datetime], periodicity: str) -> int:
        """
        Calculate the longest consecutive streak of completions based on periodicity.

        Args:
            timestamps (List[datetime.datetime]): List of completion timestamps.
            periodicity (str): Type of periodicity, either "daily" or "weekly".

        Returns:
            int: The length of the longest streak (0 if no timestamps).

        Notes:
            - For "daily", a streak breaks if there’s a gap of more than 1 day.
            - For "weekly", a streak breaks if weeks are not consecutive (handling year-end transitions).
            - Uses _get_unique_periods to process timestamps.
        """
        periods = AnalyticsService._get_unique_periods(timestamps, periodicity)
        if not periods:
            return 0

        longest = current = 1
        for prev, curr in zip(periods, periods[1:]):
            if periodicity == "daily":
                delta = (curr.date() - prev.date()).days
                if delta == 1:  # Consecutive days
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1  # Reset on gap
            else:  # weekly
                py, pw = prev.isocalendar()[:2]  # Previous year, week
                cy, cw = curr.isocalendar()[:2]  # Current year, week
                is_next = (cy == py and cw == pw + 1) or (cy == py + 1 and pw in [52, 53] and cw == 1)
                if is_next:  # Consecutive weeks (handling year-end)
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1  # Reset on gap
        return longest

    @staticmethod
    def get_current_streak(timestamps: List[datetime.datetime], periodicity: str) -> int:
        """
        Calculate the current streak of completions up to today based on periodicity.

        Args:
            timestamps (List[datetime.datetime]): List of completion timestamps.
            periodicity (str): Type of periodicity, either "daily" or "weekly".

        Returns:
            int: The length of the current streak (0 if no recent completions).

        Notes:
            - For "daily", checks if the last completion is today or yesterday.
            - For "weekly", checks if the last completion is in the current week.
            - Builds the streak backward from the most recent completion.
        """
        periods = AnalyticsService._get_unique_periods(timestamps, periodicity)
        if not periods:
            return 0

        today = datetime.datetime.now()
        last = periods[-1]

        if periodicity == "daily":
            today_date = today.date()
            last_date = last.date()
            yesterday_date = today_date - timedelta(days=1)
            
            if last_date not in {today_date, yesterday_date}:  # Not today or yesterday
                return 0
            streak = 1
            for later, earlier in zip(periods[-1::-1], periods[-2::-1]):
                if (later.date() - earlier.date()).days != 1:  # Gap detected
                    break
                streak += 1
        else:  # weekly
            current_year, current_week = today.isocalendar()[:2]
            last_year, last_week = last.isocalendar()[:2]
            if (last_year, last_week) != (current_year, current_week):  # Not current week
                return 0
            streak = 1
            for later, earlier in zip(periods[-1::-1], periods[-2::-1]):
                ey, ew = earlier.isocalendar()[:2]
                ly, lw = later.isocalendar()[:2]
                is_consecutive = (ly == ey and lw == ew + 1) or (ly == ey + 1 and ew in [52, 53] and lw == 1)
                if not is_consecutive:  # Gap detected
                    break
                streak += 1

        return streak

    @staticmethod
    def get_overall_longest_streak(habits: List[BaseHabit]) -> Tuple[int, List[Tuple[str, str]]]:
        """
        Determine the longest streak across all habits, with tied habits identified.

        Args:
            habits (List[BaseHabit]): List of habit instances to analyze.

        Returns:
            Tuple[int, List[Tuple[str, str]]]: A tuple containing the maximum streak length
                and a list of (habit_name, periodicity) tuples for habits with that streak.

        Notes:
            - Compares longest streaks for all habits and returns ties.
            - Uses get_longest_streak internally.
        """
        max_streak = 0
        longest: List[Tuple[str, str]] = []

        for habit in habits:
            times = [c.timestamp for c in habit.get_completion_records()]
            streak = AnalyticsService.get_longest_streak(times, habit.periodicity)
            if streak > max_streak:
                max_streak = streak
                longest = [(habit.name, habit.periodicity)]
            elif streak == max_streak:
                longest.append((habit.name, habit.periodicity))

        return max_streak, longest

    @staticmethod
    def get_longest_streak_by_periodicity(habits: List[BaseHabit], periodicity: str) -> Tuple[int, List[str]]:
        """
        Find the longest streak among habits of a specific periodicity.

        Args:
            habits (List[BaseHabit]): List of habit instances to analyze.
            periodicity (str): The periodicity to filter by ("daily" or "weekly").

        Returns:
            Tuple[int, List[str]]: A tuple containing the maximum streak length
                and a list of habit names with that streak.

        Notes:
            - Filters habits by the specified periodicity before calculation.
            - Uses get_longest_streak internally.
        """
        max_streak = 0
        longest = []

        for habit in habits:
            if habit.periodicity != periodicity:
                continue
            timestamps = [c.timestamp for c in habit.get_completion_records()]
            streak = AnalyticsService.get_longest_streak(timestamps, periodicity)
            if streak > max_streak:
                max_streak = streak
                longest = [habit.name]
            elif streak == max_streak:
                longest.append(habit.name)

        return max_streak, longest

    @staticmethod
    def get_current_streaks_all_habits(habits: List[BaseHabit]) -> Dict[str, int]:
        """
        Compute the current streak for all habits with active streaks.

        Args:
            habits (List[BaseHabit]): List of habit instances to analyze.

        Returns:
            Dict[str, int]: A dictionary mapping habit names to their current streak lengths.

        Notes:
            - Only includes habits with a current streak > 0.
            - Uses get_current_streak internally.
        """
        results = {}
        for habit in habits:
            timestamps = [c.timestamp for c in habit.get_completion_records()]
            streak = AnalyticsService.get_current_streak(timestamps, habit.periodicity)
            if streak > 0:
                results[habit.name] = streak
        return results