import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api():
    api_key = os.getenv('SPORTS_API_KEY')
    api_host = os.getenv('SPORTS_API_HOST')
    
    base_url = f'https://{api_host}'
    url = f"{base_url}/v3/events/inplay"
    
    params = {
        'token': api_key,
        'sport_id': 1  # Soccer
    }
    
    print("Testing API connection...")
    try:
        response = requests.get(url, params=params)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Connection successful!")
            print(f"Number of live events: {len(data.get('results', []))}")
        else:
            print(f"Failed. Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
