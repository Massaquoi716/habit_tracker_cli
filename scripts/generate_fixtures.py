#!/usr/bin/env python3
"""
Script to generate fixture data for the Habit Tracker CLI Application.

This script creates and saves test habit data to a JSON file (default: `data/habits.json`)
for use in development or testing. It generates completion records for a weekly habit
("Deep Work", due on Thursdays) over a specified period (from 29 weeks ago to June 20, 2025),
preserving existing fixtures if the file already exists. The data is formatted to match
the structure expected by `StorageHandler` and `HabitManager`.

Dependencies:
    - json (standard library)
    - datetime (standard library)
    - uuid (standard library)
    - pathlib (standard library)

Usage:
    - Run with `python3 generate_fixtures.py` or `./generate_fixtures.py` (after `chmod +x`).
    - The script overwrites `data/habits.json` with the combined fixtures.

Notes:
    - The script uses a hardcoded end date (June 20, 2025) and calculates start dates
      (29 weeks and 4 weeks ago) relative to it.
    - Existing data is loaded and appended to avoid data loss from previous runs.
    - Ensure the `data/` directory is writable.
"""

import json
import datetime
import uuid
from pathlib import Path

def generate_daily_completions(start: datetime.date, end: datetime.date, time_of_day: datetime.time):
    """
    Generate a list of completion records for a daily habit over a specified date range.

    Args:
        start (datetime.date): The start date of the range (inclusive).
        end (datetime.date): The end date of the range (inclusive).
        time_of_day (datetime.time): The time of day to assign to each completion.

    Returns:
        List[dict]: A list of dictionaries, each containing 'id', 'timestamp' (ISO format),
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

def generate_weekly_completions(start: datetime.date, end: datetime.date, weekday: int, time_of_day: datetime.time):
    """
    Generate a list of completion records for a weekly habit over a specified date range.

    Args:
        start (datetime.date): The start date of the range (inclusive).
        end (datetime.date): The end date of the range (inclusive).
        weekday (int): The weekday to generate completions for (0=Mon, 6=Sun).
        time_of_day (datetime.time): The time of day to assign to each completion.

    Returns:
        List[dict]: A list of dictionaries, each containing 'id', 'timestamp' (ISO format),
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
    Generate and save fixture data for the "Deep Work" weekly habit.

    This function creates a fixture with completions for a "Deep Work" habit (due Thursday)
    from 29 weeks ago to June 20, 2025, appending it to existing fixtures in `data/habits.json`.

    Returns:
        None

    Notes:
        - Uses a hardcoded end date of June 20, 2025, and calculates start dates relative to it.
        - Overwrites the file with the combined list of fixtures.
        - Prints the total number of habits saved to the console.
    """
    # Calculate dates relative to the hardcoded end date (June 20, 2025)
    today = datetime.date(2025, 6, 20)
    four_weeks_ago = today - datetime.timedelta(weeks=4)
    twenty_nine_weeks_ago = today - datetime.timedelta(weeks=29)

    # 1) Load existing fixtures if the file exists
    out_path = Path("data/habits.json")
    fixtures = []
    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            fixtures = json.load(f)

    # 2) Append new weekly habit with completions from 29 weeks ago to June 20, 2025
    fixtures.append({
        "id": str(uuid.uuid4()),
        "name": "Deep Work",
        "type": "WeeklyHabit",
        "due_weekday": 3,  # Thursday (0=Mon, 1=Tue, 2=Wed, 3=Thu, etc.)
        "creation_date": twenty_nine_weeks_ago.isoformat() + "T00:00:00",
        "completion_records": generate_weekly_completions(
            twenty_nine_weeks_ago, today, 3, datetime.time(8, 0)
        )
    })

    # 3) Write back (overwriting) the combined list to the JSON file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=4)

    print(f"Now {len(fixtures)} habits in {out_path.resolve()}")

if __name__ == "__main__":
    main()