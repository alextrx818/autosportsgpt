from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sports_monitor_bot import SportsMonitorBot
import os
from dotenv import load_dotenv
import asyncio
from typing import Dict, List
from datetime import datetime
import digitalocean

# Load environment variables if .env exists
try:
    load_dotenv()
except:
    pass  # It's ok if .env doesn't exist, we'll use environment variables

app = FastAPI(title="Sports Monitor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global bot instance
bot = SportsMonitorBot()

# Store for latest matches
latest_matches: Dict[int, List[dict]] = {}
last_update: datetime = None

# Initialize Digital Ocean manager
do_token = os.getenv('DO_API_TOKEN')
if not do_token:
    print("Warning: DO_API_TOKEN not found in environment variables")
do_manager = digitalocean.Manager(token=do_token) if do_token else None

async def update_matches():
    """Background task to update matches"""
    global latest_matches, last_update
    while True:
        try:
            matches = await bot.fetch_live_matches()
            # Group matches by sport_id
            matches_by_sport = {}
            for match in matches:
                sport_id = match.get('sport_id')
                if sport_id not in matches_by_sport:
                    matches_by_sport[sport_id] = []
                matches_by_sport[sport_id].append(match)
            latest_matches = matches_by_sport
            last_update = datetime.now()
        except Exception as e:
            print(f"Error updating matches: {str(e)}")
        await asyncio.sleep(60)  # Update every minute

@app.on_event("startup")
async def startup_event():
    """Start the background task on server startup"""
    asyncio.create_task(update_matches())

@app.get("/")
async def root():
    return {"status": "running", "last_update": last_update}

@app.get("/health")
async def health_check():
    """Health check endpoint for Digital Ocean"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/matches")
async def get_matches():
    """Get all live matches"""
    return {
        "matches": latest_matches,
        "last_update": last_update
    }

@app.get("/matches/{sport_id}")
async def get_matches_by_sport(sport_id: int):
    """Get live matches for a specific sport"""
    return {
        "matches": latest_matches.get(sport_id, []),
        "last_update": last_update
    }

@app.get("/logs/build")
async def get_build_logs():
    """Get the latest build logs from Digital Ocean"""
    do_token = os.getenv('DO_API_TOKEN')
    if not do_token:
        raise HTTPException(status_code=500, detail="Digital Ocean API token not configured")
    
    try:
        manager = digitalocean.Manager(token=do_token)
        # Get the app
        apps = manager.get_all_apps()
        app = next((app for app in apps if app.spec['name'] == 'plankton-app'), None)
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Get latest deployment
        deployments = app.get_deployments()
        if not deployments:
            return {"message": "No deployments found"}
        
        latest_deployment = deployments[0]
        build_logs = latest_deployment.get_logs('BUILD')
        
        # Format logs
        formatted_logs = []
        for log in build_logs:
            formatted_logs.append({
                "timestamp": datetime.fromtimestamp(log.get('timestamp', 0)).isoformat(),
                "message": log.get('message', ''),
                "type": log.get('type', '')
            })
        
        return {
            "deployment_id": latest_deployment.id,
            "status": latest_deployment.phase,
            "created_at": latest_deployment.created_at,
            "logs": formatted_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/build/{deployment_id}")
async def get_deployment_logs(deployment_id: str):
    """Get build logs for a specific deployment"""
    do_token = os.getenv('DO_API_TOKEN')
    if not do_token:
        raise HTTPException(status_code=500, detail="Digital Ocean API token not configured")
    
    try:
        manager = digitalocean.Manager(token=do_token)
        # Get the app
        apps = manager.get_all_apps()
        app = next((app for app in apps if app.spec['name'] == 'plankton-app'), None)
        if not app:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Get specific deployment
        deployment = app.get_deployment(deployment_id)
        build_logs = deployment.get_logs('BUILD')
        
        # Format logs
        formatted_logs = []
        for log in build_logs:
            formatted_logs.append({
                "timestamp": datetime.fromtimestamp(log.get('timestamp', 0)).isoformat(),
                "message": log.get('message', ''),
                "type": log.get('type', '')
            })
        
        return {
            "deployment_id": deployment.id,
            "status": deployment.phase,
            "created_at": deployment.created_at,
            "logs": formatted_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv('PORT', '8080'))  # Use PORT from environment or default to 8080
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
