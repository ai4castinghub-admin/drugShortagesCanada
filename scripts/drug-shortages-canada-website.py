import requests
import pandas as pd
from datetime import datetime
import time
import os
 
LOGIN_URL = "https://www.drugshortagescanada.ca/api/v1/login"
SEARCH_URL = "https://www.drugshortagescanada.ca/api/v1/search"
 
credentials = {'email': EMAILDRUGSHORTAGESCANADA, 'password': PASSDRUGSHORTAGESCANADA}

session = requests.Session()
response = session.post(LOGIN_URL, data=credentials)
response.raise_for_status()
 
auth_token = response.headers.get("auth-token")
if not auth_token:
    raise Exception("Authentication token not found.")
 
headers = {
    "auth-token": auth_token,
    "Content-Type": "application/json"
}
 
#paginated fetching using offset
all_results = []
offset = 0
limit = 100  # enforced by server
 
print("Fetching all drug shortage reports since 2022...")
 
while True:
    params = {
        "type": "shortage",
        "order": "desc",
        "orderby": "updated_date",
        "lang": "en",
        "limit": limit,
        "offset": offset
    }
 
    r = session.get(SEARCH_URL, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()
 
    records = data.get("data", [])
    if not records:
        print("No more records.")
        break
 
    all_results.extend(records)
    print(f"Fetched {len(records)} records at offset {offset}")
 
    remaining = data.get("remaining", 0)
    if remaining <= 0:
        break
 
    offset += limit
    time.sleep(2)  
 

df = pd.DataFrame(all_results)

def save_dataframe_safely(df, filepath):
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        if df.shape[1] == existing_df.shape[1]:
            # Same number of columns — concatenate and deduplicate
            combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates()
            combined_df.to_csv(filepath, index=False)
            print(f"DataFrame appended and saved to {filepath}")
        else:
            # Mismatched column count — save with new name
            base, ext = os.path.splitext(filepath)
            new_filepath = f"{base}_new{ext}"
            df.to_csv(new_filepath, index=False)
            print(f"Column mismatch. DataFrame saved as {new_filepath}")
    else:
        # File doesn't exist — just save
        df.to_csv(filepath, index=False)
        print(f"DataFrame saved to {filepath}")

save_dataframe_safely(df, "drug-shortages-data/data.csv")     
#df.to_csv("drug-shortages-data/data.csv", index=False)
#print(f"Saved {len(df)} records to drug_shortages.csv")