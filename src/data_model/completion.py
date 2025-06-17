import datetime



class Completion:
     
    """
    Represents a single instance of a habit being completed.

    Attributes:
        completed_at (datetime.datetime): The date and time the habit was completed. Defaults to the current time.
        notes (str, optional): Additional context or comments about the completion event.
        mood_rating (int, optional): A subjective rating (e.g., 1–5) of the user's mood at the time of completion.

    Example:
        >>> completion = Completion(notes="Felt great!", mood_rating=5)
        >>> print(completion.completed_at)
        2025-06-17 10:30:00

    Why use this class:
        - Allows extensibility beyond just storing a datetime.
        - Supports additional metadata like mood, location, or duration.
        - Demonstrates good OOP practice via composition.
    """
    def __init__(self, completed_at=None, notes=None, mood_rating=None):
        self.completed_at = completed_at if completed_at else datetime.datetime.now()
        self.notes = notes
        self.mood_rating = mood_rating

