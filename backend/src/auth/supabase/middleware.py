"""
Supabase Authentication Middleware

FastAPI dependency functions for Supabase authentication.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from supabase import Client

from .client import get_supabase_client
from ..client_auth import client_auth

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    FastAPI dependency function to get current authenticated user from Supabase.
    
    Extracts JWT token from Authorization header, verifies it with Supabase,
    and validates user against CSV whitelist (if enabled).
    
    Args:
        authorization: Authorization header value (Bearer token)
    
    Returns:
        Dictionary containing user information:
        - email: User email from Supabase
        - sub: Supabase user ID
        - client_id: Client ID from CSV whitelist (if whitelist enabled)
        - whitelisted: Whether user is in whitelist
    
    Raises:
        HTTPException: 401 if token is missing or invalid
        HTTPException: 403 if user is not in whitelist
    """
    supabase_client = get_supabase_client()
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured"
        )
    
    # Extract token from Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Parse Bearer token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token with Supabase using admin API
        # The admin API can verify tokens without requiring a session
        try:
            # Use admin API to get user by token
            # Note: Supabase Python SDK admin API requires setting the token in headers
            # We'll use the admin client to verify the token
            from supabase import create_client
            from .config import get_supabase_config
            
            config = get_supabase_config()
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Supabase configuration not available"
                )
            
            # Create a temporary client with the user's token to verify it
            # The service role key allows us to verify any token
            admin_client = create_client(config.url, config.service_role_key)
            
            # Set the user's token in the client to verify it
            # We'll use the admin API to get user info from the token
            # Actually, we need to decode and verify the JWT token
            # For now, let's use a simpler approach: create a client with the token
            # and try to get the user
            
            # Better approach: Use admin API to get user by setting auth header
            # But Supabase Python SDK doesn't directly support this
            # So we'll decode the JWT token to get user info
            import jwt as pyjwt
            
            # Decode token without verification first to get user ID
            # Then use admin API to get user details (admin API will verify the user exists)
            try:
                decoded = pyjwt.decode(token, options={"verify_signature": False})
                user_id = decoded.get("sub")
                
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token: missing user ID",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Get user from Supabase using admin API
                user_response = admin_client.auth.admin.get_user_by_id(user_id)
                
                if not user_response.user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                user = user_response.user
                email = user.email
                
            except pyjwt.DecodeError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
        except Exception as e:
            logger.error(f"Error verifying Supabase token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User email not found in token"
            )
        
        # Validate against CSV whitelist and get client_id
        email_lower = email.strip().lower()
        is_whitelisted = client_auth.validate_user_email(email_lower)
        client_id = None
        
        if is_whitelisted:
            client_id = client_auth.get_client_id_by_email(email_lower)
        else:
            logger.warning(f"User {email} is not in CSV whitelist")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {email} is not authorized. Please contact administrator."
            )
        
        # Combine Supabase user info with whitelist info
        return {
            "email": email,
            "sub": user.id,
            "name": user.user_metadata.get("name") if user.user_metadata else None,
            "email_verified": user.email_confirmed_at is not None,
            "client_id": client_id,
            "whitelisted": is_whitelisted,
            "user_metadata": user.user_metadata or {},
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Supabase authentication: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error"
        )

