import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Define all sports IDs
SPORTS = {
    1: 'Soccer',
    18: 'Basketball',
    13: 'Tennis',
    91: 'Volleyball',
    78: 'Handball',
    16: 'Baseball',
    17: 'Ice Hockey',
    12: 'American Football',
    14: 'Snooker',
    15: 'Darts',
    92: 'Table Tennis',
    94: 'Badminton',
    19: 'Rugby League',
    36: 'Australian Rules',
    95: 'Beach Volleyball'
}

def test_live_sports():
    api_key = os.getenv('SPORTS_API_KEY')
    
    print("Testing Live Events for All Sports:")
    
    for sport_id, sport_name in SPORTS.items():
        try:
            url = "https://api.b365api.com/v3/events/inplay"
            params = {
                'token': api_key,
                'sport_id': sport_id
            }
            
            print(f"\n\n{'='*50}")
            print(f"Checking {sport_name} (ID: {sport_id})")
            print('='*50)
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data:
                    events = data['results']
                    print(f"Found {len(events)} live events")
                    
                    if events:
                        print("\nLive matches:")
                        for event in events:
                            print("\n-------------------")
                            print(f"League: {event.get('league', {}).get('name')}")
                            print(f"Match: {event.get('home', {}).get('name')} vs {event.get('away', {}).get('name')}")
                            print(f"Score: {event.get('ss')}")
                            
                            # Show detailed scores if available
                            if 'scores' in event:
                                print("Detailed scores:")
                                for period, scores in event['scores'].items():
                                    print(f"  Period {period}: {scores.get('home')} - {scores.get('away')}")
                            
                            # Show timer information
                            timer = event.get('timer', {})
                            print(f"Time: {timer.get('tm')}:{timer.get('ts', 0):02d}")
                            
                            # Show statistics if available
                            if 'stats' in event:
                                print("\nStatistics:")
                                stats = event['stats']
                                for stat_name, stat_values in stats.items():
                                    if isinstance(stat_values, list) and len(stat_values) == 2:
                                        print(f"  {stat_name}: {stat_values[0]} - {stat_values[1]}")
                    else:
                        print("No live events")
                else:
                    print("No 'results' found in response")
            else:
                print(f"❌ Failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_live_sports()
