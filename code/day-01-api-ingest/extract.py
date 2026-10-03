import requests
import json
import os
from datetime import datetime

def fetch_and_save_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=22.6011&longitude=88.3178&current_weather=true"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        os.makedirs("data/raw", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/raw/weather_{timestamp}.json"
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Extracted raw data to {filepath}")
    else:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")

if __name__ == "__main__":
    fetch_and_save_weather()