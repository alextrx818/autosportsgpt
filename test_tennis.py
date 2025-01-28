import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tennis_matches():
    api_key = os.getenv('SPORTS_API_KEY')
    
    print("\n🎾 Live Tennis Matches:")
    print("=" * 50)
    
    try:
        url = "https://api.b365api.com/v3/events/inplay"
        params = {
            'token': api_key,
            'sport_id': 13  # Tennis
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data:
                events = data['results']
                print(f"\nFound {len(events)} live tennis matches\n")
                
                # Sort matches by league
                matches_by_league = {}
                for event in events:
                    league_name = event.get('league', {}).get('name', 'Unknown League')
                    if league_name not in matches_by_league:
                        matches_by_league[league_name] = []
                    matches_by_league[league_name].append(event)
                
                # Print matches organized by league
                for league_name, matches in matches_by_league.items():
                    print(f"\n📍 {league_name}")
                    print("-" * 50)
                    
                    for match in matches:
                        home = match.get('home', {}).get('name', 'Unknown')
                        away = match.get('away', {}).get('name', 'Unknown')
                        score = match.get('ss', 'No score')
                        
                        # Get detailed scores if available
                        scores = match.get('scores', {})
                        sets = []
                        for i in range(1, 6):  # Tennis can have up to 5 sets
                            if str(i) in scores:
                                set_score = scores[str(i)]
                                sets.append(f"{set_score.get('home', '0')}-{set_score.get('away', '0')}")
                        
                        print(f"\n🎾 {home} vs {away}")
                        print(f"Current Score: {score}")
                        if sets:
                            print(f"Sets: {', '.join(sets)}")
                        
                        # Add statistics if available
                        stats = match.get('stats', {})
                        if stats:
                            print("Statistics:")
                            for stat_name, stat_values in stats.items():
                                if isinstance(stat_values, list) and len(stat_values) == 2:
                                    print(f"  {stat_name}: {stat_values[0]} - {stat_values[1]}")
            else:
                print("No tennis matches found in the response")
        else:
            print(f"❌ Failed to get tennis matches. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_tennis_matches()
