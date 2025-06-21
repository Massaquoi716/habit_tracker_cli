# src/data_model/habit.py

import datetime
from typing import List, Optional
import uuid

from src.data_model.completion import Completion


class BaseHabit:
    """
    Base class for all habit types.

    Attributes:
        name (str): Descriptive name of the habit.
        _creation_date (datetime.datetime): When the habit was created.
        id (str): Unique identifier for the habit.
        _completion_records (List[Completion]): List of completion events.
    """

    def __init__(
        self,
        name: str,
        creation_date: Optional[datetime.datetime] = None,
        _id: Optional[str] = None,
        completion_records: Optional[List[Completion]] = None
    ):
        if not name:
            raise ValueError("Habit name cannot be empty.")
        self.name = name
        self._creation_date = creation_date or datetime.datetime.now()
        self.id = _id or str(uuid.uuid4())
        self._completion_records: List[Completion] = []
        if completion_records:
            # Ensure records are sorted chronologically
            self._completion_records = sorted(completion_records, key=lambda c: c.timestamp)

    @property
    def creation_date(self) -> datetime.datetime:
        """Returns the creation date of the habit."""
        return self._creation_date

    def check_off(
        self,
        completion_time: Optional[datetime.datetime] = None,
        notes: Optional[str] = None,
        mood_score: Optional[int] = None
    ) -> Completion:
        """
        Records a new completion event.

        Returns:
            The new Completion object.
        """
        new_c = Completion(completion_time, notes, mood_score)
        self._completion_records.append(new_c)
        self._completion_records.sort(key=lambda c: c.timestamp)
        return new_c

    def get_completion_records(self) -> List[Completion]:
        """
        Returns a sorted copy of completion records
        to avoid external mutation.
        """
        return list(self._completion_records)

    def reset_completions(self) -> None:
        """
        Clears all completion records (used to break a streak).
        """
        self._completion_records.clear()

    def to_dict(self) -> dict:
        """
        Serializes the habit (and its completions) to a dict for JSON.
        """
        return {
            "id": self.id,
            "name": self.name,
            "creation_date": self.creation_date.isoformat(),
            "completion_records": [c.to_dict() for c in self._completion_records],
            "type": self.__class__.__name__
        }

    def __str__(self) -> str:
        created = self.creation_date.strftime('%Y-%m-%d')
        return f"{self.__class__.__name__}('{self.name}', created {created})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"creation_date='{self.creation_date.isoformat()}', "
            f"id='{self.id}', "
            f"records={len(self._completion_records)})"
        )

    @property
    def periodicity(self) -> str:
        """Must be implemented by subclasses: 'daily' or 'weekly'."""
        raise NotImplementedError

    def is_completed_for_period(self) -> bool:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def is_due_and_not_completed(self) -> bool:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def is_broken(self) -> bool:
        """Must be implemented by subclasses."""
        raise NotImplementedError


class DailyHabit(BaseHabit):
    """Habit that should be done once per calendar day."""

    @property
    def periodicity(self) -> str:
        return "daily"

    @classmethod
    def from_dict(cls, data: dict) -> "DailyHabit":
        return cls(
            name=data["name"],
            creation_date=datetime.datetime.fromisoformat(data["creation_date"]),
            _id=data.get("id"),
            completion_records=[
                Completion.from_dict(c) for c in data.get("completion_records", [])
            ]
        )

    def is_completed_for_period(self) -> bool:
        today = datetime.date.today()
        return any(c.timestamp.date() == today for c in self._completion_records)

    def is_due_and_not_completed(self) -> bool:
        today = datetime.date.today()
        if today < self.creation_date.date():
            return False
        return not self.is_completed_for_period()

    def is_broken(self) -> bool:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        dates = sorted({c.timestamp.date() for c in self._completion_records})

        if not dates:
            # If created before yesterday and never done => broken
            return self.creation_date.date() <= yesterday

        last = dates[-1]
        if last < yesterday:
            return True
        if last == yesterday and not self.is_completed_for_period():
            return True
        return False


class WeeklyHabit(BaseHabit):
    """Habit that should be done once per week on a specified weekday."""

    def __init__(
        self,
        name: str,
        creation_date: Optional[datetime.datetime] = None,
        due_weekday: int = 0,
        _id: Optional[str] = None,
        completion_records: Optional[List[Completion]] = None
    ):
        super().__init__(name, creation_date, _id, completion_records)
        if not (0 <= due_weekday <= 6):
            raise ValueError("due_weekday must be 0 (Mon) through 6 (Sun).")
        self.due_weekday = due_weekday

    @property
    def periodicity(self) -> str:
        return "weekly"

    @classmethod
    def from_dict(cls, data: dict) -> "WeeklyHabit":
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
        year, week, _ = datetime.date.today().isocalendar()
        return any(c.timestamp.isocalendar()[:2] == (year, week)
                   for c in self._completion_records)

    def is_due_and_not_completed(self) -> bool:
        today = datetime.date.today()
        creation_year, creation_week, _ = self.creation_date.isocalendar()
        current_year, current_week, weekday = today.isocalendar()

        if (current_year, current_week) < (creation_year, creation_week):
            return False

        # If the due weekday has passed or is today, and not completed this week
        if weekday - 1 >= self.due_weekday:
            return not self.is_completed_for_period()
        return False

    def is_broken(self) -> bool:
        today = datetime.date.today()
        current_year, current_week, weekday = today.isocalendar()
        dates = sorted({(c.timestamp.isocalendar()[0], c.timestamp.isocalendar()[1])
                        for c in self._completion_records})

        if not dates:
            # If past the first due week with no completions, broken
            first_due = (self.creation_date.isocalendar()[0], self.creation_date.isocalendar()[1])
            return (current_year, current_week) > (first_due[0], first_due[1] + 1)

        last_year, last_week = dates[-1]
        # If last completed week is before the immediately preceding week => broken
        prev = (today - datetime.timedelta(weeks=1)).isocalendar()[:2]
        if (last_year, last_week) < prev:
            return True
        # If last week was prev week but not done this week after due day => broken
        if (last_year, last_week) == prev and weekday - 1 >= self.due_weekday and not self.is_completed_for_period():
            return True
        return False
