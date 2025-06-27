#!/usr/bin/env python3
"""
Script to generate fixture data for the Habit Tracker CLI Application.

This script creates and saves test habit data to a JSON file (default: `data/habits.json`)
for use in development or testing. It generates 5 predefined habits (3 daily: "Drink Water",
"Exercise", "Meditate"; 2 weekly: "Read", "Clean House") with 4 weeks of completion records
from January 2, 2023, to January 29, 2023. The data is formatted to match the structure
expected by `StorageHandler` and `HabitManager`.

Dependencies:
    - json (standard library)
    - datetime (standard library)
    - uuid (standard library)
    - pathlib (standard library)

Usage:
    - Run with `python3 generate_fixtures.py` or `./generate_fixtures.py` (after `chmod +x`).
    - The script overwrites `data/habits.json` with the predefined habits.

Notes:
    - Generates fixed 4-week data (Jan 2–Jan 29, 2023) for testing consistency.
    - Each habit includes a creation date and completion records with timestamps.
    - Ensure the `data/` directory is writable.
"""

import json
import datetime
import uuid
from pathlib import Path

def generate_daily_completions(start: datetime.date, end: datetime.date, time_of_day: datetime.time) -> list[dict]:
    """
    Generate a list of completion records for a daily habit over a specified date range.

    Args:
        start (datetime.date): The start date of the range (inclusive).
        end (datetime.date): The end date of the range (inclusive).
        time_of_day (datetime.time): The time of day to assign to each completion.

    Returns:
        list[dict]: A list of dictionaries, each containing 'id', 'timestamp' (ISO format),
            'notes' (None), and 'mood_score' (None) for each day in the range.

    Notes:
        - Generates one completion per calendar day between start and end.
        - Uses uuid.uuid4() to create unique IDs for each completion.
        - Combines the date and time_of_day into a datetime object for the timestamp.
    """
    records = []
    d = start
    while d <= end:
        records.append({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.combine(d, time_of_day).isoformat(),
            "notes": None,
            "mood_score": None
        })
        d += datetime.timedelta(days=1)
    return records

def generate_weekly_completions(start: datetime.date, end: datetime.date, weekday: int, time_of_day: datetime.time) -> list[dict]:
    """
    Generate a list of completion records for a weekly habit over a specified date range.

    Args:
        start (datetime.date): The start date of the range (inclusive).
        end (datetime.date): The end date of the range (inclusive).
        weekday (int): The weekday to generate completions for (0=Mon, 6=Sun).
        time_of_day (datetime.time): The time of day to assign to each completion.

    Returns:
        list[dict]: A list of dictionaries, each containing 'id', 'timestamp' (ISO format),
            'notes' (None), and 'mood_score' (None) for each week on the specified weekday.

    Notes:
        - Generates one completion per week on the specified weekday within the date range.
        - Adjusts the start date to the first occurrence of the weekday.
        - Uses uuid.uuid4() to create unique IDs for each completion.
        - Combines the date and time_of_day into a datetime object for the timestamp.
    """
    records = []
    # Find the first occurrence of the specified weekday
    d = start
    while d.weekday() != weekday:
        d += datetime.timedelta(days=1)
    while d <= end:
        records.append({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.combine(d, time_of_day).isoformat(),
            "notes": None,
            "mood_score": None
        })
        d += datetime.timedelta(weeks=1)
    return records

def main():
    """
    Generate and save fixture data for 5 predefined habits.

    This function creates 3 daily habits ("Drink Water", "Exercise", "Meditate") and
    2 weekly habits ("Read", "Clean House") with completion records for 4 weeks
    (January 2, 2023, to January 29, 2023). The data is saved to `data/habits.json`
    for testing purposes.

    Returns:
        None

    Notes:
        - Overwrites `data/habits.json` with the predefined habits.
        - Uses fixed dates for consistency in testing.
        - Prints the total number of habits saved to the console.
    """
    # Define the 4-week period for test data
    start_date = datetime.date(2023, 1, 2)  # Start of the 4-week period
    end_date = datetime.date(2023, 1, 29)   # End of the 4-week period

    # Define 5 predefined habits
    fixtures = [
        {
            "id": str(uuid.uuid4()),
            "name": "Drink Water",
            "type": "DailyHabit",
            "creation_date": start_date.isoformat() + "T00:00:00",
            "completion_records": generate_daily_completions(
                start_date, end_date, datetime.time(8, 0)
            )
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Exercise",
            "type": "DailyHabit",
            "creation_date": start_date.isoformat() + "T00:00:00",
            "completion_records": generate_daily_completions(
                start_date, end_date, datetime.time(18, 0)
            )
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Meditate",
            "type": "DailyHabit",
            "creation_date": start_date.isoformat() + "T00:00:00",
            "completion_records": generate_daily_completions(
                start_date, end_date, datetime.time(7, 0)
            )
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Read",
            "type": "WeeklyHabit",
            "due_weekday": 2,  # Wednesday
            "creation_date": start_date.isoformat() + "T00:00:00",
            "completion_records": generate_weekly_completions(
                start_date, end_date, 2, datetime.time(20, 0)
            )
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Clean House",
            "type": "WeeklyHabit",
            "due_weekday": 5,  # Saturday
            "creation_date": start_date.isoformat() + "T00:00:00",
            "completion_records": generate_weekly_completions(
                start_date, end_date, 5, datetime.time(10, 0)
            )
        }
    ]

    # Write the fixtures to the JSON file
    out_path = Path("data/habits.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=4)

    print(f"Generated {len(fixtures)} habits in {out_path.resolve()}")

if __name__ == "__main__":
    main()