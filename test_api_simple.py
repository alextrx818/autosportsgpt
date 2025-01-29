import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SPORTS = {
    1: {'name': 'Soccer', 'emoji': '⚽'},
    18: {'name': 'Basketball', 'emoji': '🏀'},
    13: {'name': 'Tennis', 'emoji': '🎾'},
    91: {'name': 'Volleyball', 'emoji': '🏐'},
    17: {'name': 'Ice Hockey', 'emoji': '🏒'}
}

def is_esport(league_name):
    """Check if the league is an e-sport league"""
    esport_keywords = ['esoccer', 'esports', 'e-', 'cyber', 'ebasketball', 'etennis', 'evolleyball', 'ehockey']
    league_name = league_name.lower()
    return any(keyword in league_name for keyword in esport_keywords)

def get_period(match, sport_id):
    """Get the current period of the match"""
    time_status = match.get('time_status')
    timer = match.get('timer', {})
    time = timer.get('tm', '0')
    
    if time_status == '1':  # Match is live
        if sport_id == 1:  # Soccer
            if int(time) <= 45:
                return '1H'
            else:
                return '2H'
        elif sport_id == 18:  # Basketball
            quarter = match.get('timer', {}).get('q', '1')
            return f'Q{quarter}'
        elif sport_id == 13:  # Tennis
            # Get the current score which includes set information
            score = match.get('ss', '')
            if score:
                # Count the number of completed sets by counting commas
                completed_sets = score.count(',')
                # Current set is the number of completed sets + 1
                current_set = completed_sets + 1
                return f'Set {current_set}'
        elif sport_id == 91:  # Volleyball
            set_info = match.get('timer', {}).get('set', '1')
            return f'Set {set_info}'
        elif sport_id == 17:  # Ice Hockey
            period = match.get('timer', {}).get('p', '1')
            return f'P{period}'
    return '-'

def format_match(match, sport_id):
    """Format match with minimal essential information"""
    league = match.get('league', {}).get('name', 'Unknown League')
    home = match.get('home', {}).get('name', 'Unknown')
    away = match.get('away', {}).get('name', 'Unknown')
    score = match.get('ss', 'vs')
    timer = match.get('timer', {})
    time = timer.get('tm', '0')
    period = get_period(match, sport_id)
    
    sport_info = SPORTS.get(sport_id, {'emoji': '🎮'})
    return f"{league}\n{sport_info['emoji']} {home} {score} {away}\n⏰ {time}' ({period})\n"

def fetch_live_matches(sport_id):
    """Fetch live matches for a specific sport"""
    api_key = os.getenv('SPORTS_API_KEY')
    api_host = os.getenv('SPORTS_API_HOST')
    
    url = f"https://{api_host}/v3/events/inplay"
    params = {
        'token': api_key,
        'sport_id': sport_id
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') == 1:
                matches = data.get('results', [])
                # Filter out e-sports matches
                real_matches = [m for m in matches if not is_esport(m.get('league', {}).get('name', ''))]
                sport_info = SPORTS.get(sport_id, {'name': 'Unknown'})
                print(f"\n📱 Live {sport_info['name']} Matches ({len(real_matches)} total)\n")
                
                # Sort matches by time (descending)
                real_matches.sort(key=lambda x: int(x.get('timer', {}).get('tm', 0)), reverse=True)
                
                for match in real_matches:
                    print(format_match(match, sport_id))
            else:
                print(f"\n❌ API returned success = 0 for {sport_id}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error connecting to API: {str(e)}")

def test_api_connection():
    """Test API connection for multiple sports"""
    # Fetch matches for each sport
    for sport_id in SPORTS.keys():
        fetch_live_matches(sport_id)

if __name__ == "__main__":
    test_api_connection()
