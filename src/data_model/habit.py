import datetime
from typing import List, Optional
import uuid

from src.data_model.completion import Completion

class BaseHabit:
    """
    Base class for all habit types, providing common functionality and attributes.

    This abstract class serves as the foundation for specific habit types (e.g., DailyHabit,
    WeeklyHabit) in the Habit Tracker CLI Application. It manages a habit's name, creation
    date, unique identifier, and a list of completion records. Subclasses must implement
    periodicity and period-specific methods.

    Attributes:
        name (str): Descriptive name of the habit (required, non-empty).
        _creation_date (datetime.datetime): When the habit was created (defaults to now).
        id (str): Unique identifier for the habit (auto-generated via UUID if not provided).
        _completion_records (List[Completion]): List of Completion objects, sorted by timestamp.

    Usage:
        - Instantiate directly or via subclasses with a name and optional parameters.
        - Use check_off() to record completions and get_completion_records() to retrieve them.
        - Serialize to JSON using to_dict() for persistence.
    """

    def __init__(
        self,
        name: str,
        creation_date: Optional[datetime.datetime] = None,
        _id: Optional[str] = None,
        completion_records: Optional[List[Completion]] = None
    ):
        """
        Initialize a BaseHabit instance.

        Args:
            name (str): The habit's name, must not be empty.
            creation_date (Optional[datetime.datetime]): The creation time. Defaults to now if None.
            _id (Optional[str]): Unique identifier. Defaults to a new UUID if None.
            completion_records (Optional[List[Completion]]): Initial completion records. Defaults to empty.

        Raises:
            ValueError: If name is empty or None.

        Notes:
            - Completion records are sorted by timestamp upon initialization.
            - The list is stored internally and copied on retrieval to prevent mutation.
        """
        if not name:
            raise ValueError("Habit name cannot be empty.")
        self.name = name
        self._creation_date = creation_date or datetime.datetime.now()
        self.id = _id or str(uuid.uuid4())
        self._completion_records: List[Completion] = []
        if completion_records:
            # Sort chronologically to ensure consistent ordering
            self._completion_records = sorted(completion_records, key=lambda c: c.timestamp)

    @property
    def creation_date(self) -> datetime.datetime:
        """
        Get the creation date of the habit.

        Returns:
            datetime.datetime: The habit's creation timestamp.

        Notes:
            - Implemented as a property to provide read-only access.
        """
        return self._creation_date

    def check_off(
        self,
        completion_time: Optional[datetime.datetime] = None,
        notes: Optional[str] = None,
        mood_score: Optional[int] = None
    ) -> Completion:
        """
        Record a new completion event for the habit.

        Args:
            completion_time (Optional[datetime.datetime]): The completion time. Defaults to now if None.
            notes (Optional[str]): User notes about the completion. Defaults to None.
            mood_score (Optional[int]): Mood rating (1-5). Defaults to None.

        Returns:
            Completion: The newly created Completion object.

        Notes:
            - Appends the new completion and re-sorts the records by timestamp.
            - Delegates validation (e.g., mood score) to the Completion class.
        """
        new_c = Completion(completion_time, notes, mood_score)
        self._completion_records.append(new_c)
        self._completion_records.sort(key=lambda c: c.timestamp)  # Maintain chronological order
        return new_c

    def get_completion_records(self) -> List[Completion]:
        """
        Retrieve a sorted copy of all completion records.

        Returns:
            List[Completion]: A new list of Completion objects, sorted by timestamp.

        Notes:
            - Returns a copy to prevent external modification of the internal list.
        """
        return list(self._completion_records)

    def reset_completions(self) -> None:
        """
        Clear all completion records, effectively breaking the habit's streak.

        Returns:
            None

        Notes:
            - Used by the break_streak_flow in UserInterface to reset progress.
        """
        self._completion_records.clear()

    def to_dict(self) -> dict:
        """
        Serialize the habit and its completions to a dictionary for JSON persistence.

        Returns:
            dict: A dictionary with id, name, creation_date (ISO format), completion_records,
                  and the habit type (class name).

        Notes:
            - Completion records are converted using their to_dict() method.
            - The type field aids deserialization to the correct subclass.
        """
        return {
            "id": self.id,
            "name": self.name,
            "creation_date": self.creation_date.isoformat(),
            "completion_records": [c.to_dict() for c in self._completion_records],
            "type": self.__class__.__name__
        }

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the habit.

        Returns:
            str: A string including the habit type, name, and creation date.

        Notes:
            - Uses strftime for a readable date format.
        """
        created = self.creation_date.strftime('%Y-%m-%d')
        return f"{self.__class__.__name__}('{self.name}', created {created})"

    def __repr__(self) -> str:
        """
        Return a detailed string representation for debugging.

        Returns:
            str: A string showing all key attributes, useful for logging or debugging.

        Notes:
            - Includes the number of completion records.
        """
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"creation_date='{self.creation_date.isoformat()}', "
            f"id='{self.id}', "
            f"records={len(self._completion_records)})"
        )

    @property
    def periodicity(self) -> str:
        """
        Get the periodicity of the habit.

        Returns:
            str: The periodicity type ('daily' or 'weekly').

        Raises:
            NotImplementedError: Must be implemented by subclasses.

        Notes:
            - Abstract property, intended for subclass specialization.
        """
        raise NotImplementedError

    def is_completed_for_period(self) -> bool:
        """
        Check if the habit has been completed for the current period.

        Returns:
            bool: True if completed for the current period, False otherwise.

        Raises:
            NotImplementedError: Must be implemented by subclasses.

        Notes:
            - Defines the period based on periodicity (e.g., day for daily, week for weekly).
        """
        raise NotImplementedError

    def is_due_and_not_completed(self) -> bool:
        """
        Check if the habit is due and has not been completed for the current period.

        Returns:
            bool: True if due and not completed, False otherwise.

        Raises:
            NotImplementedError: Must be implemented by subclasses.

        Notes:
            - Considers creation date to avoid due dates before habit creation.
        """
        raise NotImplementedError

    def is_broken(self) -> bool:
        """
        Check if the habit's streak is broken based on completion history.

        Returns:
            bool: True if the streak is broken, False otherwise.

        Raises:
            NotImplementedError: Must be implemented by subclasses.

        Notes:
            - A streak is broken if a due period is missed after a completion.
        """
        raise NotImplementedError


class DailyHabit(BaseHabit):
    """
    Habit that should be completed once per calendar day.

    Inherits from BaseHabit and implements periodicity-specific logic for daily habits.
    """

    @property
    def periodicity(self) -> str:
        """
        Get the periodicity of the habit.

        Returns:
            str: 'daily', indicating the habit's recurrence pattern.
        """
        return "daily"

    @classmethod
    def from_dict(cls, data: dict) -> "DailyHabit":
        """
        Create a DailyHabit instance from a dictionary (e.g., deserialized JSON).

        Args:
            data (dict): Dictionary with keys 'name', 'creation_date', 'id', and 'completion_records'.

        Returns:
            DailyHabit: A new DailyHabit instance populated from the dictionary.

        Raises:
            ValueError: If timestamp parsing fails.
            KeyError: If required keys are missing.

        Notes:
            - Uses Completion.from_dict for deserialization of completion records.
        """
        return cls(
            name=data["name"],
            creation_date=datetime.datetime.fromisoformat(data["creation_date"]),
            _id=data.get("id"),
            completion_records=[
                Completion.from_dict(c) for c in data.get("completion_records", [])
            ]
        )

    def is_completed_for_period(self) -> bool:
        """
        Check if the habit was completed today.

        Returns:
            bool: True if completed today, False otherwise.

        Notes:
            - Compares completion timestamps' dates with today's date.
        """
        today = datetime.date.today()
        return any(c.timestamp.date() == today for c in self._completion_records)

    def is_due_and_not_completed(self) -> bool:
        """
        Check if the habit is due today and not yet completed.

        Returns:
            bool: True if due (created before today) and not completed, False otherwise.

        Notes:
            - Considers the habit due only after its creation date.
        """
        today = datetime.date.today()
        if today < self.creation_date.date():
            return False
        return not self.is_completed_for_period()

    def is_broken(self) -> bool:
        """
        Check if the daily habit's streak is broken.

        Returns:
            bool: True if the streak is broken (e.g., missed yesterday after completion), False otherwise.

        Notes:
            - Broken if no completions exist before yesterday or if yesterday was missed after a prior completion.
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        dates = sorted({c.timestamp.date() for c in self._completion_records})

        if not dates:
            # Broken if created before yesterday and never completed
            return self.creation_date.date() <= yesterday

        last = dates[-1]
        if last < yesterday:
            return True
        if last == yesterday and not self.is_completed_for_period():
            return True
        return False


