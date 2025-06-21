#!/usr/bin/env python3
from src.storage.storage_handler import StorageHandler
from src.managers.habit_manager import HabitManager
from src.cli.user_interface import UserInterface

if __name__ == "__main__":
    storage = StorageHandler()
    manager = HabitManager(storage)
    cli = UserInterface(manager)
    cli.start()
