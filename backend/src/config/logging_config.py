"""
Logging configuration for the application
"""
import os
from pathlib import Path

# Base directory for logs (relative to backend root)
LOGS_BASE_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_BASE_DIR.mkdir(parents=True, exist_ok=True)

# General application log
APP_LOG_FILE = LOGS_BASE_DIR / "bot.log"

# Per-user log directory
USER_LOGS_DIR = LOGS_BASE_DIR / "users"
USER_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Log retention settings
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "7"))  # Default 7 days
LOG_MAX_SIZE_MB = int(os.getenv("LOG_MAX_SIZE_MB", "100"))  # Default 100 MB
LOG_CLEANUP_INTERVAL_HOURS = int(os.getenv("LOG_CLEANUP_INTERVAL_HOURS", "24"))  # Default 24 hours

# Logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Sensitive fields to sanitize in logs
SENSITIVE_FIELDS = [
    "api_key", "api_secret", "x_delta_api_key", "x_delta_api_secret",
    "X-Delta-API-Key", "X-Delta-API-Secret", "password", "credential"
]

