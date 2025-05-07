
# EasyLogiPro - Logistics Management System

A simple desktop application for small trucking businesses to manage logistics operations.

## Features

- **Trip Management:** Add, edit, and delete trip records
- **Vehicle Maintenance Tracker:** Log and track maintenance activities
- **Driver Payment Tracker:** Calculate driver payments based on trips
- **Inventory Management:** Track inventory items and their values
- **Customer Ledger:** Monitor customer transactions and outstanding balances

## Requirements

- Python 3.6+
- tkinter (included with standard Python installation)
- tkcalendar
- SQLite3 (included with standard Python installation)
- PyInstaller (for creating executable)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application directly with Python:

```
python easylogipro.py
```

## Creating an Executable

To create a standalone Windows executable:

```
pyinstaller --onefile --windowed --icon=icon.ico --name=EasyLogiPro easylogipro.py
```

The executable will be created in the `dist` folder.

## Database

The application uses a local SQLite database file (`easylogipro.db`) that will be created automatically on first run. All data is stored locally.

## License

Free for personal and commercial use.
