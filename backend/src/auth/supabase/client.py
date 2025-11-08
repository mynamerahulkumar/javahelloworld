"""
Supabase Client Module

Creates and manages Supabase client instances for server-side operations.
"""
import logging
from typing import Optional
from supabase import create_client, Client
from .config import get_supabase_config

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Get or create Supabase client instance.
    
    Uses service role key for server-side operations (bypasses RLS).
    
    Returns:
        Supabase Client instance if configured, None otherwise.
    """
    global _client
    
    if _client is not None:
        return _client
    
    config = get_supabase_config()
    if not config:
        logger.warning("Cannot create Supabase client: configuration not available")
        return None
    
    try:
        _client = create_client(config.url, config.service_role_key)
        logger.info("Supabase client created successfully")
        return _client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None


def get_supabase_client_anon() -> Optional[Client]:
    """
    Get or create Supabase client instance using anon key.
    
    Uses anon key for client-side-like operations (respects RLS).
    
    Returns:
        Supabase Client instance if configured, None otherwise.
    """
    config = get_supabase_config()
    if not config:
        logger.warning("Cannot create Supabase client: configuration not available")
        return None
    
    if not config.anon_key:
        logger.warning("SUPABASE_ANON_KEY not set, using service role key")
        return get_supabase_client()
    
    try:
        return create_client(config.url, config.anon_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client with anon key: {e}")
        return None





