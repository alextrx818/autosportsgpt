import os
import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Configure logging
logger.add("sports_monitor.log", rotation="1 day")

# Sport configurations with emojis
SPORTS = {
    1: {'name': 'Soccer', 'emoji': '⚽'},
    18: {'name': 'Basketball', 'emoji': '🏀'},
    13: {'name': 'Tennis', 'emoji': '🎾'},
    91: {'name': 'Volleyball', 'emoji': '🏐'},
    17: {'name': 'Ice Hockey', 'emoji': '🏒'},
    78: {'name': 'Handball', 'emoji': '🤾'},
    16: {'name': 'Baseball', 'emoji': '⚾'},
    12: {'name': 'American Football', 'emoji': '🏈'},
    14: {'name': 'Snooker', 'emoji': '🎱'},
    15: {'name': 'Darts', 'emoji': '🎯'},
    92: {'name': 'Table Tennis', 'emoji': '🏓'},
    94: {'name': 'Badminton', 'emoji': '🏸'},
    19: {'name': 'Rugby League', 'emoji': '🏉'},
    36: {'name': 'Australian Rules', 'emoji': '🏉'},
    95: {'name': 'Beach Volleyball', 'emoji': '🏐'}
}

class SportsMonitorBot:
    def __init__(self):
        self.api_key = os.getenv('SPORTS_API_KEY')
        self.api_host = os.getenv('SPORTS_API_HOST')

    def is_esport(self, league_name):
        """Check if the league is an e-sport league"""
        esport_keywords = ['esoccer', 'esports', 'e-', 'cyber', 'ebasketball', 'etennis', 'evolleyball', 'ehockey']
        league_name = league_name.lower()
        return any(keyword in league_name for keyword in esport_keywords)

    def get_period(self, match, sport_id):
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

    def format_match(self, match, sport_id):
        """Format match with minimal essential information"""
        league = match.get('league', {}).get('name', 'Unknown League')
        home = match.get('home', {}).get('name', 'Unknown')
        away = match.get('away', {}).get('name', 'Unknown')
        score = match.get('ss', 'vs')
        timer = match.get('timer', {})
        time = timer.get('tm', '0')
        period = self.get_period(match, sport_id)
        
        sport_info = SPORTS.get(sport_id, {'emoji': '🎮'})
        return f"{league}\n{sport_info['emoji']} {home} {score} {away}\n⏰ {time}' ({period})\n"

    async def fetch_live_matches(self):
        """Fetch live matches from the API for all sports"""
        url = f"https://{self.api_host}/v3/events/inplay"
        all_matches = []
        
        for sport_id, sport_info in SPORTS.items():
            try:
                params = {
                    'token': self.api_key,
                    'sport_id': sport_id
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') == 1:
                        matches = data.get('results', [])
                        # Filter out e-sports matches
                        real_matches = [m for m in matches if not self.is_esport(m.get('league', {}).get('name', ''))]
                        
                        if real_matches:
                            logger.info(f"\n📱 Live {sport_info['name']} Matches ({len(real_matches)} total)\n")
                            
                            # Sort matches by time (descending)
                            real_matches.sort(key=lambda x: int(x.get('timer', {}).get('tm', 0)), reverse=True)
                            
                            for match in real_matches:
                                logger.info(self.format_match(match, sport_id))
                            
                            all_matches.extend(real_matches)
                            # Pause between sports to make it easier to read
                            await asyncio.sleep(2)
                    else:
                        logger.error(f"❌ API returned success = 0 for {sport_id}")
                else:
                    logger.error(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching {sport_info['name']} matches: {str(e)}")
                
        return all_matches

async def run_monitoring():
    bot = SportsMonitorBot()
    while True:
        await bot.fetch_live_matches()
        await asyncio.sleep(60)  # Wait for 60 seconds before next update

if __name__ == "__main__":
    logger.info("Starting Sports Monitor Bot...")
    import asyncio
    asyncio.run(run_monitoring())
