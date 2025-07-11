# Habit Tracker CLI Application

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/release/python-3100/)


A Python command-line application for tracking daily and weekly habits, built with object-oriented and functional programming principles.

## Table of Contents

* [Conception Phase](#conception-phase)
* [Features](#features)
* [Requirements](#requirements)
* [Setup](#setup)
* [How to Run](#how-to-run)
* [How to Test](#how-to-test)
* [Project Structure](#project-structure)
* [Predefined Habits](#predefined-habits)
* [Development Notes](#development-notes)
* [License](#license)

## Conception Phase

Refer to [`docs/concept_document.md`](./docs/concept_document.md) for the detailed design and technical specifications, including core concepts, high-level architecture, and development philosophy (TDD).

## Features

* Create daily and weekly habits with custom names.
* Check off habits with optional notes and mood scores (1–5).
* View all habits and their streaks.
* Delete habits or reset streaks.
* Analytics for longest and current streaks, implemented using functional programming.
* Data persistence in `data/habits.json`.
* 5 predefined habits with 4 weeks of tracking data via `scripts/generate_fixtures.py`.

## Requirements

- Python 3.10 or later
- Dependencies:
  - exceptiongroup==1.3.0
  - freezegun==1.5.2
  - iniconfig==2.1.0
  - packaging==25.0
  - pluggy==1.6.0
  - prompt_toolkit==3.0.51
  - Pygments==2.19.1
  - pytest==8.4.0
  - pytest-mock==3.14.1
  - python-dateutil==2.9.0.post0
  - questionary==2.1.0
  - six==1.17.0
  - tomli==2.2.1
  - typing_extensions==4.14.0
  - wcwidth==0.2.13

## Setup

1.  **Clone this repository:**
    
    git clone [https://github.com/Massaquoi716/habit_tracker_cli](https://github.com/Massaquoi716/habit_tracker_cli)
    
2.  **Navigate into the directory:**
    
    cd habit_tracker_cli
    
3.  **Create and activate a virtual environment:**
    - Create environment (all platforms):
        - python -m venv venv
    - Activate the environment:
        - On macOS/Linux:
            - source venv/bin/activate
        - On Windows (PowerShell):
            - .\venv\Scripts\Activate.ps1
        - On Windows (Command Prompt):
            - .\venv\Scripts\activate.bat
    
    
    
4.  **Install dependencies:**
    
    pip install -r requirements.txt
    

## How to Run

1.  **Run the application:**
    
    python -m src.main
    
    Use the interactive menu to:
    * Add a new habit (daily or weekly, with optional weekday for weekly habits).
    * Check off a habit (with notes and mood score).
    * View all habits or streak analytics.
    * Delete a habit or reset its streak.
    * Exit the application.

2.  **Generate predefined habits (3 daily, 2 weekly) with 4 weeks of data:**
    
    python3 scripts/generate_fixtures.py
    

## How to Test

Run the test suite (currently **65 tests**):


pytest -v


## Project Structure

```
habit_tracker_cli/
├── src/                      # Source code
│   ├── data_model/           # Defines core entities: Habit, Completion
│   │   ├── habit.py
│   │   └── completion.py
│   ├── cli/                  # Command-Line Interface (user interaction)
│   │   └── user_interface.py
│   ├── managers/             # Business logic managers
│   │   └── habit_manager.py
│   ├── storage/              # Handles data persistence
│   │   └── storage_handler.py
│   ├── analytics/            # Streak calculations and overall statistics
│   │   └── analytics_service.py
│   └── main.py               # Application entry point
├── tests/                    # Unit and integration tests
├── scripts/                  # Utility scripts
│   └── generate_fixtures.py  # Generates initial habit data
├── data/                     # Data storage directory
│   └── habits.json           # JSON file for habit persistence
├── docs/                     # Project documentation
│   └── concept_document.md   # High-level design document
├── requirements.txt          # Python dependencies
└── venv/                     # Python virtual environment (not tracked by Git)
```

## Predefined Habits

Run `scripts/generate_fixtures.py` to create the following habits with completion data for 4 weeks (Jan 2–Jan 29, 2023):

  * **Daily Habits:** "Drink Water", "Exercise", "Meditate"
  * **Weekly Habits:** "Read" (due Wednesday), "Clean House" (due Saturday)

## Development Notes

  * Built with a hybrid approach of **Object-Oriented Programming** (for `habit.py`, `completion.py` data models) and **Functional Programming** (particularly in `analytics_service.py` for immutable data processing and calculations).
  * Uses `questionary` for an intuitive and interactive CLI experience.
  * Data is automatically stored and loaded from a JSON file via `storage_handler.py`.
  * Comprehensive unit and integration tests (following TDD principles) ensure correctness and maintainability.

