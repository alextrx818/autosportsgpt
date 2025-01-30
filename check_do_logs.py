"""Quick script to check Digital Ocean console messages"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the base URL from remote_config.py
REMOTE_API_URL = "https://plankton-app-qyijl.ondigitalocean.app"

def check_logs():
    """Check latest console messages from Digital Ocean"""
    try:
        response = requests.get(f"{REMOTE_API_URL}/logs/build")
        if response.status_code == 200:
            data = response.json()
            print("\nLatest Deployment Status:", data.get('status', 'Unknown'))
            print("Created at:", data.get('created_at', 'Unknown'))
            print("\nLatest Console Messages:")
            print("-" * 50)
            for log in data.get('logs', []):
                print(f"[{log['timestamp']}] {log['message']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to Digital Ocean app: {str(e)}")

if __name__ == "__main__":
    check_logs()
