"""
Configuration module for loading environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Delta Exchange API credentials (from environment variables or .env file)
DELTA_API_KEY = os.getenv("DELTA_API_KEY")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET")
DELTA_BASE_URL = os.getenv("DELTA_BASE_URL", "https://api.india.delta.exchange")

# Price fetch interval in seconds (configurable via environment variable, default 5 seconds)
PRICE_FETCH_INTERVAL_SECONDS = int(os.getenv("PRICE_FETCH_INTERVAL_SECONDS", "5"))

