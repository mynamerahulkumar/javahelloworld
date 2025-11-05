"""
Logging utilities for per-user logging and log sanitization
"""
import logging
from pathlib import Path
from config.logging_config import USER_LOGS_DIR, LOG_FORMAT, SENSITIVE_FIELDS


def setup_user_logger(client_id: str, error: bool = False) -> logging.Logger:
    """
    Sets up a logger for a specific user (client_id).
    Logs are stored in logs/users/{client_id}_user.log or {client_id}_user_error.log
    """
    log_file_name = f"{client_id}_user{'s_error' if error else ''}.log"
    log_file_path = USER_LOGS_DIR / log_file_name

    logger_name = f"user_logger_{client_id}{'_error' if error else ''}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent logs from going to root logger

    # Check if handler already exists to prevent duplicate logs
    if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename == str(log_file_path.resolve()) for handler in logger.handlers):
        file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitizes a dictionary by replacing sensitive field values with '[REDACTED]'.
    """
    sanitized_data = data.copy()
    for key, value in sanitized_data.items():
        if isinstance(value, dict):
            sanitized_data[key] = sanitize_dict(value)
        elif key.lower() in SENSITIVE_FIELDS:
            sanitized_data[key] = "[REDACTED]"
    return sanitized_data

