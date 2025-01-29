# AutoSportsGPT

A sports monitoring bot that runs on Digital Ocean and can be edited from any computer using Windsurf.

## Quick Start for New Computers

1. Open Windsurf
2. Clone this repository:
   ```
   https://github.com/alextrx818/autosportsgpt.git
   ```

3. Create a `.env` file with your API keys:
   ```
   SPORTS_API_KEY=your_key_here
   SPORTS_API_HOST=api.b365api.com
   ```

That's it! The bot is already running on Digital Ocean at:
`https://plankton-app-qyijl.ondigitalocean.app/`

## Development Workflow

1. Make your code changes in Windsurf
2. Run the deploy script to update Digital Ocean:
   ```
   ./deploy.ps1 "Your commit message"
   ```
3. Digital Ocean will automatically rebuild and run the new version

## Benefits
- Edit from any computer using Windsurf
- No local CPU usage - bot runs on Digital Ocean
- Changes automatically deploy to production
- Access the bot from anywhere

## Project Structure
- `sports_monitor_bot.py` - Main bot (runs on Digital Ocean)
- `local_monitor.py` - Light client to view matches locally
- `deploy.ps1` - Script to deploy changes to Digital Ocean

## Note
The CPU-intensive bot runs entirely on Digital Ocean. Your local computer only needs to run Windsurf for editing code.