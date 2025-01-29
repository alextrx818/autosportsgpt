"""Configuration for remote Digital Ocean instance"""

# Digital Ocean App URL
REMOTE_API_URL = "https://plankton-app-qyijl.ondigitalocean.app"

# API endpoints
MATCHES_ENDPOINT = f"{REMOTE_API_URL}/matches"
LIVE_MATCHES_ENDPOINT = f"{REMOTE_API_URL}/live"
HEALTH_CHECK_ENDPOINT = f"{REMOTE_API_URL}/health"

# Whether to use remote or local processing
USE_REMOTE = True
