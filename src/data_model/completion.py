import datetime
from typing import Optional
import uuid

class Completion:
    """
    Represents a single completion event for a habit, encapsulating details like timestamp,
    notes, mood score, and a unique identifier.

    This class is designed to be used within the Habit Tracker CLI Application to record
    when a habit is completed, including optional metadata (notes and mood). It supports
    serialization to and deserialization from dictionaries for JSON persistence (e.g., in
    `data/habits.json`). Instances are immutable after creation, with validation for mood
    scores.

    Attributes:
        timestamp (datetime.datetime): The time of completion (defaults to now if not provided).
        notes (Optional[str]): Optional user-provided notes about the completion.
        mood_score (Optional[int]): Optional mood rating from 1 to 5.
        id (str): A unique identifier for the completion (auto-generated via UUID if not provided).

    Usage:
        - Create instances directly with optional parameters.
        - Use to_dict() for JSON serialization and from_dict() for deserialization.
        - Compare instances using __eq__ based on ID.
    """

    def __init__(
        self,
        timestamp: Optional[datetime.datetime] = None,
        notes: Optional[str] = None,
        mood_score: Optional[int] = None,
        _id: Optional[str] = None
    ):
        """
        Initialize a Completion instance with optional parameters.

        Args:
            timestamp (Optional[datetime.datetime]): The completion time. Defaults to now if None.
            notes (Optional[str]): User notes about the completion. Defaults to None.
            mood_score (Optional[int]): Mood rating (1-5). Defaults to None.
            _id (Optional[str]): Unique identifier. Defaults to a new UUID if None.

        Raises:
            ValueError: If mood_score is provided but not between 1 and 5.

        Notes:
            - Timestamp is set to the current time if not specified.
            - ID is auto-generated using uuid.uuid4() if not provided.
        """
        self.timestamp = timestamp or datetime.datetime.now()
        self.notes = notes
        self.mood_score = mood_score
        self.id = _id or str(uuid.uuid4())

        # Validate mood score if provided
        if self.mood_score is not None and not (1 <= self.mood_score <= 5):
            raise ValueError("Mood score must be between 1 and 5.")

    def to_dict(self) -> dict:
        """
        Convert the Completion object to a dictionary for JSON serialization.

        Returns:
            dict: A dictionary containing id, timestamp (ISO format), notes, and mood_score.

        Notes:
            - Timestamp is converted to ISO format for compatibility with JSON.
            - None values are included to preserve structure.
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes,
            "mood_score": self.mood_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Completion":
        """
        Create a Completion object from a dictionary (e.g., deserialized JSON).

        Args:
            data (dict): Dictionary with keys 'id', 'timestamp', 'notes', and 'mood_score'.

        Returns:
            Completion: A new Completion instance populated from the dictionary.

        Raises:
            ValueError: If timestamp cannot be parsed from ISO format.
            KeyError: If required keys are missing from data.

        Notes:
            - Uses datetime.fromisoformat to parse the timestamp.
            - Missing optional fields (notes, mood_score) default to None.
        """
        return cls(
            _id=data.get("id"),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            notes=data.get("notes"),
            mood_score=data.get("mood_score")
        )

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Completion.

        Returns:
            str: Formatted string with timestamp, notes (if any), and mood score (if any).

        Notes:
            - Uses strftime for a readable date-time format.
            - Appends notes and mood only if they exist.
        """
        mood_str = f" Mood: {self.mood_score}/5" if self.mood_score else ""
        notes_str = f" Notes: '{self.notes}'" if self.notes else ""
        return f"Completed at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{notes_str}{mood_str}"

    def __repr__(self) -> str:
        """
        Return a detailed string representation for debugging.

        Returns:
            str: A string showing all attributes, useful for debugging or logging.

        Notes:
            - Includes all fields in a Python constructor-like format.
        """
        return (
            f"Completion(timestamp='{self.timestamp.isoformat()}', "
            f"notes='{self.notes}', mood_score={self.mood_score}, _id='{self.id}')"
        )

    def __eq__(self, other) -> bool:
        """
        Compare two Completion instances for equality based on their IDs.

        Args:
            other: Another object to compare with.

        Returns:
            bool: True if both are Completion instances with the same ID, False otherwise.
            NotImplemented if other is not a Completion instance.

        Notes:
            - Equality is determined solely by the id attribute.
            - Returns NotImplemented for non-Completion comparisons to allow fallback.
        """
        if not isinstance(other, Completion):
            return NotImplemented
        return self.id == other.id