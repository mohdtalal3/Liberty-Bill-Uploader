# Liberty Bill Uploader

A GUI application for uploading Liberty Energy bill data.

## Features

- User-friendly PyQt5 interface
- Excel file selection
- Date selection with calendar
- Two-step process: login and upload
- Automatic token extraction

## Installation

1. Clone this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python bill_utility_gui.py
```

2. Select your Excel file using the file browser
3. Choose the appropriate date using the date picker
4. Click "Step 1: Login to Liberty" to open Chrome and login to your account
5. After successful login, click "Step 2: Upload Bill Data" to process and upload the bill data

## Requirements

- Python 3.6+
- Chrome browser
- Internet connection

## Files

- `bill_utility.py`: Main entry point for the utility
- `simplified_uploader.py`: Implementation of the simplified uploader
- `liberty_api.py`: API interaction with Liberty Energy & Water

## Notes

- This utility requires the Excel file "MWTC UTILITY BILLS - DASHBOARD.xlsm" in the same directory
- It will only work with the "COLEVILLE ELECTRICITY" sheet in that file
- The API token may need to be updated periodically in `liberty_api.py`
- When fetching data, the utility checks for existing entries to avoid duplicates 