import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
import telegram
from sports_gpt_handler import SportsGPTHandler
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logger.add("sports_monitor.log", rotation="1 day")

class SportsMonitorBot:
    def __init__(self):
        self.api_key = os.getenv('SPORTS_API_KEY')
        self.api_host = os.getenv('SPORTS_API_HOST')
        self.telegram_bot = None
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.telegram_bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        
        self.last_events = {}  # Store last known state of events
        # Temporarily disable GPT handler
        # self.gpt_handler = SportsGPTHandler()

    async def fetch_live_matches(self):
        """Fetch live matches from the API for all sports"""
        url = f"https://{self.api_host}/v3/events/inplay"
        all_matches = []
        
        # List of sport IDs from sports_config.py
        sport_ids = {
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
        
        logger.info("\n🏆 LIVE SPORTS MONITOR - ALL CURRENT MATCHES 🏆")
        logger.info("=" * 80)
        
        for sport_id, sport_name in sport_ids.items():
            try:
                params = {
                    'token': self.api_key,
                    'sport_id': sport_id
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    matches = data.get('results', [])
                    if matches:
                        logger.info(f"\n\n🎯 {sport_name.upper()} - {len(matches)} live matches")
                        logger.info("=" * 80)
                        
                        # Group matches by league
                        league_matches = {}
                        for match in matches:
                            league = match.get('league', {}).get('name', 'Unknown League')
                            if league not in league_matches:
                                league_matches[league] = []
                            league_matches[league].append(match)
                        
                        # Display ALL matches by league
                        for league, league_matches_list in sorted(league_matches.items()):
                            logger.info(f"\n📍 {league}")
                            for match in sorted(league_matches_list, key=lambda x: x.get('time', 0)):
                                home = match.get('home', {}).get('name', 'Unknown')
                                away = match.get('away', {}).get('name', 'Unknown')
                                score = match.get('ss', 'No score')
                                time = match.get('time', 'No time')
                                logger.info(f"   • {home} vs {away}")
                                logger.info(f"     Score: {score}")
                        
                        logger.info("\n" + "=" * 80)
                        all_matches.extend(matches)
                        # Pause between sports to make it easier to read
                        await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error fetching {sport_name} matches: {str(e)}")
                
        logger.info(f"\n📊 Total live matches across all sports: {len(all_matches)}")
        logger.info("=" * 80 + "\n")
        return all_matches

    async def process_match_updates(self, matches):
        """Process updates for each live match"""
        for match in matches:
            current_state = {
                'score': match.get('ss', 'No score'),
                'time': match.get('time', 'No time')
            }
            
            await self.handle_match_update(match, current_state)

    async def get_api_suggestions(self, matches):
        """Get GPT suggestions for API queries"""
        if not matches:
            return []
        
        # Format match data for GPT
        match_descriptions = [
            f"{m.get('home', {}).get('name', 'Unknown')} vs {m.get('away', {}).get('name', 'Unknown')} ({m.get('league', {}).get('name', 'Unknown League')})"
            for m in matches[:5]  # Limit to 5 matches to avoid token limits
        ]
        
        # Temporarily disable GPT suggestions
        # return await self.gpt_handler.suggest_api_queries(matches)

    async def handle_match_update(self, match, current_state):
        """Handle updates for a specific match"""
        match_id = match.get('id')
        if not match_id:
            return
        
        if match_id not in self.last_events:
            # New match detected
            message = self.create_update_message(match, "NEW_MATCH")
            self.last_events[match_id] = current_state
        else:
            # Check for updates
            last_state = self.last_events[match_id]
            if current_state != last_state:
                message = self.create_update_message(match, "UPDATE")
                self.last_events[match_id] = current_state
            else:
                return  # No update needed

        # Send update via Telegram if configured
        if self.telegram_bot and message:
            try:
                await self.telegram_bot.send_message(chat_id=self.chat_id, text=message)
            except Exception as e:
                logger.error(f"Error sending Telegram message: {str(e)}")

    def create_update_message(self, match, update_type):
        """Create a formatted message for match updates"""
        try:
            home_team = match.get('home', {}).get('name', 'Unknown')
            away_team = match.get('away', {}).get('name', 'Unknown')
            league = match.get('league', {}).get('name', 'Unknown League')
            score = match.get('ss', 'No score')
            time = match.get('time', 'No time')
            
            if update_type == "NEW_MATCH":
                return f"🆕 New Match:\n{home_team} vs {away_team}\n📊 {score}\n⚽ {league}\n⏰ {time}"
            else:
                return f"📢 Match Update:\n{home_team} vs {away_team}\n📊 {score}\n⚽ {league}\n⏰ {time}"
        except Exception as e:
            logger.error(f"Error creating update message: {str(e)}")
            return None

    async def monitor_events(self):
        """Main monitoring function"""
        while True:
            logger.info("Checking for live matches...")
            matches = await self.fetch_live_matches()
            
            if matches:
                await self.process_match_updates(matches)
                # Temporarily disable GPT suggestions
                # await self.get_api_suggestions(matches)
            
            # Wait before next check
            await asyncio.sleep(30)  # Check every 30 seconds

async def run_monitoring():
    """Run the monitoring process"""
    bot = SportsMonitorBot()
    await bot.monitor_events()

if __name__ == "__main__":
    logger.info("Starting Sports Monitor Bot...")
    import asyncio
    asyncio.run(run_monitoring())
