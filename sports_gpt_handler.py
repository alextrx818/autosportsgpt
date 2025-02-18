import os
from openai import OpenAI
from loguru import logger
import yaml
from typing import Dict, List, Any

class SportsGPTHandler:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.api_key = os.getenv('SPORTS_API_KEY')
        self.api_host = os.getenv('SPORTS_API_HOST')
        
        # Load sports-specific prompts
        self.load_prompts()

    def load_prompts(self):
        """Load predefined prompts for different sports scenarios"""
        with open('prompts.yaml', 'r') as file:
            self.prompts = yaml.safe_load(file)

    async def analyze_match_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use GPT to analyze match data and provide insights"""
        prompt = self.prompts['match_analysis'].format(
            home_team=match_data.get('home', {}).get('name', 'Unknown'),
            away_team=match_data.get('away', {}).get('name', 'Unknown'),
            score=match_data.get('ss', 'No score'),
            time=match_data.get('time', 'No time')
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['system_prompt']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            analysis = response.choices[0].message.content
            return {
                'analysis': analysis,
                'match_id': match_data.get('id'),
                'timestamp': match_data.get('time')
            }
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return None

    async def suggest_api_queries(self, current_matches: List[Dict[str, Any]]) -> List[str]:
        """Generate API query suggestions based on current matches"""
        if not current_matches:
            return []

        # Format match information for GPT
        match_info = "\n".join([
            f"{m.get('home', {}).get('name', 'Unknown')} vs {m.get('away', {}).get('name', 'Unknown')} ({m.get('league', {}).get('name', 'Unknown League')})"
            for m in current_matches[:5]  # Limit to 5 matches to avoid token limits
        ])

        prompt = self.prompts['api_suggestions'].format(matches=match_info)

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['system_prompt']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            suggestions = response.choices[0].message.content.split('\n')
            return [s.strip() for s in suggestions if s.strip()]
        except Exception as e:
            logger.error(f"Error getting API suggestions: {str(e)}")
            return []

    async def interpret_api_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Use GPT to interpret API responses and extract relevant information"""
        prompt = self.prompts['api_interpretation'].format(
            response=str(api_response)
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['system_prompt']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            interpretation = response.choices[0].message.content
            return {
                'interpretation': interpretation,
                'timestamp': api_response.get('timestamp', None),
                'source': api_response.get('source', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error interpreting API response: {str(e)}")
            return None
