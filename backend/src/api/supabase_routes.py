"""
Supabase-specific API routes

Separate router for Supabase authentication endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel, EmailStr

from models import UserInfoResponse
from auth.supabase.middleware import get_current_user
from auth.supabase.config import get_supabase_config

logger = logging.getLogger(__name__)

# Create separate router for Supabase routes
router = APIRouter(prefix="/api/v1/supabase", tags=["supabase"])


class ConfirmEmailRequest(BaseModel):
    email: EmailStr


class ConfirmEmailResponse(BaseModel):
    success: bool
    message: str
    error: str | None = None


@router.get("/user/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserInfoResponse:
    """
    Get current authenticated user information.
    
    Returns Supabase user info along with client_id from CSV whitelist.
    """
    try:
        from models import Auth0User  # Reuse Auth0User model structure
        
        user = Auth0User(
            email=current_user["email"],
            sub=current_user["sub"],
            name=current_user.get("name"),
            email_verified=current_user.get("email_verified", False),
            client_id=current_user.get("client_id"),
            whitelisted=current_user.get("whitelisted", False),
        )
        
        return UserInfoResponse(
            success=True,
            user=user
        )
    
    except Exception as e:
        logger.error(f"Error getting user info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/confirm-email", response_model=ConfirmEmailResponse, status_code=status.HTTP_200_OK)
async def confirm_user_email(request: ConfirmEmailRequest) -> ConfirmEmailResponse:
    """
    Auto-confirm a user's email address (for development/testing).
    
    This endpoint uses the service role key to confirm emails without requiring
    the user to click a confirmation link. Useful for development and testing.
    
    WARNING: This should be disabled or restricted in production!
    """
    try:
        config = get_supabase_config()
        if not config:
            return ConfirmEmailResponse(
                success=False,
                message="Supabase not configured",
                error="Supabase configuration is missing"
            )
        
        from supabase import create_client
        
        # Create admin client with service role key
        admin_client = create_client(config.url, config.service_role_key)
        
        # Find user by email
        users_response = admin_client.auth.admin.list_users()
        user = next((u for u in users_response.data.users if u.email == request.email), None)
        
        if not user:
            return ConfirmEmailResponse(
                success=False,
                message=f"User with email {request.email} not found",
                error="User not found"
            )
        
        # Update user to confirm email
        update_data = {
            "email_confirm": True
        }
        
        response = admin_client.auth.admin.update_user_by_id(user.id, update_data)
        
        if response.user and response.user.email_confirmed_at:
            logger.info(f"Email confirmed for user: {request.email}")
            return ConfirmEmailResponse(
                success=True,
                message=f"Email confirmed successfully for {request.email}",
                error=None
            )
        else:
            return ConfirmEmailResponse(
                success=False,
                message="Failed to confirm email",
                error="Email confirmation update failed"
            )
    
    except Exception as e:
        logger.error(f"Error confirming email: {e}", exc_info=True)
        return ConfirmEmailResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )


