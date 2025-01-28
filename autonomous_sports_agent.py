import os
import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

class AutonomousSportsAgent:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.sports_api_key = os.getenv('SPORTS_API_KEY')
        self.sports_api_host = os.getenv('SPORTS_API_HOST')
        self.memory = {}  # Simple memory storage
        self.goals = [
            "Monitor live sports events",
            "Analyze match statistics",
            "Identify interesting patterns",
            "Make predictions",
            "Track performance changes"
        ]
        self.sports = {
            'soccer': 1,
            'tennis': 13,
            'basketball': 18,
            'volleyball': 91,
            'hockey': 17
        }

    async def think(self, context: str) -> Dict[str, Any]:
        """Think about the current situation and decide next actions"""
        prompt = f"""
        You are an autonomous sports analysis agent. Your goals are:
        {self.goals}

        Current context:
        {context}

        Based on this information:
        1. What are the most important aspects to analyze?
        2. What patterns or trends should we look for?
        3. What predictions can we make?
        4. What additional data would be helpful?

        Format your response as JSON with these keys:
        - analysis: Your main analysis
        - patterns: List of identified patterns
        - predictions: List of predictions
        - next_actions: List of suggested next actions
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an autonomous sports analysis AI. Think carefully and provide detailed insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response as JSON
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in thinking process: {str(e)}")
            return {
                "analysis": "Error in analysis",
                "patterns": [],
                "predictions": [],
                "next_actions": ["Retry analysis"]
            }

    async def get_live_matches(self, sport: str) -> List[Dict[str, Any]]:
        """Get live matches for a specific sport"""
        try:
            url = f"https://{self.sports_api_host}/v3/events/inplay"
            params = {
                'token': self.sports_api_key,
                'sport_id': self.sports.get(sport.lower())
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                matches = response.json().get('results', [])
                self.memory[f"live_{sport}_matches"] = matches
                return matches
            return []
        except Exception as e:
            logger.error(f"Error fetching {sport} matches: {str(e)}")
            return []

    async def analyze_match(self, match: Dict[str, Any], sport: str) -> Dict[str, Any]:
        """Analyze a specific match"""
        match_context = f"""
        Sport: {sport}
        Match: {match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}
        Score: {match.get('ss', 'No score')}
        League: {match.get('league', {}).get('name')}
        Statistics: {json.dumps(match.get('stats', {}))}
        """

        analysis = await self.think(match_context)
        
        # Store analysis in memory
        match_id = match.get('id')
        if match_id:
            self.memory[f"analysis_{match_id}"] = analysis

        return analysis

    async def monitor_sports(self):
        """Main monitoring loop"""
        while True:
            print("\n" + "="*50)
            print(f"Starting new monitoring cycle at {datetime.now()}")
            print("="*50)

            for sport in self.sports.keys():
                print(f"\nChecking {sport.upper()} matches...")
                matches = await self.get_live_matches(sport)
                
                if not matches:
                    print(f"No live {sport} matches found")
                    continue

                print(f"Found {len(matches)} live {sport} matches")
                
                # Analyze top 3 matches for each sport
                for match in matches[:3]:
                    print(f"\nAnalyzing: {match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}")
                    analysis = await self.analyze_match(match, sport)
                    
                    print("\nAnalysis:")
                    print(f"Main insights: {analysis.get('analysis')}")
                    print("\nPatterns identified:")
                    for pattern in analysis.get('patterns', []):
                        print(f"- {pattern}")
                    print("\nPredictions:")
                    for prediction in analysis.get('predictions', []):
                        print(f"- {prediction}")
                    print("\nNext actions:")
                    for action in analysis.get('next_actions', []):
                        print(f"- {action}")

            # Wait before next update
            print("\nWaiting 5 minutes before next update...")
            await asyncio.sleep(300)

async def main():
    agent = AutonomousSportsAgent()
    print("Starting Autonomous Sports Agent...")
    await agent.monitor_sports()

if __name__ == "__main__":
    asyncio.run(main())
