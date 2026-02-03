"""Configuration for the MCP NBA server."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY", "")
BALLDONTLIE_BASE_URL = "https://api.balldontlie.io/v1"

# Rate limiting: 5 requests per minute for free tier
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

# HTTP Client settings
REQUEST_TIMEOUT_SECONDS = 10
