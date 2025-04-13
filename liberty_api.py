import requests
import json
from datetime import datetime

def fetch_electric_usage(account_number, date_str,token):
    """
    Fetch electricity usage data from the Liberty API for a specific account and date
    
    Args:
        account_number (str): The account number to query
        date_str (str): Date in YYYY-MM-DD format
        
    Returns:
        dict: The API response data or None if the request failed
    """
    # URL for Liberty API
    url = "https://libertycf2-svc.smartcmobile.com/UsageAPI/api/V1/Electric"
    
    # Query parameters (payload for GET)
    params = {
        "AccountNumber": account_number,
        "From": date_str,
        "To": date_str,
        "Uom": "",
        "Periodicity": "MO",
        "IsNonAmi": "true"
    }
    
    # Headers
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "origin": "https://myaccount.libertyenergyandwater.com",
        "referer": "https://myaccount.libertyenergyandwater.com/",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    
    try:
        # Send GET request
        response = requests.get(url, headers=headers, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully fetched data for account {account_number} on {date_str}")
            return data
        else:
            print(f"Error fetching data: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred during API request: {e}")
        return None

def extract_usage_data(api_response):
    """
    Extract the relevant usage data from the API response
    
    Args:
        api_response (dict): The API response from fetch_electric_usage
        
    Returns:
        dict: Dictionary containing extracted data or None if data is missing
    """
    if not api_response or "Result" not in api_response:
        return None
    
    try:
        # Extract the electric usage data from the response
        electric_usages = api_response["Result"]["electricUsages"]
        
        if not electric_usages or len(electric_usages) == 0:
            print("No usage data found in the API response")
            return None
        
        usage_data = electric_usages[0]
        
        # Format dates properly
        reading_date = datetime.fromisoformat(usage_data["readingDate"].replace("Z", ""))
        reading_from = datetime.fromisoformat(usage_data["readingFrom"].replace("Z", ""))
        reading_to = datetime.fromisoformat(usage_data["readingTo"].replace("Z", ""))
        
        # Extract and return the relevant data
        return {
            "account_number": usage_data["accountNumber"],
            "meter_number": usage_data["meterNumber"],
            "reading_date": reading_date,
            "reading_from": reading_from,
            "reading_to": reading_to,
            "usage": usage_data["usageValue"],
            "cost": usage_data["usageCost"],
            "uom": usage_data["uom"]
        }
    except Exception as e:
        print(f"Error extracting usage data: {e}")
        return None

def get_electricity_data(account_number, date_str,token):
    """
    Fetch and extract electricity usage data for a given account and date
    
    Args:
        account_number (str): The account number to query
        date_str (str): Date in YYYY-MM-DD format
        
    Returns:
        dict: Dictionary containing extracted usage data or None if data is missing
    """
    # Fetch data from the API
    api_response = fetch_electric_usage(account_number, date_str,token)
    
    if not api_response:
        return None
    
    # Extract and return the usage data
    return extract_usage_data(api_response)

# Test function
if __name__ == "__main__":
    # Example usage
    account_number = "200008980241"
    date_str = "2025-03-13"
    
    data = get_electricity_data(account_number, date_str)
    
    if data:
        print(f"Account: {data['account_number']}")
        print(f"Meter: {data['meter_number']}")
        print(f"Reading Date: {data['reading_date']}")
        print(f"From: {data['reading_from']} to {data['reading_to']}")
        print(f"Usage: {data['usage']} {data['uom']}")
        print(f"Cost: ${data['cost']}")
    else:
        print("Failed to retrieve usage data") 