from flask import Flask, render_template_string
import os
from datetime import datetime
import re
from openai import OpenAI
from fastapi import BackgroundTasks
import logging
from autogpt.agent import Agent
from autogpt.config import Config
from autogpt.workspace import Workspace
from autogpt.commands.command import CommandRegistry

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI()

# Initialize logger
logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Sports Monitor</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="30">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }
        .match {
            margin-bottom: 20px;
            padding: 10px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 4px;
        }
        .sport-header {
            color: #2196F3;
            font-size: 1.2em;
            margin: 20px 0 10px 0;
            padding: 5px 0;
            border-bottom: 2px solid #2196F3;
        }
        pre {
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            margin: 0;
            padding: 10px;
        }
        .last-update {
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            padding: 10px;
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2196F3;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>📱 Live Sports Monitor</h1>
    <div id="matches">
        <pre>{{ matches | safe }}</pre>
    </div>
    <div class="last-update">
        Last Update: {{ last_update }}
        <br>
        Auto-refreshing every 30 seconds...
    </div>
</body>
</html>
"""

def is_esport(league_name):
    """Check if the league is an e-sport league"""
    esport_keywords = ['esoccer', 'esports', 'e-', 'cyber', 'ebasketball', 'etennis', 'evolleyball', 'ehockey']
    league_name = league_name.lower()
    return any(keyword in league_name for keyword in esport_keywords)

def read_log_file():
    """Read the latest matches from the log file"""
    try:
        # Get the absolute path to the log file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, 'sports_monitor.log')
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Get the latest complete update
        matches = []
        current_sport = None
        current_sport_matches = []
        
        for line in reversed(lines):
            # Split the log line to get the actual message
            parts = line.split('|')
            if len(parts) >= 2:
                message = parts[-1].strip()
                
                # Check for start/end markers
                if "Starting Sports Monitor Bot" in message:
                    if current_sport and current_sport_matches:
                        matches.extend([current_sport] + current_sport_matches)
                    break
                
                # Check for sport header (e.g. "📱 Live Soccer Matches (5 total)")
                if "Live" in message and "Matches" in message:
                    if current_sport and current_sport_matches:
                        matches.extend([current_sport] + current_sport_matches)
                    current_sport = message
                    current_sport_matches = []
                    continue
                
                # Skip e-sports matches
                if any(keyword in message.lower() for keyword in ['esoccer', 'esports', 'e-', 'cyber']):
                    continue
                    
                # Only add lines that contain match data (must have both emoji and score)
                if any(emoji in message for emoji in ['⚽', '🏀', '🎾', '🏐', '🏒', '🤾', '⚾', '🏈', '🎱', '🎯', '🏓', '🏸', '🏉']):
                    if ('vs' in message or '-' in message) and '⏰' in message:
                        current_sport_matches.append(message)
        
        # Add the last sport section if it exists
        if current_sport and current_sport_matches:
            matches.extend([current_sport] + current_sport_matches)
        
        if not matches:
            return "No live matches available at the moment. Please wait for updates..."
            
        return '\n'.join(matches)
    except Exception as e:
        return f"Error reading match data: {str(e)}\nPlease make sure the sports monitor bot is running."

async def analyze_sports_data(data):
    """Analyze sports data using OpenAI API - runs on Digital Ocean"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a sports analysis assistant that helps monitor matches and suggest UI improvements."},
                {"role": "user", "content": f"Analyze this sports data and provide insights: {data}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing sports data: {e}")
        return None

# AutoGPT Integration
def init_autogpt():
    """Initialize AutoGPT agent - runs on Digital Ocean"""
    config = Config()
    config.continuous_mode = True
    config.speak_mode = False
    
    # Use Digital Ocean's mounted filesystem
    workspace = Workspace(
        workspace_root="/workspace/autogpt-data",
        restrict_to_workspace=True
    )
    
    command_registry = CommandRegistry()
    
    agent = Agent(
        ai_name="SportsGPT",
        memory_type="local",  # Uses Digital Ocean's mounted filesystem
        workspace=workspace,
        command_registry=command_registry,
        config=config
    )
    return agent

# Initialize AutoGPT agent
agent = init_autogpt()

@app.route('/')
def home():
    matches = read_log_file()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, matches=matches, last_update=last_update)

@app.route('/analyze', methods=['POST'])
async def analyze_matches():
    """Endpoint to analyze matches - runs entirely on Digital Ocean"""
    matches = read_log_file()
    analysis = await analyze_sports_data(matches)
    return {"status": "Analysis completed", "analysis": analysis}

@app.route('/autogpt/analyze', methods=['POST'])
def autogpt_analyze():
    """Use AutoGPT to analyze matches and suggest improvements"""
    matches = read_log_file()
    
    # Run AutoGPT analysis
    result = agent.run_task(
        f"Analyze these sports matches and suggest UI improvements: {matches}"
    )
    
    return {"status": "Analysis completed", "suggestions": result}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
