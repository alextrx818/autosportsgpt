import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

def test_upcoming_events():
    api_key = os.getenv('SPORTS_API_KEY')
    
    # Test Upcoming Events
    print("Testing Upcoming Events API:")
    try:
        url = "https://api.b365api.com/v3/events/upcoming"
        params = {
            'token': api_key,
            'sport_id': 1  # Soccer
        }
        
        print(f"\nMaking request to: {url}")
        print(f"Parameters: sport_id=1, token={api_key}")
        
        response = requests.get(url, params=params)
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Upcoming Events:")
            
            if 'results' in data:
                events = data['results']
                print(f"\nFound {len(events)} upcoming events")
                
                if events:
                    print("\nFirst event complete data structure:")
                    print(json.dumps(events[0], indent=2))
                    
                    print("\nFirst 5 events summary:")
                    for event in events[:5]:
                        print("\n-------------------")
                        # Print all available fields
                        for key, value in event.items():
                            print(f"{key}: {value}")
            else:
                print("No 'results' found in response")
                print(f"Full response: {data}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_upcoming_events()