class WeeklyHabit(BaseHabit):
    """
    Habit that should be completed once per week on a specified weekday.

    Inherits from BaseHabit and implements periodicity-specific logic for weekly habits,
    with a due_weekday attribute (0-6, where 0 is Monday).
    """

    def __init__(
        self,
        name: str,
        creation_date: Optional[datetime.datetime] = None,
        due_weekday: int = 0,
        _id: Optional[str] = None,
        completion_records: Optional[List[Completion]] = None
    ):
        """
        Initialize a WeeklyHabit instance.

        Args:
            name (str): The habit's name, must not be empty.
            creation_date (Optional[datetime.datetime]): The creation time. Defaults to now if None.
            due_weekday (int): The day of week to complete (0=Mon, 6=Sun). Defaults to 0.
            _id (Optional[str]): Unique identifier. Defaults to a new UUID if None.
            completion_records (Optional[List[Completion]]): Initial completion records. Defaults to empty.

        Raises:
            ValueError: If due_weekday is not between 0 and 6.

        Notes:
            - Calls the parent constructor and validates due_weekday.
        """
        super().__init__(name, creation_date, _id, completion_records)
        if not (0 <= due_weekday <= 6):
            raise ValueError("due_weekday must be 0 (Mon) through 6 (Sun).")
        self.due_weekday = due_weekday

    @property
    def periodicity(self) -> str:
        """
        Get the periodicity of the habit.

        Returns:
            str: 'weekly', indicating the habit's recurrence pattern.
        """
        return "weekly"

    @classmethod
    def from_dict(cls, data: dict) -> "WeeklyHabit":
        """
        Create a WeeklyHabit instance from a dictionary (e.g., deserialized JSON).

        Args:
            data (dict): Dictionary with keys 'name', 'creation_date', 'id', 'due_weekday',
                        and 'completion_records'.

        Returns:
            WeeklyHabit: A new WeeklyHabit instance populated from the dictionary.

        Raises:
            ValueError: If timestamp parsing fails.
            KeyError: If required keys are missing.

        Notes:
            - Uses Completion.from_dict for deserialization of completion records.
            - Defaults due_weekday to 0 if not present.
        """
        return cls(
            name=data["name"],
            creation_date=datetime.datetime.fromisoformat(data["creation_date"]),
            due_weekday=data.get("due_weekday", 0),
            _id=data.get("id"),
            completion_records=[
                Completion.from_dict(c) for c in data.get("completion_records", [])
            ]
        )

    def is_completed_for_period(self) -> bool:
        """
        Check if the habit was completed this week.

        Returns:
            bool: True if completed in the current week, False otherwise.

        Notes:
            - Uses ISO week number and year to determine the current week.
        """
        year, week, _ = datetime.date.today().isocalendar()
        return any(c.timestamp.isocalendar()[:2] == (year, week)
                   for c in self._completion_records)

    def is_due_and_not_completed(self) -> bool:
        """
        Check if the habit is due this week and not yet completed.

        Returns:
            bool: True if due (after due weekday) and not completed, False otherwise.

        Notes:
            - Due if the current weekday is >= due_weekday, considering creation week.
        """
        today = datetime.date.today()
        creation_year, creation_week, _ = self.creation_date.isocalendar()
        current_year, current_week, weekday = today.isocalendar()

        if (current_year, current_week) < (creation_year, creation_week):
            return False

        # Due if the due weekday has passed or is today
        if weekday - 1 >= self.due_weekday:
            return not self.is_completed_for_period()
        return False

    def is_broken(self) -> bool:
        """
        Check if the weekly habit's streak is broken.

        Returns:
            bool: True if the streak is broken (e.g., missed a due week), False otherwise.

        Notes:
            - Broken if no completions exist past the first due week or if the last
              completed week is before the previous week after the due day.
        """
        today = datetime.date.today()
        current_year, current_week, weekday = today.isocalendar()
        dates = sorted({(c.timestamp.isocalendar()[0], c.timestamp.isocalendar()[1])
                        for c in self._completion_records})

        if not dates:
            # Broken if past the first due week with no completions
            first_due = (self.creation_date.isocalendar()[0], self.creation_date.isocalendar()[1])
            return (current_year, current_week) > (first_due[0], first_due[1] + 1)

        last_year, last_week = dates[-1]
        prev = (today - datetime.timedelta(weeks=1)).isocalendar()[:2]
        if (last_year, last_week) < prev:
            return True
        if (last_year, last_week) == prev and weekday - 1 >= self.due_weekday and not self.is_completed_for_period():
            return True
        return False