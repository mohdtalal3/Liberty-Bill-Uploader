# Liberty Bill Uploader

A simplified utility for automating the management of electricity billing data from Liberty Energy & Water. This tool automatically processes and uploads billing data to an Excel spreadsheet by fetching data from the Liberty API.

## Features

- Automatically extracts account numbers from the Excel sheet
- Fetches electricity usage data from Liberty's API for all accounts
- Adds new entries to the Excel sheet with proper formatting
- Checks for duplicate entries to avoid data redundancy
- Preserves formatting of existing Excel data

## Requirements

- Python 3.6+
- xlwings
- pandas
- requests

## Installation

1. Clone or download this repository
2. Install required packages:

For windows:
   ```bash
   pip install xlwings pandas requests seleniumbase
   ```
For Mac:

   ```bash
   pip3 install xlwings pandas requests seleniumbase
   ```
## Usage

Run the utility script:

```bash
python bill_utility.py
```
For Mac:

```bash
python3 bill_utility.py
```

The utility will:
1. Ask you to enter a date to process in YYYY-MM-DD format
2. Automatically find all account numbers in the Excel file
3. Fetch data from the Liberty API for each account for the specified date
4. Add entries to the Excel file, skipping any that already exist
5. Save changes automatically when complete

## Files

- `bill_utility.py`: Main entry point for the utility
- `simplified_uploader.py`: Implementation of the simplified uploader
- `liberty_api.py`: API interaction with Liberty Energy & Water

## Notes

- This utility requires the Excel file "MWTC UTILITY BILLS - DASHBOARD.xlsm" in the same directory
- It will only work with the "COLEVILLE ELECTRICITY" sheet in that file
- The API token may need to be updated periodically in `liberty_api.py`
- When fetching data, the utility checks for existing entries to avoid duplicates 