import json
from pathlib import Path
from typing import List, Any, Dict

import datetime

from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit
from src.data_model.completion import Completion


class StorageHandler:
    """
    Handles saving and loading habit data to/from a JSON file.
    """

    def __init__(self, file_path: str = "data/habits.json"):
        """
        Initializes the handler with a target JSON file path.
        Ensures the parent directory exists.
        """
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def _serialize_completion(self, completion: Completion) -> Dict[str, Any]:
        """Convert a Completion into a JSON-serializable dict."""
        return {
            "id": completion.id,
            "timestamp": completion.timestamp.isoformat(),
            "notes": completion.notes,
            "mood_score": completion.mood_score,
        }

    def _deserialize_completion(self, data: Dict[str, Any]) -> Completion:
        """Reconstruct a Completion from its dict representation."""
        return Completion(
            _id=data.get("id"),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            notes=data.get("notes"),
            mood_score=data.get("mood_score"),
        )

    def _serialize_habit(self, habit: BaseHabit) -> Dict[str, Any]:
        """Convert a Habit (daily or weekly) into a dict for JSON."""
        d = habit.to_dict()  # includes id, name, creation_date, type, completion_records
        # Override completion_records with full serialization
        d["completion_records"] = [self._serialize_completion(c) for c in habit.get_completion_records()]
        # WeeklyHabit has extra due_weekday
        if isinstance(habit, WeeklyHabit):
            d["due_weekday"] = habit.due_weekday
        return d

    def _deserialize_habit(self, data: Dict[str, Any]) -> BaseHabit:
        """Reconstruct a Habit object from its dict representation."""
        # Deserialize completions first
        comps = [self._deserialize_completion(c) for c in data.get("completion_records", [])]

        habit_type = data.get("type")
        name = data["name"]
        creation = datetime.datetime.fromisoformat(data["creation_date"])
        hid = data.get("id")

        if habit_type == "DailyHabit":
            habit = DailyHabit(name, creation, _id=hid, completion_records=comps)
        elif habit_type == "WeeklyHabit":
            due = data.get("due_weekday", 0)
            habit = WeeklyHabit(name, creation, due_weekday=due, _id=hid, completion_records=comps)
        else:
            raise ValueError(f"Unknown habit type: {habit_type}")

        return habit

    def save_habits(self, habits: List[BaseHabit]) -> None:
        """
        Save a list of Habit objects to the JSON file.
        """
        data = [self._serialize_habit(h) for h in habits]
        with self._file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_habits(self) -> List[BaseHabit]:
        """
        Load Habit objects from the JSON file.
        Returns an empty list if the file doesn't exist or is invalid.
        """
        if not self._file_path.exists():
            return []

        try:
            with self._file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # Corrupted file; start fresh
            return []
        
        habits: List[BaseHabit] = []
        for item in data:
            try:
                habits.append(self._deserialize_habit(item))
            except Exception:
                # Skip invalid entries
                continue
        return habits