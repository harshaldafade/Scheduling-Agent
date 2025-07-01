from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.auth_service import AuthService
from app.models.user import TokenResponse, OAuthCallbackRequest, RefreshTokenRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
auth_service = AuthService()
security = HTTPBearer()

# --- Add these models ---
class OAuthProviderUrl(BaseModel):
    url: str
    state: str

class OAuthUrlsResponse(BaseModel):
    oauth_urls: Dict[str, OAuthProviderUrl]
# ------------------------

@router.get("/auth/oauth-urls", response_model=OAuthUrlsResponse)
async def get_oauth_urls() -> OAuthUrlsResponse:
    """Get OAuth authorization URLs with state parameters"""
    try:
        urls = auth_service.get_oauth_urls()
        # Convert dict of dicts to dict of OAuthProviderUrl
        typed_urls = {k: OAuthProviderUrl(**v) for k, v in urls.items()}
        return OAuthUrlsResponse(oauth_urls=typed_urls)
    except Exception as e:
        logger.error(f"Error getting OAuth URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get OAuth URLs")

@router.post("/auth/google/callback")
async def google_oauth_callback(request: OAuthCallbackRequest) -> TokenResponse:
    """Handle Google OAuth callback with state validation"""
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        token_response = await auth_service.authenticate_google_oauth(request.code, request.state)
        return token_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.post("/auth/github/callback")
async def github_oauth_callback(request: OAuthCallbackRequest) -> TokenResponse:
    """Handle GitHub OAuth callback with state validation"""
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        token_response = await auth_service.authenticate_github_oauth(request.code, request.state)
        return token_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/auth/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user information from JWT token"""
    try:
        token = credentials.credentials
        user = auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "timezone": user.timezone,
            "preferences": user.preferences,
            "availability_patterns": user.availability_patterns,
            "provider": user.provider,
            "provider_id": user.provider_id,
            "avatar_url": user.avatar_url,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@router.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """Refresh JWT access token using refresh token"""
    try:
        token_response = auth_service.refresh_access_token(request.refresh_token)
        return token_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")

@router.post("/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    response: Response = None
) -> Dict[str, str]:
    """Logout user and blacklist token"""
    try:
        token = credentials.credentials
        auth_service.logout(token)
        
        # Clear any cookies if using them
        if response:
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return {"message": "Logout completed"} 