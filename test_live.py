import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_live_events():
    api_key = os.getenv('SPORTS_API_KEY')
    
    print("Testing Live Events API:")
    try:
        url = "https://api.b365api.com/v3/events/inplay"
        params = {
            'token': api_key,
            'sport_id': 1  # Soccer
        }
        
        print(f"\nMaking request to: {url}")
        response = requests.get(url, params=params)
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Live Events:")
            
            if 'results' in data:
                events = data['results']
                print(f"\nFound {len(events)} live events")
                
                if events:
                    print("\nFirst live event complete data structure:")
                    print(json.dumps(events[0], indent=2))
                    
                    print("\nFirst 3 live events:")
                    for event in events[:3]:
                        print("\n-------------------")
                        print(f"Event ID: {event.get('id')}")
                        print(f"League: {event.get('league', {}).get('name')}")
                        print(f"Teams: {event.get('home', {}).get('name')} vs {event.get('away', {}).get('name')}")
                        print(f"Score: {event.get('ss')}")  # Live score
                        print(f"Timer: {event.get('timer', {}).get('tm')}")  # Match time
                        print(f"Period: {event.get('timer', {}).get('tt')}")  # Period/Half
                        
                        # Print all score-related fields
                        print("\nAll score fields:")
                        for key, value in event.items():
                            if any(score_key in key.lower() for score_key in ['score', 'ss', 'timer']):
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
    test_live_events()
