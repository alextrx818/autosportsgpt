import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api():
    api_key = os.getenv('SPORTS_API_KEY')
    api_host = os.getenv('SPORTS_API_HOST')
    
    base_url = f"https://{api_host}"
    url = f"{base_url}/v3/events/inplay"
    
    params = {
        'token': api_key,
        'sport_id': 1  # Soccer
    }
    
    print("Testing API connection...")
    print(f"Using API Key: {api_key}")
    print(f"Using Host: {api_host}")
    print(f"Full URL: {url}")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nStatus code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Connection successful!")
            print(f"Number of live events: {len(data.get('results', []))}")
            if data.get('results'):
                first_event = data['results'][0]
                print("\nExample event:")
                print(f"League: {first_event.get('league', {}).get('name', 'N/A')}")
                print(f"Match: {first_event.get('home', {}).get('name', 'N/A')} vs {first_event.get('away', {}).get('name', 'N/A')}")
        else:
            print(f"Failed. Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()
