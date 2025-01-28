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
            home_team=match_data['teams']['home']['name'],
            away_team=match_data['teams']['away']['name'],
            score=f"{match_data['goals']['home']} - {match_data['goals']['away']}",
            time=match_data['fixture']['status']['elapsed']
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
                'match_id': match_data['fixture']['id'],
                'timestamp': match_data['fixture']['status']['elapsed']
            }
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return None

    async def suggest_api_queries(self, current_matches: List[Dict[str, Any]]) -> List[str]:
        """Use GPT to suggest relevant API queries based on current matches"""
        matches_summary = "\n".join([
            f"{m['teams']['home']['name']} vs {m['teams']['away']['name']} ({m['league']['name']})"
            for m in current_matches
        ])

        prompt = self.prompts['api_suggestions'].format(matches=matches_summary)

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
