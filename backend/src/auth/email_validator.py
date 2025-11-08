"""
Email validation middleware for backend API routes
Validates user email against CSV whitelist
"""
from typing import Tuple, Optional
from auth.client_auth import client_auth
import logging

logger = logging.getLogger(__name__)


def validate_email_against_csv(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email against CSV whitelist and return client_id if found.
    
    Args:
        email: User email to validate
        
    Returns:
        Tuple of (is_valid, client_id)
        - is_valid: True if email exists in CSV whitelist
        - client_id: Client ID from CSV if found, None otherwise
    """
    if not email:
        return False, None
    
    email = email.strip().lower()
    
    # Check if email exists in CSV whitelist
    is_whitelisted = client_auth.validate_user_email(email)
    
    if not is_whitelisted:
        logger.warning(f"Email validation failed: {email} is not in CSV whitelist")
        return False, None
    
    # Get client_id from CSV
    client_id = client_auth.get_client_id_by_email(email)
    
    if not client_id:
        logger.warning(f"Email found in whitelist but client_id not found for: {email}")
        return False, None
    
    logger.info(f"Email validated successfully: {email} (client_id: {client_id})")
    return True, client_id





