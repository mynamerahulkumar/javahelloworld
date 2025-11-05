"""
Configuration management for trading API
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Delta Exchange API Configuration
# These are fallback values if not provided via headers
DELTA_BASE_URL = os.getenv("DELTA_BASE_URL", "https://api.india.delta.exchange")
DELTA_API_KEY = os.getenv("DELTA_API_KEY", "")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET", "")

