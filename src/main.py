#!/usr/bin/env python3
"""
Entry point for the Habit Tracker CLI Application.

This script initializes and launches the command-line interface for managing habits.
It sets up the storage layer, habit management logic, and user interface, loading
existing habits from a JSON file (default: `data/habits.json`) and entering a
interactive loop for user commands. The application relies on the `StorageHandler`,
`HabitManager`, and `UserInterface` classes for functionality.

Dependencies:
    - src.storage.storage_handler.StorageHandler
    - src.managers.habit_manager.HabitManager
    - src.cli.user_interface.UserInterface

Usage:
    - Run directly with `python3 main.py` or `./main.py` (if executable permissions are set).
    - Ensure the `data/` directory exists or is creatable for habit persistence.

Notes:
    - The script assumes all dependencies are correctly installed in the project environment.
    - Existing habits are loaded on startup; new habits are persisted to the JSON file.
"""

from src.storage.storage_handler import StorageHandler
from src.managers.habit_manager import HabitManager
from src.cli.user_interface import UserInterface

if __name__ == "__main__":
    # Initialize the storage handler to manage habit data persistence
    storage = StorageHandler()
    
    # Create the habit manager, loading existing habits from storage
    manager = HabitManager(storage)
    
    # Set up the CLI interface with the manager to handle user interactions
    cli = UserInterface(manager)
    
    # Start the interactive CLI loop, processing user commands until exit
    cli.start()