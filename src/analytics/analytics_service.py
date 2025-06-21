import datetime
from typing import List, Dict, Tuple, Optional
from datetime import timedelta

from src.data_model.habit import BaseHabit

class AnalyticsService:
    """
    Service for computing habit analytics using functional programming principles.
    """

    @staticmethod
    def _get_unique_periods(timestamps: List[datetime.datetime], periodicity: str) -> List[datetime.datetime]:
        seen = set()
        result = []
        for ts in sorted(timestamps):
            if periodicity == "daily":
                key = (ts.year, ts.month, ts.day)
            elif periodicity == "weekly":
                key = ts.isocalendar()[:2]
            else:
                raise ValueError("Invalid periodicity.")
            if key not in seen:
                seen.add(key)
                result.append(ts)
        return result

    @staticmethod
    def get_longest_streak(timestamps: List[datetime.datetime], periodicity: str) -> int:
        periods = AnalyticsService._get_unique_periods(timestamps, periodicity)
        if not periods:
            return 0

        longest = current = 1
        for prev, curr in zip(periods, periods[1:]):
            if periodicity == "daily":
                delta = (curr.date() - prev.date()).days
                if delta == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1  # Reset streak on gap
            else:  # weekly
                py, pw = prev.isocalendar()[:2]
                cy, cw = curr.isocalendar()[:2]
                is_next = (cy == py and cw == pw + 1) or (cy == py + 1 and pw in [52, 53] and cw == 1)
                if is_next:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1  # Reset streak on gap

        return longest

    @staticmethod
    def get_current_streak(timestamps: List[datetime.datetime], periodicity: str) -> int:
        periods = AnalyticsService._get_unique_periods(timestamps, periodicity)
        if not periods:
            return 0

        today = datetime.datetime.now()
        last = periods[-1]

        if periodicity == "daily":
            today_date = today.date()
            last_date = last.date()
            yesterday_date = today_date - timedelta(days=1)
            
            if last_date not in {today_date, yesterday_date}:
                return 0
            streak = 1
            for later, earlier in zip(periods[-1::-1], periods[-2::-1]):
                if (later.date() - earlier.date()).days != 1:
                    break
                streak += 1
        else:  # weekly
            current_year, current_week = today.isocalendar()[:2]
            last_year, last_week = last.isocalendar()[:2]
            # Only count if last completion is in the current week
            if (last_year, last_week) != (current_year, current_week):
                return 0
            streak = 1
            for later, earlier in zip(periods[-1::-1], periods[-2::-1]):
                ey, ew = earlier.isocalendar()[:2]
                ly, lw = later.isocalendar()[:2]
                is_consecutive = (ly == ey and lw == ew + 1) or (ly == ey + 1 and ew in [52, 53] and lw == 1)
                if not is_consecutive:
                    break
                streak += 1

        return streak

    @staticmethod
    def get_overall_longest_streak(habits: List[BaseHabit]) -> Tuple[int, List[Tuple[str, str]]]:
        """
        Returns:
            max_streak: int
            longest: List of (habit_name, periodicity) tuples
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
        results = {}
        for habit in habits:
            timestamps = [c.timestamp for c in habit.get_completion_records()]
            streak = AnalyticsService.get_current_streak(timestamps, habit.periodicity)
            if streak > 0:
                results[habit.name] = streak
        return results