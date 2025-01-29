"""Local monitor that uses the remote Digital Ocean API"""

import os
import requests
import time
from dotenv import load_dotenv
from loguru import logger
from config.remote_config import (
    MATCHES_ENDPOINT,
    LIVE_MATCHES_ENDPOINT,
    HEALTH_CHECK_ENDPOINT
)

# Load environment variables
load_dotenv()

# Configure logging
logger.add("local_monitor.log", rotation="1 day")

def check_remote_health():
    """Check if the remote API is healthy"""
    try:
        response = requests.get(HEALTH_CHECK_ENDPOINT)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error checking remote health: {e}")
        return False

def get_live_matches():
    """Get live matches from the remote API"""
    try:
        response = requests.get(LIVE_MATCHES_ENDPOINT)
        if response.status_code == 200:
            return response.json()
        logger.error(f"Error getting live matches: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error getting live matches: {e}")
        return None

def main():
    """Main function to monitor matches using the remote API"""
    logger.info("Starting local monitor using remote API...")
    
    # First check if remote API is healthy
    if not check_remote_health():
        logger.error("Remote API is not healthy. Please check the Digital Ocean deployment.")
        return

    logger.info("Remote API is healthy. Starting monitoring...")
    
    try:
        while True:
            matches = get_live_matches()
            if matches:
                print("\n" + "="*50)
                print("Live Matches:")
                print("="*50)
                for match in matches:
                    print(f"\n{match['league_name']}")
                    print(f"{match['sport_emoji']} {match['team1']} {match['score']} {match['team2']}")
                    print(f"⏰ {match['time']} ({match['period']})")
            
            # Wait for 30 seconds before next update
            time.sleep(30)
            
    except KeyboardInterrupt:
        logger.info("Stopping local monitor...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
