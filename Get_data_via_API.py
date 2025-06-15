# This script retrieves asset data from a Supabase REST API and exports it as a CSV file.

# Import library
from supabase import create_client, Client
import requests
import csv

# --- Supabase credentials and endpoint configuration ---
SUPABASE_URL = "https://pvgaaikztozwlfhyrqlo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2Z2FhaWt6dG96d2xmaHlycWxvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc4NDE2MjUsImV4cCI6MjA2MzQxNzYyNX0.iAqMXnJ_sJuBMtA6FPNCRcYnKw95YkJvY3OhCIZ77vI"

endpoint = f"{SUPABASE_URL}/rest/v1/assets?select=*"


# --- Set request headers with API key and authorization ---
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Accept": "application/json"
}

# --- Send GET request to Supabase REST API to retrieve asset data ---
response = requests.get(endpoint, headers=headers)

if response.status_code == 200:
    data = response.json()

    # Export csv file
    with open("assets_data.csv", mode="w", newline="", encoding="utf-8") as file:
        if data:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            print("csv data extracted : assets_data.csv")
        else:
            print("failed to extract csv data")
else:
    print("error", response.status_code, response.text)
