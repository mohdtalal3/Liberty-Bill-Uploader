#!/usr/bin/env python
"""
Simplified Liberty Bill Uploader
Automatically fetches and uploads utility bill data for all accounts
"""

import xlwings as xw
import pandas as pd
from datetime import datetime
import re
import time
from liberty_api import get_electricity_data

def extract_account_number(building_name_text):
    """Extract account number from the building name text"""
    if not building_name_text:
        return None
    
    match = re.search(r'Account Number:\s*(\d+)', str(building_name_text))
    if match:
        return match.group(1)
    return None

def format_date_for_comparison(date_obj):
    """Format a date object to a standard string format for comparison"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%Y-%m-%d")
    return str(date_obj)

def check_existing_entry(data, account_number, check_date):
    """
    Check if an entry already exists for the given account number and date
    Using string comparison to avoid datetime type issues
    """
    check_date_str = format_date_for_comparison(check_date)
    
    for entry in data:
        if entry['account_number'] == account_number:
            entry_date_str = format_date_for_comparison(entry['date'])
            if entry_date_str == check_date_str:
                return True
    
    return False

def main(token):
    try:
        print("===== Liberty Bill Uploader =====")
        
        # Get the start date (will be used as both start and end date)
        while True:
            start_date_str = input("Enter date to process (YYYY-MM-DD): ")
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        
        # Open the Excel file
        print("\nOpening Excel file...")
        wb = xw.Book("MWTC UTILITY BILLS - DASHBOARD.xlsm")
        sheet = wb.sheets["COLEVILLE ELECTRICITY"]
        
        # Get dimensions
        last_row = sheet.used_range.last_cell.row
        
        # Read headers to identify columns
        headers = sheet.range("A1:Z1").value
        
        # Find indices of important columns
        date_col_idx = headers.index("Date") if "Date" in headers else 0
        building_col_idx = headers.index("Building Name") if "Building Name" in headers else 3
        usage_col_idx = headers.index("Usage") if "Usage" in headers else 6
        rate_col_idx = headers.index("Rate ($/kWh))") if "Rate ($/kWh))" in headers else 7
        cost_col_idx = headers.index("Cost ($)") if "Cost ($)" in headers else 8
        sqft_col_idx = headers.index("SQFT") if "SQFT" in headers else 9
        
        # Read all data from the sheet
        data = []
        account_numbers = set()
        account_to_building = {}
        account_to_sqft = {}
        
        print("Extracting data and account numbers...")
        for i in range(2, last_row + 1):
            row_data = sheet.range(f"A{i}:{chr(65 + max(building_col_idx, usage_col_idx, rate_col_idx, cost_col_idx, sqft_col_idx))}{i}").value
            
            # Extract account number from building name
            building_name = row_data[building_col_idx] if building_col_idx < len(row_data) else None
            account_number = extract_account_number(building_name)
            
            # Get SQFT value
            sqft_value = row_data[sqft_col_idx] if sqft_col_idx < len(row_data) else None
            
            if account_number:
                account_numbers.add(account_number)
                account_to_building[account_number] = building_name
                if sqft_value:
                    account_to_sqft[account_number] = sqft_value
                
            data.append({
                'row': i,
                'date': row_data[date_col_idx] if date_col_idx < len(row_data) else None,
                'building_name': building_name,
                'account_number': account_number,
                'usage': row_data[usage_col_idx] if usage_col_idx < len(row_data) else None,
                'rate': row_data[rate_col_idx] if rate_col_idx < len(row_data) else None,
                'cost': row_data[cost_col_idx] if cost_col_idx < len(row_data) else None,
                'sqft': sqft_value
            })
        
        # Get all accounts
        account_numbers_list = sorted(list(account_numbers))
        print(f"Found {len(account_numbers_list)} accounts to process")
        
        # Process each account for the specified date
        new_entries = 0
        skipped_entries = 0
        error_entries = 0
        
        for account_number in account_numbers_list:
            date_str = start_date_str
            print(f"\nProcessing account {account_number} for date {date_str}...")
            
            # Fetch data from API
            usage_data = get_electricity_data(account_number, date_str,token)
            
            if not usage_data:
                print(f"Error: Failed to retrieve data for account {account_number} on {date_str}")
                error_entries += 1
                continue
            
            # Get the reading date from the API response
            new_date = usage_data['reading_date']
            
            # Check if an entry for this account and date already exists
            if check_existing_entry(data, account_number, new_date):
                print(f"Skipping: Entry already exists for account {account_number} on {format_date_for_comparison(new_date)}")
                skipped_entries += 1
                continue
            
            # Get building name for this account
            building_info = account_to_building.get(account_number)
            if not building_info:
                print(f"Error: Could not find building information for account {account_number}")
                error_entries += 1
                continue
            
            # Extract values from API data
            new_usage = usage_data['usage']
            
            # Calculate rate from usage and cost
            if new_usage > 0:
                new_rate = usage_data['cost'] / new_usage
            else:
                new_rate = 0
                
            new_cost = usage_data['cost']
            reading_to_date = usage_data['reading_to']
            
            # Add the new row to Excel
            new_row = last_row + 1 + new_entries
            
            # Copy data format from a previous row for the same account
            template_row = None
            for row in data:
                if row['account_number'] == account_number:
                    template_row = row['row']
                    break
            
            if template_row:
                # Copy row format
                sheet.range(f"A{template_row}:{chr(65 + max(date_col_idx, building_col_idx, usage_col_idx, rate_col_idx, cost_col_idx, sqft_col_idx))}{template_row}").copy(sheet.range(f"A{new_row}"))
                
                # Update with new values
                sheet.range(f"{chr(65 + date_col_idx)}{new_row}").value = new_date
                
                # Add reading_to date to the building name for reference
                building_info_with_dates = f"{building_info}"
                sheet.range(f"{chr(65 + building_col_idx)}{new_row}").value = building_info_with_dates
                
                sheet.range(f"{chr(65 + usage_col_idx)}{new_row}").value = new_usage
                sheet.range(f"{chr(65 + rate_col_idx)}{new_row}").value = new_rate
                sheet.range(f"{chr(65 + cost_col_idx)}{new_row}").value = new_cost
                
                # Get SQFT from the template row (it should remain the same for the account)
                sqft_value = account_to_sqft.get(account_number)
                if sqft_value:
                    sheet.range(f"{chr(65 + sqft_col_idx)}{new_row}").value = sqft_value
                
                print(f"Added entry for account {account_number} on {format_date_for_comparison(new_date)}")
                new_entries += 1
                
                # Add to data list for duplicate checking
                data.append({
                    'row': new_row,
                    'date': new_date,
                    'building_name': building_info,
                    'account_number': account_number,
                    'usage': new_usage,
                    'rate': new_rate,
                    'cost': new_cost,
                    'sqft': sqft_value
                })
            else:
                print(f"Error: Could not find a template row for account {account_number}")
                error_entries += 1
            
            # Sleep to avoid overloading the API
            time.sleep(5)
        
        # Summary
        print("\n--- Processing Complete ---")
        print(f"New entries added: {new_entries}")
        print(f"Entries skipped (already exist): {skipped_entries}")
        print(f"Errors: {error_entries}")
        
        if new_entries > 0:
            print("\nSaving changes to Excel file...")
            wb.save()
            print("Changes saved successfully.")
        else:
            print("\nNo changes to save.")
        
        # Close the workbook
        wb.close()
        
    except Exception as e:
        print(f"Error: {e}")
        try:
            wb.close()
        except:
            pass

if __name__ == "__main__":
    main() 