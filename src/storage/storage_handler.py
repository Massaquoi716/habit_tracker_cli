import json
from pathlib import Path
from typing import List, Any, Dict

import datetime

from src.data_model.habit import BaseHabit, DailyHabit, WeeklyHabit
from src.data_model.completion import Completion

class StorageHandler:
    """
    Handles saving and loading habit data to and from a JSON file.

    This class provides persistence functionality for the Habit Tracker CLI Application,
    managing the serialization and deserialization of BaseHabit instances (including
    DailyHabit and WeeklyHabit) and their associated Completion objects to/from a JSON
    file (default: `data/habits.json`). It ensures the directory structure exists and
    handles file corruption gracefully.

    Attributes:
        _file_path (Path): The file path for the JSON storage (defaults to "data/habits.json").

    Usage:
        - Initialize with an optional file path.
        - Use save_habits() to persist a list of habits and load_habits() to retrieve them.
    """

    def __init__(self, file_path: str = "data/habits.json"):
        """
        Initialize the StorageHandler with a target JSON file path.

        Args:
            file_path (str): The path to the JSON file (defaults to "data/habits.json").

        Notes:
            - Creates parent directories if they don't exist using Path.mkdir().
            - Stores the path as a Path object for consistent file operations.
        """
        self._file_path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def _serialize_completion(self, completion: Completion) -> Dict[str, Any]:
        """
        Convert a Completion object into a JSON-serializable dictionary.

        Args:
            completion (Completion): The Completion instance to serialize.

        Returns:
            Dict[str, Any]: A dictionary with id, timestamp (ISO format), notes, and mood_score.

        Notes:
            - Uses isoformat() for timestamp compatibility with JSON.
        """
        return {
            "id": completion.id,
            "timestamp": completion.timestamp.isoformat(),
            "notes": completion.notes,
            "mood_score": completion.mood_score,
        }

    def _deserialize_completion(self, data: Dict[str, Any]) -> Completion:
        """
        Reconstruct a Completion object from its dictionary representation.

        Args:
            data (Dict[str, Any]): A dictionary containing id, timestamp, notes, and mood_score.

        Returns:
            Completion: A new Completion instance populated from the dictionary.

        Raises:
            ValueError: If timestamp cannot be parsed from ISO format.
            KeyError: If required keys are missing.

        Notes:
            - Uses datetime.fromisoformat() for timestamp parsing.
            - Missing optional fields (notes, mood_score) default to None.
        """
        return Completion(
            _id=data.get("id"),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            notes=data.get("notes"),
            mood_score=data.get("mood_score"),
        )

    def _serialize_habit(self, habit: BaseHabit) -> Dict[str, Any]:
        """
        Convert a BaseHabit object (daily or weekly) into a dictionary for JSON serialization.

        Args:
            habit (BaseHabit): The habit instance to serialize.

        Returns:
            Dict[str, Any]: A dictionary with id, name, creation_date, type, completion_records,
                and due_weekday (for WeeklyHabit).

        Notes:
            - Overrides completion_records with fully serialized versions.
            - Adds due_weekday for WeeklyHabit instances.
        """
        d = habit.to_dict()  # Base serialization (id, name, creation_date, type, completion_records)
        # Replace completion_records with fully serialized data
        d["completion_records"] = [self._serialize_completion(c) for c in habit.get_completion_records()]
        # Include due_weekday for WeeklyHabit
        if isinstance(habit, WeeklyHabit):
            d["due_weekday"] = habit.due_weekday
        return d

    def _deserialize_habit(self, data: Dict[str, Any]) -> BaseHabit:
        """
        Reconstruct a BaseHabit object from its dictionary representation.

        Args:
            data (Dict[str, Any]): A dictionary containing id, name, creation_date, type,
                completion_records, and due_weekday (for WeeklyHabit).

        Returns:
            BaseHabit: A new habit instance (DailyHabit or WeeklyHabit) populated from the dictionary.

        Raises:
            ValueError: If habit_type is unknown or timestamp parsing fails.
            KeyError: If required keys are missing.

        Notes:
            - Deserializes completions first using _deserialize_completion.
            - Uses the 'type' field to instantiate the correct subclass.
            - Defaults due_weekday to 0 for WeeklyHabit if missing.
        """
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
        Save a list of habit objects to the JSON file.

        Args:
            habits (List[BaseHabit]): The list of habit instances to save.

        Returns:
            None

        Notes:
            - Serializes each habit using _serialize_habit and writes with indentation for readability.
            - Uses UTF-8 encoding to support special characters.
        """
        data = [self._serialize_habit(h) for h in habits]
        with self._file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_habits(self) -> List[BaseHabit]:
        """
        Load habit objects from the JSON file.

        Returns:
            List[BaseHabit]: A list of reconstructed habit instances.

        Notes:
            - Returns an empty list if the file doesn't exist or is invalid (e.g., JSONDecodeError).
            - Skips individual invalid entries during deserialization to prevent failure.
        """
        if not self._file_path.exists():
            return []

        try:
            with self._file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # Handle corrupted file by returning an empty list
            return []
        
        habits: List[BaseHabit] = []
        for item in data:
            try:
                habits.append(self._deserialize_habit(item))
            except Exception:
                # Skip invalid entries to maintain partial data integrity
                continue
        return habits