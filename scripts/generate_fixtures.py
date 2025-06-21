
import json
import datetime
import uuid
from pathlib import Path

def generate_daily_completions(start: datetime.date, end: datetime.date, time_of_day: datetime.time):
    """Generate one completion per calendar day."""
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
    """Generate one completion per calendar week on the given weekday."""
    records = []
    # Find first occurrence of the due weekday
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
    today = datetime.date(2025, 6, 20)
    four_weeks_ago = today - datetime.timedelta(weeks=4)
    twenty_nine_weeks_ago = today - datetime.timedelta(weeks=29)

    # 1) Load existing fixtures if the file exists
    out_path = Path("data/habits.json")
    fixtures = []
    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            fixtures = json.load(f)

    # 2) Append your new weekly habit
    fixtures.append({
        "id": str(uuid.uuid4()),
        "name": "Deep Work",
        "type": "WeeklyHabit",
        "due_weekday": 3,  # Thursday
        "creation_date": twenty_nine_weeks_ago.isoformat() + "T00:00:00",
        "completion_records": generate_weekly_completions(
            twenty_nine_weeks_ago, today, 3, datetime.time(8, 0)
        )
    })

    # 3) Write back (overwriting) the combined list
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=4)

    print(f"Now {len(fixtures)} habits in {out_path.resolve()}")

if __name__ == "__main__":
    main()
