# src/cli/user_interface.py

import questionary
from typing import List, Dict, Tuple, Optional
from src.managers.habit_manager import HabitManager


class UserInterface:
    """
    Manages all interactions with the user via the command line.
    """

    def __init__(self, manager: HabitManager):
        self.manager = manager

    def start(self):
        """Launch the CLI application loop."""
        while True:
            choice = questionary.select(
                "📋 What would you like to do?",
                choices=[
                    "➕ Add a New Habit",
                    "✅ Check Off a Habit",
                    "📄 View All Habits",
                    "📈 View Streaks",
                    "🗑️ Delete a Habit",
                    "🧨 Break a Habit’s Streak",
                    "🚪 Exit",
                ]
            ).ask()

            if choice == "➕ Add a New Habit":
                self.add_habit_flow()
            elif choice == "✅ Check Off a Habit":
                self.check_off_flow()
            elif choice == "📄 View All Habits":
                self.view_habits()
            elif choice == "📈 View Streaks":
                self.view_streaks()
            elif choice == "🗑️ Delete a Habit":
                self.delete_habit_flow()
            elif choice == "🧨 Break a Habit’s Streak":
                self.break_streak_flow()
            elif choice == "🚪 Exit":
                print("👋 Goodbye!")
                break

    def add_habit_flow(self):
        name = questionary.text("Enter the habit name:").ask()
        habit_type = questionary.select("Select habit type:", choices=["daily", "weekly"]).ask()

        due_weekday = None
        if habit_type == "weekly":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_day = questionary.select("Pick due weekday:", choices=days).ask()
            due_weekday = days.index(selected_day)

        success, msg = self.manager.add_habit(habit_type, name, due_weekday)
        print(f"✅ {msg}" if success else f"❌ {msg}")

    def check_off_flow(self):
        habits = self.manager.get_all_habits()
        if not habits:
            print("⚠️ No habits found.")
            return

        name = questionary.select(
            "Select a habit to check off:",
            choices=[h.name for h in habits]
        ).ask()
        notes = questionary.text("Optional notes (or leave empty):").ask()
        mood = questionary.select(
            "How was your mood?",
            choices=["1", "2", "3", "4", "5", "Skip"]
        ).ask()
        mood_score = int(mood) if mood.isdigit() else None

        success, msg = self.manager.check_off_habit(name, notes=notes or None, mood_score=mood_score)
        print(f"✅ {msg}" if success else f"❌ {msg}")

    def view_habits(self):
        habits = self.manager.get_all_habits()
        if not habits:
            print("⚠️ No habits to show.")
            return
        for h in habits:
            print(f"- {h}")

    

    def view_streaks(self):
        # Get analytics
        max_any, longest_any = self.manager.get_longest_streak_overall()
        max_daily, longest_daily = self.manager.get_longest_streak_daily()
        max_weekly, longest_weekly = self.manager.get_longest_streak_weekly()
        current = self.manager.get_current_streaks()

        # Format helpers
        def fmt_any(items: List[Tuple[str, str]], length: int) -> str:
            if not items or length is None:
                return "None"
            parts = []
            for name, periodicity in items:
                unit = "days" if periodicity == "daily" else "weeks"
                parts.append(f"{name} ({length} {unit})")
            return ", ".join(parts)

        def fmt_list(names: List[str], length: int, unit: str) -> str:
            return "None" if not names or length is None else ", ".join(f"{n} ({length} {unit})" for n in names)

        # Display streaks
        print("\n📊 Longest Streak (Any):", fmt_any(longest_any, max_any))
        print("📊 Longest Daily:       ", fmt_list(longest_daily, max_daily, "days"))
        print("📊 Longest Weekly:      ", fmt_list(longest_weekly, max_weekly, "weeks"))

        print("\n🔥 Current Streaks:")
        if not current:
            print("  (none active)")
        else:
            for name, streak in current.items():
                print(f"  {name}: {streak}")


    def delete_habit_flow(self):
        habits = self.manager.get_all_habits()
        if not habits:
            print("⚠️ No habits to delete.")
            return
        name = questionary.select(
            "Pick a habit to delete:",
            choices=[h.name for h in habits]
        ).ask()
        confirm = questionary.confirm(f"Are you sure you want to delete '{name}'?").ask()
        if confirm:
            success, msg = self.manager.delete_habit(name)
            print(f"🗑️ {msg}" if success else f"❌ {msg}")

    def break_streak_flow(self):
        habits = self.manager.get_all_habits()
        if not habits:
            print("⚠️ No habits available.")
            return
        name = questionary.select(
            "Select a habit to break streak:",
            choices=[h.name for h in habits]
        ).ask()
        confirm = questionary.confirm(
            f"Really break the streak for '{name}'? This cannot be undone."
        ).ask()
        if confirm:
            success, msg = self.manager.break_streak(name)
            print(f"🧨 {msg}" if success else f"❌ {msg}")
