
# 🧠 Habit Tracker Project: Conception Phase Document

---

## 1. Project Overview and Goals

This document outlines the conceptual design and technical blueprint for a **Command Line Interface (CLI)** based habit tracking application. The primary goal of this Conception Phase is to detail the application's core components, data model, storage strategy, user interaction, analytics logic, and testing approach before significant coding begins.

The design emphasizes:
- **Object-Oriented Programming (OOP)** for the data model
- **Functional Programming (FP)** for analytics logic

> These principles promote clean, testable, and maintainable code (Lott, 2018; Phillips, 2018).

---

## 2. Core Application Components

The Habit Tracker application will be structured around several distinct, interacting components. This modular design promotes separation of concerns and easier maintenance.

### 2.1 Component Breakdown and Responsibilities

#### 📦 `HabitManager` (`src/managers/habit_manager.py`)
- Adds, retrieves, checks off, deletes, and lists habits.
- Manages the collection of Habit objects in memory.
- Delegates persistence to `StorageHandler`.

#### 📦 `StorageHandler` (`src/storage/storage_handler.py`)
- Serializes and saves Habit and Completion objects to JSON.
- Deserializes data from file and restores them as objects.
- Coordinates with `HabitManager`.

#### 📦 `UserInterface` (`src/cli/user_interface.py`)
- Manages all CLI interactions using the `questionary` library.
- Presents menus, prompts input, validates, and displays feedback.
- Translates user input into actions using `HabitManager` and `AnalyticsService`.

#### 📦 `AnalyticsService` (`src/analytics/analytics_service.py`)
- Computes current and longest streaks.
- Aggregates statistics.
- Returns insights without modifying any data (pure functions).

---

### 2.2 Component Interaction Flow

```text
UserInterface
    └── HabitManager (core habit logic)
        └── StorageHandler (data I/O)
    └── AnalyticsService (for calculations)
```

---

## 3. Designing the Habit Data Model (OOP)

The core data structure uses OOP to model and manage habits.

### 3.1 `BaseHabit` (`src/data_model/habit.py`)

**Attributes:**
- `name (str)`: Name of the habit.
- `_creation_date (datetime)`: Private-like creation timestamp.
- `_completion_records (list[Completion])`: List of check-offs (composition).

**Core Methods:**
- `__init__()`: Initializes with validations.
- `check_off()`: Adds a new `Completion` record.
- `get_completion_records()`: Returns sorted copy of completions.
- `__str__()` and `__repr__()`: String representations.

---

### 3.2 `DailyHabit` and `WeeklyHabit` (Inheritance & Polymorphism)

- Subclasses of `BaseHabit`.
- Implement `is_due_on(date)` to determine habit periodicity.
- Demonstrate polymorphism by overriding behavior in each subclass.

---

### 3.3 `Completion` (`src/data_model/completion.py`)

**Attributes:**
- `timestamp (datetime)`: When it was completed.
- `notes (str, optional)`: Freeform notes.
- `mood_score (int, optional)`: Mood rating.

**Benefits:**
- Encapsulation of completion metadata.
- Easy to extend with new attributes (e.g., duration).
- Keeps data structure flexible and future-proof.

---

## 4. Data Storage and Retrieval Strategy (JSON)

Data will be stored in a **human-readable JSON file** (`data/habits.json`).

### 🔐 Why JSON?
- Simple, readable, and structured.
- Supported natively by Python.
- Avoids database complexity for a CLI project.

### 💾 Serialization
- Habits and completions are converted to dictionaries.
- `datetime` fields stored as ISO 8601 strings.
- A `"type"` field (e.g., `DailyHabit`) is included to reconstruct the object class.

### 🔁 Deserialization
- JSON is read into dictionaries.
- Based on `"type"`, the correct class is instantiated.
- All data is loaded into `HabitManager`.

---

## 5. User Interaction and CLI Flow

The `UserInterface` offers a friendly, menu-driven command-line experience using `questionary`.

### 🎯 Main Features
- Create daily/weekly habits
- Check off habits (with optional mood/notes)
- View all habits or filter by type
- View streaks and completions
- Delete or reset habits

### 🔄 User Flow

```text
App Launch
  └─ Load data via StorageHandler
  └─ Show Main Menu (questionary)
      └─ Handle actions via HabitManager or AnalyticsService
      └─ Show output and return to menu
```

### ✨ User Prompts
Menus and forms will be built with `questionary.select`, `text`, `confirm`, etc.

---

## 6. Analytics and Streak Logic (Functional Programming)

The `AnalyticsService` module provides insight into user progress.

### Key Functions
- `calculate_current_streak(habit)`
- `calculate_longest_streak(habit)`
- `get_habits_by_periodicity(habits, periodicity)`

### FP Principles Applied

- **Pure Functions**: No side effects; predictable outputs.
- **Immutability**: Input data remains unchanged.
- **Higher-Order Functions**: Use of `map()`, `filter()`, `sorted()`, `reduce()`.
- **Generators**: Efficient for large completion lists.

---

## 7. Testing Strategy

Testing is done using `pytest` with test files in the `tests/` directory.

### 🔍 Test Coverage

| File | Purpose |
|------|---------|
| `test_habit_model.py` | Tests for `BaseHabit`, `DailyHabit`, `WeeklyHabit`, `Completion` |
| `test_habit_manager.py` | Tests logic in `HabitManager` |
| `test_storage_handler.py` | Tests file save/load logic |
| `test_analytics_service.py` | Tests FP calculations |
| `test_cli.py` | Mocks CLI interactions |

### 🧪 Testing Practices
- Unit tests for every component
- Use of fixtures and mocks
- Temporary files for storage tests
- Edge case handling (e.g., invalid input, missing fields)

---

## 📚 References

- IETF. (2017). *The JavaScript Object Notation (JSON) Data Interchange Format (RFC 8259)*. [RFC 8259](https://datatracker.ietf.org/doc/html/rfc8259)  
- Lott, S. F. (2018). *Functional Python Programming* (2nd ed.). Packt Publishing.  
- Lutz, M. (2013). *Learning Python* (5th ed.). O’Reilly.  
- Phillips, D. (2018). *Python 3 Object-Oriented Programming* (3rd ed.). Packt Publishing.  
- Pytest Documentation. [pytest.org](https://pytest.org/)  
- Questionary Developers. [questionary.readthedocs.io](https://questionary.readthedocs.io/)  
- Ramalho, L. (2015). *Fluent Python*. O’Reilly.  
