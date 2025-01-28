import os
from autogpt.agents import Agent
from autogpt.config import Config
from autogpt.memory import Memory
from autogpt.prompts.generator import PromptGenerator
from autogpt.workspace import Workspace
from dotenv import load_dotenv
from typing import Dict, List, Any
import json

# Load environment variables
load_dotenv()

class SportsAgent(Agent):
    def __init__(self):
        # Initialize AutoGPT configuration
        config = Config()
        config.continuous_mode = True
        config.speak_mode = False
        
        # Set up the agent's memory
        memory = Memory()
        
        # Create workspace for the agent
        workspace = Workspace()
        
        # Initialize prompt generator
        prompt_generator = PromptGenerator()
        
        # Add sports-specific commands
        self.add_sports_commands(prompt_generator)
        
        # Initialize the parent Agent class
        super().__init__(
            ai_name="SportsBettingAnalyst",
            memory=memory,
            full_message_history=[],
            next_action_count=0,
            prompt_generator=prompt_generator,
            command_registry=prompt_generator,
            config=config,
            workspace=workspace,
            triggering_prompt="Analyze sports events and provide insights"
        )

    def add_sports_commands(self, prompt_generator: PromptGenerator):
        """Add sports-specific commands to the agent"""
        prompt_generator.add_command(
            "get_live_matches",
            "Get current live matches for a specific sport",
            {"sport": "<sport_name>"},
            self.get_live_matches
        )
        
        prompt_generator.add_command(
            "analyze_match",
            "Analyze a specific match and provide insights",
            {"match_data": "<match_json>"},
            self.analyze_match
        )
        
        prompt_generator.add_command(
            "track_statistics",
            "Track specific statistics for a match",
            {
                "match_id": "<match_id>",
                "stats": "<stats_to_track>"
            },
            self.track_statistics
        )
        
        prompt_generator.add_command(
            "get_historical_data",
            "Get historical data for teams/players",
            {
                "team1": "<team1_name>",
                "team2": "<team2_name>"
            },
            self.get_historical_data
        )

    async def get_live_matches(self, sport: str) -> List[Dict[str, Any]]:
        """Get live matches for a specific sport"""
        api_key = os.getenv('SPORTS_API_KEY')
        api_host = os.getenv('SPORTS_API_HOST')
        
        sport_ids = {
            'soccer': 1,
            'tennis': 13,
            'basketball': 18,
            'volleyball': 91,
            'hockey': 17
        }
        
        if sport.lower() not in sport_ids:
            return {"error": f"Sport {sport} not supported"}
            
        url = f"https://{api_host}/v3/events/inplay"
        params = {
            'token': api_key,
            'sport_id': sport_ids[sport.lower()]
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                matches = response.json().get('results', [])
                # Store matches in agent's memory for future reference
                self.memory.add(f"live_{sport}_matches", matches)
                return matches
            return {"error": f"API request failed with status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def analyze_match(self, match_data: str) -> Dict[str, Any]:
        """Analyze a match and provide insights"""
        try:
            match = json.loads(match_data)
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze this match:
            {match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}
            Score: {match.get('ss', 'No score')}
            League: {match.get('league', {}).get('name')}
            Statistics: {match.get('stats', {})}
            
            Provide:
            1. Current match state
            2. Key events or patterns
            3. Performance analysis
            4. Predictions
            """
            
            # Use the agent's thinking process to analyze
            thoughts = await self.think(analysis_prompt)
            
            # Store analysis in memory
            self.memory.add(f"match_analysis_{match.get('id')}", thoughts)
            
            return {
                'match_id': match.get('id'),
                'analysis': thoughts,
                'timestamp': match.get('time')
            }
        except Exception as e:
            return {"error": str(e)}

    async def track_statistics(self, match_id: str, stats: str) -> Dict[str, Any]:
        """Track specific statistics for a match"""
        try:
            stats_to_track = json.loads(stats)
            match_data = self.memory.get(f"match_{match_id}")
            
            if not match_data:
                return {"error": "Match not found in memory"}
            
            tracked_stats = {}
            for stat in stats_to_track:
                if stat in match_data.get('stats', {}):
                    tracked_stats[stat] = match_data['stats'][stat]
            
            # Store tracked stats in memory
            self.memory.add(f"tracked_stats_{match_id}", tracked_stats)
            
            return tracked_stats
        except Exception as e:
            return {"error": str(e)}

    async def get_historical_data(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get historical data for teams/players"""
        # This would typically connect to a historical database
        # For now, return placeholder data
        return {
            "head_to_head": "Historical data not implemented yet",
            "team1_form": "Historical data not implemented yet",
            "team2_form": "Historical data not implemented yet"
        }

async def main():
    # Create the sports agent
    agent = SportsAgent()
    
    # Start the continuous monitoring loop
    while True:
        # Get live matches for each sport
        sports = ['soccer', 'tennis', 'basketball', 'volleyball', 'hockey']
        
        for sport in sports:
            matches = await agent.get_live_matches(sport)
            
            if isinstance(matches, list):
                print(f"\nAnalyzing {sport} matches...")
                for match in matches[:3]:  # Analyze top 3 matches per sport
                    analysis = await agent.analyze_match(json.dumps(match))
                    print(f"\nMatch Analysis for {match.get('home', {}).get('name')} vs {match.get('away', {}).get('name')}:")
                    print(analysis.get('analysis', 'No analysis available'))
        
        # Wait before next update
        await asyncio.sleep(300)  # 5 minutes delay

if __name__ == "__main__":
    import asyncio
    print("Starting Sports AutoGPT Agent...")
    asyncio.run(main())
