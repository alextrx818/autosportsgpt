import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
import telegram
from sports_gpt_handler import SportsGPTHandler

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
        
        self.headers = {
            'x-rapidapi-host': self.api_host,
            'x-rapidapi-key': self.api_key
        }
        
        self.last_events = {}  # Store last known state of events
        self.gpt_handler = SportsGPTHandler()  # Initialize GPT handler

    def fetch_live_matches(self):
        """Fetch live matches from the API"""
        url = f"https://{self.api_host}/fixtures"
        params = {'live': 'all'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                logger.error(f"API request failed with status {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching live matches: {str(e)}")
            return []

    async def process_match_updates(self, matches):
        """Process updates for each live match with GPT analysis"""
        for match in matches:
            match_id = match['fixture']['id']
            current_state = {
                'status': match['fixture']['status']['short'],
                'home_score': match['goals']['home'],
                'away_score': match['goals']['away'],
                'elapsed': match['fixture']['status']['elapsed']
            }

            # Check if this is a new match or if there's been an update
            if match_id not in self.last_events or self.last_events[match_id] != current_state:
                # Get GPT analysis
                analysis = await self.gpt_handler.analyze_match_data(match)
                if analysis:
                    match['gpt_analysis'] = analysis['analysis']
                
                await self.handle_match_update(match, current_state)
                self.last_events[match_id] = current_state

    async def handle_match_update(self, match, current_state):
        """Handle updates for a specific match"""
        message = self.create_update_message(match, current_state)
        logger.info(message)
        
        if self.telegram_bot:
            try:
                self.telegram_bot.send_message(chat_id=self.chat_id, text=message)
            except Exception as e:
                logger.error(f"Error sending Telegram message: {str(e)}")

    def create_update_message(self, match, current_state):
        """Create a formatted message for match updates"""
        base_message = (
            f" {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n"
            f" Score: {current_state['home_score']} - {current_state['away_score']}\n"
            f" Time: {current_state['elapsed']}'\n"
            f" League: {match['league']['name']}\n"
            f" Venue: {match['fixture']['venue']['name']}"
        )
        
        # Add GPT analysis if available
        if 'gpt_analysis' in match:
            base_message += f"\n\n Analysis:\n{match['gpt_analysis']}"
        
        return base_message

    async def get_api_suggestions(self, matches):
        """Get GPT suggestions for API queries"""
        suggestions = await self.gpt_handler.suggest_api_queries(matches)
        if suggestions:
            logger.info("GPT API Suggestions:")
            for suggestion in suggestions:
                logger.info(f"- {suggestion}")
        return suggestions

    async def monitor_events(self):
        """Main monitoring function with GPT integration"""
        logger.info("Checking for live matches...")
        matches = self.fetch_live_matches()
        
        if matches:
            # Get API suggestions from GPT
            await self.get_api_suggestions(matches)
            
            # Process match updates with GPT analysis
            await self.process_match_updates(matches)

async def run_monitoring():
    """Run the monitoring process"""
    bot = SportsMonitorBot()
    while True:
        await bot.monitor_events()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    logger.info("Starting Sports Monitor Bot...")
    import asyncio
    asyncio.run(run_monitoring())
