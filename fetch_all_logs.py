import os
import subprocess
import requests
from datetime import datetime

APP_ID = "5137f955-d71d-41a0-9774-fb35149ea21b"
DO_API_TOKEN = os.getenv("DO_API_TOKEN")

def get_runtime_logs():
    """Get current runtime logs"""
    print("\n=== Runtime Logs ===")
    result = subprocess.run([
        ".\\doctl\\doctl.exe", 
        "apps", "logs", 
        APP_ID,
        "--type=RUN"
    ], capture_output=True, text=True)
    print(result.stdout)
    
def get_crash_logs():
    """Get logs from the last crash"""
    print("\n=== Crash Logs ===")
    result = subprocess.run([
        ".\\doctl\\doctl.exe", 
        "apps", "logs", 
        APP_ID,
        "--type=run_restarted"
    ], capture_output=True, text=True)
    print(result.stdout)

def get_build_logs(deployment_id, component="autosportsgpt"):
    """Get build logs for a specific deployment"""
    print("\n=== Build Logs ===")
    headers = {
        "Authorization": f"Bearer {DO_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.digitalocean.com/v2/apps/{APP_ID}/deployments/{deployment_id}/components/{component}/logs?type=BUILD"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if "historic_urls" in data and data["historic_urls"]:
            build_log_url = data["historic_urls"][0]
            build_logs = requests.get(build_log_url).text
            print(build_logs)
        else:
            print("No build logs found")
    else:
        print(f"Error getting build logs: {response.text}")

def get_deployments():
    """Get list of recent deployments"""
    headers = {
        "Authorization": f"Bearer {DO_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.digitalocean.com/v2/apps/{APP_ID}/deployments"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        deployments = response.json().get("deployments", [])
        print("\n=== Recent Deployments ===")
        for d in deployments[:5]:  # Show last 5 deployments
            phase = d.get("phase", "unknown")
            cause = d.get("cause", "unknown")
            created_at = d.get("created_at", "unknown")
            deployment_id = d.get("id", "unknown")
            print(f"ID: {deployment_id}")
            print(f"Phase: {phase}")
            print(f"Cause: {cause}")
            print(f"Created: {created_at}")
            print("-" * 50)
        return deployments
    else:
        print(f"Error getting deployments: {response.text}")
        return []

def main():
    print("Fetching Digital Ocean App Logs...")
    print(f"Time: {datetime.now()}")
    print(f"App ID: {APP_ID}")
    
    # Get runtime and crash logs
    get_runtime_logs()
    get_crash_logs()
    
    # Get recent deployments and their build logs
    deployments = get_deployments()
    if deployments:
        latest_deployment = deployments[0]
        get_build_logs(latest_deployment["id"])

if __name__ == "__main__":
    main()
