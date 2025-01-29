import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_api_connection():
    api_key = os.getenv('SPORTS_API_KEY')
    api_host = os.getenv('SPORTS_API_HOST')
    
    base_url = f'https://{api_host}'
    
    print("Testing Bet365 API Connection...\n")
    
    # 1. Test In-Play Events
    print("1. Testing In-Play Events:")
    try:
        url = f"{base_url}/v3/events/inplay"
        params = {
            'token': api_key,
            'sport_id': 1  # Soccer
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Success! In-Play Events:")
            if 'results' in data:
                print(f"Found {len(data['results'])} live events")
                if data['results']:
                    print("\nExample live event:")
                    event = data['results'][0]
                    print(f"  League: {event.get('league', {}).get('name', 'N/A')}")
                    print(f"  Match: {event.get('home', {}).get('name', 'N/A')} vs {event.get('away', {}).get('name', 'N/A')}")
                    print(f"  Score: {event.get('ss', 'N/A')}")
                    print(f"  Time: {event.get('time', 'N/A')}")
        else:
            print(f"[FAILED] Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")

    # 2. Test Upcoming Events
    print("\n2. Testing Upcoming Events:")
    try:
        url = f"{base_url}/v3/events/upcoming"
        params = {
            'token': api_key,
            'sport_id': 1  # Soccer
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Success! Upcoming Events:")
            if 'results' in data:
                print(f"Found {len(data['results'])} upcoming events")
                if data['results']:
                    print("\nExample upcoming events:")
                    for event in data['results'][:3]:
                        event_time = datetime.fromtimestamp(int(event.get('time', 0)))
                        print(f"  {event.get('home', {}).get('name', 'N/A')} vs {event.get('away', {}).get('name', 'N/A')}")
                        print(f"  Time: {event_time}")
                        print(f"  League: {event.get('league', {}).get('name', 'N/A')}\n")
        else:
            print(f"[FAILED] Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")

    # 3. Test Pre-match Odds
    print("\n3. Testing Pre-match Odds:")
    try:
        url = f"{base_url}/v3/event/odds"
        # Get the first upcoming event ID from previous call
        if 'data' in locals() and 'results' in data and data['results']:
            event_id = data['results'][0].get('id')
            params = {
                'token': api_key,
                'event_id': event_id
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                odds_data = response.json()
                print("[SUCCESS] Success! Pre-match Odds:")
                if 'results' in odds_data:
                    print(f"Found odds for event ID: {event_id}")
                    if odds_data['results'].get('odds'):
                        print("\nExample odds:")
                        odds = odds_data['results']['odds']
                        for market in list(odds.items())[:2]:  # Show first 2 markets
                            print(f"  Market: {market[0]}")
                            for outcome in market[1]:
                                print(f"    {outcome.get('name', 'N/A')}: {outcome.get('odds', 'N/A')}")
            else:
                print(f"[FAILED] Failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")

if __name__ == "__main__":
    test_api_connection()
