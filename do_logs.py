"""
Digital Ocean Build Logs Fetcher

This script connects to Digital Ocean API and fetches build logs for the specified app.
"""

import os
import sys
import time
from datetime import datetime
import digitalocean
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DOLogsManager:
    def __init__(self):
        self.token = os.getenv('DO_API_TOKEN')
        if not self.token:
            raise ValueError("DO_API_TOKEN environment variable not found")
        self.manager = digitalocean.Manager(token=self.token)
        self.app_id = os.getenv('DO_APP_ID', 'plankton-app-qyijl')  # Default to our app ID

    def get_app(self):
        """Get the Digital Ocean app instance"""
        apps = self.manager.get_all_apps()
        for app in apps:
            if app.id == self.app_id or app.spec['name'] == self.app_id:
                return app
        raise ValueError(f"App with ID/name {self.app_id} not found")

    def get_deployments(self, limit=5):
        """Get recent deployments for the app"""
        app = self.get_app()
        deployments = app.get_deployments()
        return deployments[:limit]

    def get_build_logs(self, deployment_id=None):
        """Get build logs for a specific deployment or the latest one"""
        app = self.get_app()
        if deployment_id is None:
            deployments = self.get_deployments(limit=1)
            if not deployments:
                print("No deployments found")
                return
            deployment = deployments[0]
        else:
            deployment = app.get_deployment(deployment_id)

        # Get build logs
        build_logs = deployment.get_logs('BUILD')
        return build_logs

    def stream_logs(self, deployment_id=None):
        """Stream logs in real-time for the specified deployment"""
        try:
            while True:
                logs = self.get_build_logs(deployment_id)
                if logs:
                    for log in logs:
                        timestamp = datetime.fromtimestamp(log.get('timestamp', 0))
                        print(f"[{timestamp}] {log.get('message', '')}")
                time.sleep(5)  # Poll every 5 seconds
        except KeyboardInterrupt:
            print("\nStopping log stream...")

def main():
    logs_manager = DOLogsManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            # List recent deployments
            deployments = logs_manager.get_deployments()
            print("\nRecent Deployments:")
            for dep in deployments:
                print(f"ID: {dep.id}")
                print(f"Created: {dep.created_at}")
                print(f"Status: {dep.phase}")
                print("-" * 50)
        elif sys.argv[1] == '--deployment':
            # Get logs for specific deployment
            if len(sys.argv) < 3:
                print("Please provide deployment ID")
                return
            logs_manager.stream_logs(sys.argv[2])
    else:
        # Stream latest deployment logs
        print("Streaming latest deployment logs (Ctrl+C to stop)...")
        logs_manager.stream_logs()

if __name__ == "__main__":
    main()
