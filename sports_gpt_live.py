import os
import asyncio
from openai import OpenAI
from loguru import logger
import yaml
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SportsGPTLive:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.api_key = os.getenv('SPORTS_API_KEY')
        self.api_host = os.getenv('SPORTS_API_HOST')
        self.base_url = f"https://{self.api_host}"
        
        # Load sports-specific prompts
        self.load_prompts()
        
        # Initialize sport IDs
        self.sports = {
            'soccer': 1,
            'tennis': 13,
            'basketball': 18,
            'volleyball': 91,
            'hockey': 17
        }

    def load_prompts(self):
        """Load predefined prompts for different sports scenarios"""
        with open('prompts.yaml', 'r') as file:
            self.prompts = yaml.safe_load(file)

    async def get_live_matches(self, sport_id: int) -> List[Dict[str, Any]]:
        """Fetch live matches for a specific sport"""
        url = f"{self.base_url}/v3/events/inplay"
        params = {
            'token': self.api_key,
            'sport_id': sport_id
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json().get('results', [])
            return []
        except Exception as e:
            logger.error(f"Error fetching live matches: {str(e)}")
            return []

    async def analyze_live_match(self, match_data: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """Analyze a live match using GPT"""
        # Create a sport-specific analysis prompt
        if sport == 'tennis':
            prompt = f"""
            Analyze this live tennis match:
            {match_data.get('home', {}).get('name')} vs {match_data.get('away', {}).get('name')}
            Score: {match_data.get('ss', 'No score')}
            Tournament: {match_data.get('league', {}).get('name')}
            
            Detailed scores: {match_data.get('scores', {})}
            Statistics: {match_data.get('stats', {})}
            
            Provide insights about:
            1. Current match state and momentum
            2. Key points or turning points
            3. Player performance analysis
            4. Potential predictions for the next set
            """
        else:  # Default format for other sports
            prompt = f"""
            Analyze this live {sport} match:
            {match_data.get('home', {}).get('name')} vs {match_data.get('away', {}).get('name')}
            Score: {match_data.get('ss', 'No score')}
            League: {match_data.get('league', {}).get('name')}
            
            Statistics: {match_data.get('stats', {})}
            
            Provide insights about:
            1. Current match state
            2. Key events or patterns
            3. Team performance analysis
            4. Potential predictions
            """

        try:
            response = await self.get_gpt_analysis(prompt)
            return {
                'match_id': match_data.get('id'),
                'sport': sport,
                'analysis': response,
                'timestamp': match_data.get('time')
            }
        except Exception as e:
            logger.error(f"Error in match analysis: {str(e)}")
            return None

    async def get_gpt_analysis(self, prompt: str) -> str:
        """Get analysis from GPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['system_prompt']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return "Analysis unavailable"

    async def monitor_live_sports(self):
        """Main function to monitor and analyze live sports"""
        while True:
            for sport_name, sport_id in self.sports.items():
                logger.info(f"Checking {sport_name} matches...")
                
                # Get live matches
                matches = await self.get_live_matches(sport_id)
                if not matches:
                    logger.info(f"No live {sport_name} matches found")
                    continue

                logger.info(f"Found {len(matches)} live {sport_name} matches")
                
                # Analyze each match
                for match in matches[:3]:  # Limit to 3 matches per sport to avoid API overload
                    analysis = await self.analyze_live_match(match, sport_name)
                    if analysis:
                        print(f"\n{'='*50}")
                        print(f"Sport: {sport_name.upper()}")
                        print(f"Match: {match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}")
                        print(f"Score: {match.get('ss', 'No score')}")
                        print(f"\nAnalysis:")
                        print(analysis['analysis'])
                        print(f"{'='*50}\n")

            # Wait before next update
            await asyncio.sleep(300)  # 5 minutes delay

async def main():
    gpt_live = SportsGPTLive()
    await gpt_live.monitor_live_sports()

if __name__ == "__main__":
    logger.info("Starting Sports GPT Live Monitor...")
    asyncio.run(main())
