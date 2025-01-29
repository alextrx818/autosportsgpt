from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sports_monitor_bot import SportsMonitorBot
import os
from dotenv import load_dotenv
import asyncio
from typing import Dict, List
from datetime import datetime

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
bot = SportsMonitorBot(
    api_key=os.getenv('SPORTS_API_KEY'),
    api_host=os.getenv('SPORTS_API_HOST')
)

# Store for latest matches
latest_matches: Dict[int, List[dict]] = {}
last_update: datetime = None

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

if __name__ == "__main__":
    port = int(os.getenv('PORT', '8080'))  # Use PORT from environment or default to 8080
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
