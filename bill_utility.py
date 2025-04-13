from seleniumbase import SB
import os
import json
from get_token import extract_token
from simplified_uploader import main

full_path = os.path.abspath("chromedatabills")

# Initialize the SeleniumBase context manager with Chrome options
with SB(uc=True, headless=False, user_data_dir=full_path,log_cdp_events=True) as sb:
    # Open the target website
    sb.open("https://myaccount.libertyenergyandwater.com/portal/#/login?LUCA")
    input("Press Enter to continue...")
    cdp_logs = sb.driver.get_log("performance")
    file_path = os.path.abspath("cdp_logs.json")
    with open(file_path, 'w') as f:
        json.dump(cdp_logs, f, indent=4)
    token= extract_token(file_path)
    main(token)