import os
import requests
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables from .env.do file
load_dotenv('.env.do')

class DigitalOceanMonitor:
    def __init__(self):
        self.api_token = os.getenv('DO_API_TOKEN')
        self.app_id = os.getenv('DO_APP_ID')
        self.base_url = 'https://api.digitalocean.com/v2'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def get_app_info(self):
        """Get information about the app"""
        url = f"{self.base_url}/apps"
        response = requests.get(url, headers=self.headers)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            apps = response.json().get('apps', [])
            for app in apps:
                if app.get('spec', {}).get('name') == self.app_id:
                    return app
        print(f"API Response: {response.text}")
        return None

    def get_deployment_status(self):
        """Get the latest deployment status"""
        app = self.get_app_info()
        if app:
            app_id = app.get('id')
            url = f"{self.base_url}/apps/{app_id}/deployments"
            response = requests.get(url, headers=self.headers)
            print(f"Deployments response status: {response.status_code}")
            if response.status_code == 200:
                deployments = response.json().get('deployments', [])
                if deployments:
                    latest = deployments[0]
                    return {
                        'id': latest.get('id'),
                        'phase': latest.get('phase'),
                        'created_at': latest.get('created_at'),
                        'updated_at': latest.get('updated_at'),
                        'cause': latest.get('cause'),
                        'progress': latest.get('progress', {})
                    }
            print(f"Deployments Response: {response.text}")
        return None

    def monitor_deployment(self):
        """Monitor the deployment status continuously"""
        print("\n🔍 Starting Digital Ocean App Platform Monitoring...")
        print(f"Monitoring app: {self.app_id}")
        
        while True:
            print("\nChecking deployment status...")
            status = self.get_deployment_status()
            
            if status:
                print(f"\n📊 Deployment Status at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
                print(f"Phase: {status['phase']}")
                print(f"Cause: {status['cause']}")
                print(f"Updated: {status['updated_at']}")
                
                progress = status['progress']
                if progress:
                    print("\nProgress:")
                    print(f"Success Rate: {progress.get('success_steps', 0)}/{progress.get('total_steps', 0)}")
                    print(f"Error Count: {progress.get('error_steps', 0)}")
                    
                if status['phase'] == 'ERROR':
                    print("\n❌ Deployment failed!")
                    break
                elif status['phase'] == 'ACTIVE':
                    print("\n✅ Deployment successful!")
                    break
            else:
                print("Could not fetch deployment status")
            
            print("\nWaiting 10 seconds before next check...")
            time.sleep(10)

if __name__ == "__main__":
    monitor = DigitalOceanMonitor()
    monitor.monitor_deployment()
