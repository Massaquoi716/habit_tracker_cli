import questionary
from typing import List, Dict, Tuple, Optional
from src.managers.habit_manager import HabitManager

class UserInterface:
    """
    Manages all interactions with the user via the command line interface (CLI).
    This class provides a menu-driven interface for users to create, manage, and analyze
    habits, leveraging the HabitManager for business logic. It uses the questionary library
    for interactive prompts and handles user input in a loop until exit.

    Attributes:
        manager (HabitManager): The habit management instance to handle habit operations.

    Usage:
        - Initialize with a HabitManager instance.
        - Call start() to launch the CLI application loop.
    """

    def __init__(self, manager: HabitManager):
        """
        Initialize the UserInterface with a HabitManager instance.

        Args:
            manager (HabitManager): The habit manager instance to delegate operations to.

        Raises:
            ValueError: If manager is None.
        """
        if manager is None:
            raise ValueError("HabitManager instance cannot be None.")
        self.manager = manager

    def start(self):
        """
        Launch the CLI application loop.

        This method runs an infinite loop presenting a menu of options to the user
        until they choose to exit. Each option triggers a corresponding flow method.

        Returns:
            None

        Notes:
            - Uses questionary.select for a dynamic menu with emoji indicators.
            - Exits gracefully with a goodbye message when "Exit" is selected.
        """
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
        """
        Handle the flow for adding a new habit.

        Prompts the user for a habit name and type (daily or weekly), and optionally
        a due weekday for weekly habits. Delegates the addition to HabitManager.

        Returns:
            None

        Notes:
            - Uses questionary.text and questionary.select for input.
            - Maps weekday names to indices (0-6) for weekly habits.
            - Displays success or error message based on manager response.
        """
        name = questionary.text("Enter the habit name:").ask()
        habit_type = questionary.select("Select habit type:", choices=["daily", "weekly"]).ask()

        due_weekday = None
        if habit_type == "weekly":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_day = questionary.select("Pick due weekday:", choices=days).ask()
            due_weekday = days.index(selected_day)  # Convert to 0-6 index

        success, msg = self.manager.add_habit(habit_type, name, due_weekday)
        print(f"✅ {msg}" if success else f"❌ {msg}")

    def check_off_flow(self):
        """
        Handle the flow for checking off a habit completion.

        Allows the user to select a habit, add optional notes, and provide a mood score.
        Delegates the check-off to HabitManager.

        Returns:
            None

        Notes:
            - Skips mood score if "Skip" is selected.
            - Displays success or error message based on manager response.
        """
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
        mood_score = int(mood) if mood.isdigit() else None  # Convert to int or None if skipped

        success, msg = self.manager.check_off_habit(name, notes=notes or None, mood_score=mood_score)
        print(f"✅ {msg}" if success else f"❌ {msg}")

    def view_habits(self):
        """
        Display all habits managed by the application.

        Retrieves and prints a list of all habits from HabitManager.

        Returns:
            None

        Notes:
            - Uses the string representation of each habit (via __str__ in Habit class).
            - Shows a warning if no habits exist.
        """
        habits = self.manager.get_all_habits()
        if not habits:
            print("⚠️ No habits to show.")
            return
        for h in habits:
            print(f"- {h}")

    def view_streaks(self):
        """
        Display streak analytics for all habits.

        Retrieves longest and current streaks from HabitManager and formats them for display.

        Returns:
            None

        Notes:
            - Uses helper functions fmt_any and fmt_list to format output.
            - Handles cases where no streaks are available.
        """
        # Get analytics from HabitManager
        max_any, longest_any = self.manager.get_longest_streak_overall()
        max_daily, longest_daily = self.manager.get_longest_streak_daily()
        max_weekly, longest_weekly = self.manager.get_longest_streak_weekly()
        current = self.manager.get_current_streaks()

        # Helper functions to format output
        def fmt_any(items: List[Tuple[str, str]], length: int) -> str:
            """Format a list of (name, periodicity) tuples with a streak length."""
            if not items or length is None:
                return "None"
            return ", ".join(f"{name} ({length} {'days' if p == 'daily' else 'weeks'})" 
                           for name, p in items)

        def fmt_list(names: List[str], length: int, unit: str) -> str:
            """Format a list of names with a streak length and unit."""
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
        """
        Handle the flow for deleting a habit.

        Prompts the user to select a habit and confirm deletion, then delegates to HabitManager.

        Returns:
            None

        Notes:
            - Requires confirmation to prevent accidental deletion.
            - Displays success or error message based on manager response.
        """
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
        """
        Handle the flow for breaking a habit's streak.

        Prompts the user to select a habit and confirm streak reset, then delegates to HabitManager.

        Returns:
            None

        Notes:
            - Includes a strong warning about irreversibility.
            - Displays success or error message based on manager response.
        """
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