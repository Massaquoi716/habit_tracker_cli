import datetime
from typing import Optional
import uuid

class Completion:
    """Represents a single completion event for a habit."""
    
    def __init__(
        self,
        timestamp: Optional[datetime.datetime] = None,
        notes: Optional[str] = None,
        mood_score: Optional[int] = None,
        _id: Optional[str] = None
    ):
        self.timestamp = timestamp or datetime.datetime.now()
        self.notes = notes
        self.mood_score = mood_score
        self.id = _id or str(uuid.uuid4())

        if self.mood_score is not None and not (1 <= self.mood_score <= 5):
            raise ValueError("Mood score must be between 1 and 5.")

    def to_dict(self) -> dict:
        """Converts the Completion object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes,
            "mood_score": self.mood_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Completion":
        """Creates a Completion object from a dictionary."""
        return cls(
            _id=data.get("id"),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            notes=data.get("notes"),
            mood_score=data.get("mood_score")
        )

    def __str__(self) -> str:
        mood_str = f" Mood: {self.mood_score}/5" if self.mood_score else ""
        notes_str = f" Notes: '{self.notes}'" if self.notes else ""
        return f"Completed at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{notes_str}{mood_str}"

    def __repr__(self) -> str:
        return (
            f"Completion(timestamp='{self.timestamp.isoformat()}', "
            f"notes='{self.notes}', mood_score={self.mood_score}, _id='{self.id}')"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Completion):
            return NotImplemented
        return self.id == other.id
