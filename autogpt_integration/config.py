from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AutoGPTConfig:
    def __init__(self):
        self.api_key = os.getenv('AUTOGPT_API_KEY')
        self.project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Data Analysis Configuration
        self.analysis_config = {
            'live_match_interval': 30,  # seconds
            'alert_threshold': 0.75,    # confidence threshold for alerts
            'api_monitor_interval': 60,  # seconds
        }
        
        # Interface Development Configuration
        self.interface_config = {
            'ui_frameworks': ['Flask', 'Bootstrap'],
            'code_review_enabled': True,
            'auto_optimize': True,
        }
        
        # GitHub Integration
        self.github_config = {
            'repo': 'alextrx818/autosportsgpt',
            'branch': 'main',
            'auto_commit': False,  # Require manual approval for commits
        }

    def get_analysis_tasks(self) -> List[str]:
        return [
            'monitor_live_matches',
            'generate_alerts',
            'track_api_performance',
            'analyze_patterns',
        ]

    def get_development_tasks(self) -> List[str]:
        return [
            'review_code',
            'suggest_improvements',
            'generate_components',
            'optimize_layouts',
        ]

    def get_integration_points(self) -> Dict[str, List[str]]:
        return {
            'sports_web.py': [
                'ui_components',
                'api_endpoints',
                'data_display',
            ],
            'sports_monitor_bot.py': [
                'alerts',
                'match_analysis',
                'performance',
            ],
        }
