# Reimbursement Simulator Project Documentation

## 1. Overview

This project provides a desktop application for importing reimbursement-related spreadsheet data, reviewing it in a tabular grid, deleting selected rows, storing the cleaned data into a local SQLite database, and preparing a foundation for future grouping and analysis workflows.

## 2. Goals

- Import Excel and CSV files through a graphical user interface.
- Display imported data in a grid view for inspection.
- Allow users to delete a selected row range by entering start and end row numbers.
- Store imported data into a local SQLite database using SQLAlchemy.
- Provide a tab-based UI structure ready for future group and analysis features.

## 3. Scope

### In Scope
- PySide6-based desktop UI.
- Tabbed main window with three tabs.
- File import from Excel and CSV.
- In-memory grid display and row deletion.
- SQLite persistence using SQLAlchemy ORM.
- Basic project documentation.

### Out of Scope
- Advanced business-rule validation.
- Complex grouping logic.
- Full analytics dashboard.
- Multi-user or network database support.

## 4. Architecture

### 4.1 Application Structure

- main.py: entry point for the application.
- app/main_window.py: PySide6 window and UI event handling.
- app/models.py: SQLAlchemy ORM models and database initialization.
- docs/PROJECT_DOCUMENTATION.md: project documentation.

### 4.2 Data Model

The database stores imported reimbursement records in a table named reimbursement_records. The current model is derived from the columns present in the sample Excel file and includes the following fields:

- item_code
- item_name
- category_code
- department
- expense_type
- period_1_2
- payment_method
- business_trip
- travel_expense
- meal_expense
- lodging_expense
- remarks
- note
- group_name

## 5. Functional Requirements

### 5.1 Import Tab

- Provide a file selection button.
- Open a file dialog for selecting Excel or CSV files.
- Load the selected file into a DataFrame.
- Display the loaded data in a grid.
- Allow row deletion either by selecting rows directly in the preview table or by entering a start/end row range and clicking the Delete button.
- Map imported columns to the database schema using both English field names and a set of Korean aliases.
- Persist the current data into SQLite when the Save button is clicked.

### 5.2 Group Tab

- Load records from the database.
- Display them in a table for review.
- Prepare the UI for future grouping configuration features.

### 5.3 Analysis Tab

- Reserve a space for future analysis features.
- Keep the tab intentionally empty for now.

## 6. Technology Stack

- Python 3.x
- PySide6 for desktop UI.
- SQLAlchemy for ORM and SQLite access.
- pandas for reading Excel and CSV files.
- openpyxl for Excel .xlsx import support; legacy .xls support depends on the runtime environment.
- SQLite as the local persistent database.

## 7. Development Notes

- The project includes a Qt Designer UI file and supporting designer assets for future refinement.
- UI files can be created and edited in Qt Designer, then converted or loaded as the project evolves.
- The current implementation uses direct Python UI construction to keep the project runnable quickly while preserving the option to switch to designer-based loading later.

## 8. Future Enhancements

- Add Qt Designer .ui files and generate Python code from them.
- Implement grouping configuration and validation logic.
- Introduce analysis views and reporting features.
- Improve schema mapping for different Excel templates.
