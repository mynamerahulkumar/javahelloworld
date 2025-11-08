"""
Supabase Configuration Module

Loads and validates Supabase configuration from environment variables.
"""
import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SupabaseConfig:
    """Supabase configuration"""
    url: str
    service_role_key: str
    anon_key: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.url:
            raise ValueError("SUPABASE_URL is required")
        if not self.service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY is required")
        
        # Remove trailing slash from URL if present
        self.url = self.url.rstrip("/")


_config: Optional[SupabaseConfig] = None


def get_supabase_config() -> Optional[SupabaseConfig]:
    """
    Get Supabase configuration from environment variables.
    
    Returns:
        SupabaseConfig instance if all required variables are set, None otherwise.
    """
    global _config
    
    if _config is not None:
        return _config
    
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not service_role_key:
        logger.warning(
            "Supabase is not fully configured. "
            "Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY. "
            "Optional: SUPABASE_ANON_KEY"
        )
        return None
    
    try:
        _config = SupabaseConfig(
            url=url,
            service_role_key=service_role_key,
            anon_key=anon_key
        )
        logger.info("Supabase configuration loaded successfully")
        return _config
    except ValueError as e:
        logger.error(f"Invalid Supabase configuration: {e}")
        return None






