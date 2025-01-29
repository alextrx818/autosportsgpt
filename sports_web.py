from flask import Flask, render_template_string
import os
from datetime import datetime
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Sports Monitor</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <style>
        body {
            font-family: monospace;
            background: #1a1a1a;
            color: #ffffff;
            padding: 20px;
            line-height: 1.6;
        }
        .match {
            margin-bottom: 20px;
            border-left: 3px solid #333;
            padding-left: 10px;
        }
        .sport-header {
            color: #00ff00;
            font-size: 1.2em;
            margin: 20px 0;
            border-bottom: 1px solid #333;
        }
        pre {
            white-space: pre-wrap;
            margin: 0;
        }
        .last-update {
            color: #888;
            font-size: 0.8em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>🎮 Live Sports Monitor</h1>
    <div id="matches">
        <pre>{{ matches | safe }}</pre>
    </div>
    <div class="last-update">
        Last Update: {{ last_update }}
        <br>
        Auto-refreshing every 60 seconds...
    </div>
    <script>
        // Auto refresh every 60 seconds
        setTimeout(() => window.location.reload(), 60000);
    </script>
</body>
</html>
"""

def read_log_file():
    """Read the latest matches from the log file"""
    try:
        with open('sports_monitor.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Get the latest complete update
        matches = []
        latest_update = []
        in_update = False
        
        for line in reversed(lines):
            # Split the log line to get the actual message
            parts = line.split('|')
            if len(parts) >= 2:
                message = parts[-1].strip()
                
                # Check for start/end markers
                if "Starting Sports Monitor Bot" in message:
                    if latest_update:
                        matches = latest_update
                    break
                    
                # Only add lines that are match data (contain emojis or sport headers)
                if any(emoji in message for emoji in ['⚽', '🏀', '🎾', '🏐', '🏒', '🤾', '⚾', '🏈', '🎱', '🎯', '🏓', '🏸', '🏉', '📱']):
                    latest_update.insert(0, message)
            
        return '\n'.join(matches) if matches else "Waiting for match data..."
    except Exception as e:
        return f"Error reading log file: {str(e)}"

@app.route('/')
def home():
    matches = read_log_file()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, matches=matches, last_update=last_update)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
