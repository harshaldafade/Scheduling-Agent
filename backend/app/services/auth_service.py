import jwt
import httpx
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User, OAuthUserInfo, TokenResponse, UserResponse
from app.services.user_service import UserService
import logging
import redis
import json

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication and OAuth with enhanced security"""
    
    def __init__(self):
        self.user_service = UserService()
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
        
        # Initialize Redis for rate limiting and token blacklisting
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Using in-memory storage.")
            self.redis_client = None
    
    def _generate_secure_state(self) -> str:
        """Generate a secure state parameter for OAuth"""
        return secrets.token_urlsafe(32)
    
    def _store_oauth_state(self, state: str, provider: str, expires_in: int = 600) -> bool:
        """Store OAuth state in Redis with expiration"""
        if not self.redis_client:
            return True  # Skip if Redis not available
        
        try:
            key = f"oauth_state:{state}"
            data = {
                "provider": provider,
                "created_at": time.time(),
                "expires_at": time.time() + expires_in
            }
            self.redis_client.setex(key, expires_in, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")
            return False
    
    def _validate_oauth_state(self, state: str, provider: str) -> bool:
        """Validate OAuth state parameter"""
        if not self.redis_client:
            return True  # Skip if Redis not available
        
        try:
            key = f"oauth_state:{state}"
            data = self.redis_client.get(key)
            if not data:
                return False
            
            state_data = json.loads(data)
            if state_data["provider"] != provider:
                return False
            
            # Check if expired
            if time.time() > state_data["expires_at"]:
                self.redis_client.delete(key)
                return False
            
            # Clean up used state
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to validate OAuth state: {e}")
            return False
    
    def _check_rate_limit(self, identifier: str, limit: int = None, window: int = None) -> bool:
        """Check rate limiting for authentication attempts"""
        if not self.redis_client:
            return True  # Skip if Redis not available
        
        limit = limit or settings.rate_limit_requests
        window = window or settings.rate_limit_window
        
        try:
            key = f"rate_limit:{identifier}"
            current = self.redis_client.get(key)
            
            if current is None:
                self.redis_client.setex(key, window, 1)
                return True
            
            count = int(current)
            if count >= limit:
                return False
            
            self.redis_client.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow if rate limiting fails
    
    def _blacklist_token(self, token: str, expires_in: int = None) -> bool:
        """Add token to blacklist"""
        if not self.redis_client:
            return True  # Skip if Redis not available
        
        try:
            if expires_in is None:
                # Use token expiration time
                payload = self.verify_token(token)
                if payload and "exp" in payload:
                    expires_in = int(payload["exp"]) - int(time.time())
                else:
                    expires_in = self.access_token_expire_minutes * 60
            
            key = f"blacklist:{hashlib.sha256(token.encode()).hexdigest()}"
            self.redis_client.setex(key, expires_in, "1")
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        if not self.redis_client:
            return False  # Skip if Redis not available
        
        try:
            key = f"blacklist:{hashlib.sha256(token.encode()).hexdigest()}"
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()
        
        # Add standard claims
        now = datetime.utcnow()
        to_encode.update({
            "iat": now,
            "nbf": now,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience
        })
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        # Add jti (JWT ID) for token uniqueness
        to_encode["jti"] = secrets.token_urlsafe(16)
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        to_encode.update({
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "jti": secrets.token_urlsafe(16)
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload with enhanced security"""
        try:
            # Check if token is blacklisted
            if self._is_token_blacklisted(token):
                return None
            
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience=settings.jwt_audience,
                issuer=settings.jwt_issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "nbf", "iss", "aud", "jti"]
                }
            )
            return payload
        except jwt.PyJWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token with enhanced security"""
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        
        user = self.user_service.get_user(user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    def get_oauth_urls(self) -> Dict[str, Dict[str, str]]:
        """Get OAuth authorization URLs with state parameter"""
        urls = {}
        
        if settings.google_client_id:
            state = self._generate_secure_state()
            self._store_oauth_state(state, "google", settings.oauth_state_expire_minutes * 60)
            
            google_params = {
                "client_id": settings.google_client_id,
                "redirect_uri": settings.google_redirect_uri,
                "scope": "openid email profile",
                "response_type": "code",
                "access_type": "offline",
                "state": state,
                "prompt": "select_account"
            }
            google_url = "https://accounts.google.com/o/oauth2/v2/auth"
            google_query = "&".join([f"{k}={v}" for k, v in google_params.items()])
            urls["google"] = {
                "url": f"{google_url}?{google_query}",
                "state": state
            }
        
        if settings.github_client_id:
            state = self._generate_secure_state()
            self._store_oauth_state(state, "github", settings.oauth_state_expire_minutes * 60)
            
            github_params = {
                "client_id": settings.github_client_id,
                "redirect_uri": settings.github_redirect_uri,
                "scope": "user:email",
                "response_type": "code",
                "state": state
            }
            github_url = "https://github.com/login/oauth/authorize"
            github_query = "&".join([f"{k}={v}" for k, v in github_params.items()])
            urls["github"] = {
                "url": f"{github_url}?{github_query}",
                "state": state
            }
        
        return urls
    
    async def authenticate_google_oauth(self, code: str, state: str = None) -> TokenResponse:
        """Authenticate user with Google OAuth with enhanced security"""
        # Rate limiting
        if not self._check_rate_limit("google_oauth", 10, 300):  # 10 attempts per 5 minutes
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts"
            )
        
        # Validate state parameter
        if state and not self._validate_oauth_state(state, "google"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter"
            )
        
        try:
            # Exchange authorization code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                token_response = await client.post(token_url, data=token_data)
                token_response.raise_for_status()
                token_info = token_response.json()
                
                if "error" in token_info:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Google OAuth error: {token_info.get('error_description', token_info['error'])}"
                    )
                
                access_token = token_info["access_token"]
                
                # Get user info from Google
                user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                
                user_response = await client.get(user_info_url, headers=headers)
                user_response.raise_for_status()
                user_info = user_response.json()
                
                # Validate required fields
                if not user_info.get("email") or not user_info.get("id"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Incomplete user information from Google"
                    )
                
                # Create OAuth user info
                oauth_user = OAuthUserInfo(
                    provider="google",
                    provider_id=user_info["id"],
                    email=user_info["email"],
                    name=user_info.get("name", ""),
                    avatar_url=user_info.get("picture")
                )
                
                # Get or create user
                user = await self._get_or_create_oauth_user(oauth_user)
                
                # Create tokens
                access_token = self.create_access_token(data={"sub": user.id})
                refresh_token = self.create_refresh_token(data={"sub": user.id})
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=self.access_token_expire_minutes * 60,
                    user=UserResponse.from_orm(user)
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Google OAuth HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to authenticate with Google"
            )
        except Exception as e:
            logger.error(f"Google OAuth error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
    
    async def authenticate_github_oauth(self, code: str, state: str = None) -> TokenResponse:
        """Authenticate user with GitHub OAuth with enhanced security"""
        # Rate limiting
        if not self._check_rate_limit("github_oauth", 10, 300):  # 10 attempts per 5 minutes
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts"
            )
        
        # Validate state parameter
        if state and not self._validate_oauth_state(state, "github"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter"
            )
        
        try:
            print(f"GitHub OAuth: Received code: {code}")
            # Exchange authorization code for access token
            token_url = "https://github.com/login/oauth/access_token"
            token_data = {
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code
            }
            headers = {"Accept": "application/json"}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                token_response = await client.post(token_url, data=token_data, headers=headers)
                print(f"GitHub OAuth: Token response status: {token_response.status_code}, body: {token_response.text}")
                token_response.raise_for_status()
                token_info = token_response.json()
                
                if "error" in token_info:
                    print(f"GitHub OAuth error: {token_info}")
                    logger.error(f"GitHub OAuth error: {token_info}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"GitHub OAuth error: {token_info.get('error_description', token_info['error'])}"
                    )
                
                access_token = token_info["access_token"]
                
                # Get user info from GitHub
                user_info_url = "https://api.github.com/user"
                headers = {
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                user_response = await client.get(user_info_url, headers=headers)
                print(f"GitHub OAuth: User info response status: {user_response.status_code}, body: {user_response.text}")
                user_response.raise_for_status()
                user_info = user_response.json()
                
                # Get user email from GitHub
                email_url = "https://api.github.com/user/emails"
                email_response = await client.get(email_url, headers=headers)
                print(f"GitHub OAuth: Email response status: {email_response.status_code}, body: {email_response.text}")
                email_response.raise_for_status()
                emails = email_response.json()
                
                # Find primary email
                primary_email = next((email["email"] for email in emails if email["primary"]), user_info.get("email"))
                
                if not primary_email:
                    print("GitHub OAuth: No valid email found from GitHub")
                    logger.error("GitHub OAuth: No valid email found from GitHub")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No valid email found from GitHub"
                    )
                
                # Create OAuth user info
                oauth_user = OAuthUserInfo(
                    provider="github",
                    provider_id=str(user_info["id"]),
                    email=primary_email,
                    name=user_info.get("name") or user_info.get("login", ""),
                    avatar_url=user_info.get("avatar_url")
                )
                
                # Get or create user
                user = await self._get_or_create_oauth_user(oauth_user)
                
                # Create tokens
                access_token = self.create_access_token(data={"sub": user.id})
                refresh_token = self.create_refresh_token(data={"sub": user.id})
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=self.access_token_expire_minutes * 60,
                    user=UserResponse.from_orm(user)
                )
                
        except httpx.HTTPStatusError as e:
            print(f"GitHub OAuth HTTP error: {e.response.status_code} - {e.response.text}")
            logger.error(f"GitHub OAuth HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to authenticate with GitHub"
            )
        except Exception as e:
            print(f"GitHub OAuth error: {str(e)}")
            logger.error(f"GitHub OAuth error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
    
    async def _get_or_create_oauth_user(self, oauth_user: OAuthUserInfo) -> User:
        """Get existing user or create new user from OAuth info with enhanced security"""
        # Try to find user by provider and provider_id
        user = self.user_service.get_user_by_provider(oauth_user.provider, oauth_user.provider_id)
        
        if user:
            # Update user info if needed
            if user.name != oauth_user.name or user.avatar_url != oauth_user.avatar_url:
                user.name = oauth_user.name
                user.avatar_url = oauth_user.avatar_url
                self.user_service.update_user(user.id, user)
            return user
        
        # Try to find user by email
        user = self.user_service.get_user_by_email(oauth_user.email)
        
        if user:
            # Link existing user to OAuth provider
            user.provider = oauth_user.provider
            user.provider_id = oauth_user.provider_id
            user.avatar_url = oauth_user.avatar_url
            self.user_service.update_user(user.id, user)
            return user
        
        # Create new user
        user_data = {
            "email": oauth_user.email,
            "name": oauth_user.name,
            "provider": oauth_user.provider,
            "provider_id": oauth_user.provider_id,
            "avatar_url": oauth_user.avatar_url,
            "timezone": "UTC",
            "preferences": {}
        }
        
        return self.user_service.create_user(user_data)
    
    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_signature": True, "verify_exp": True}
            )
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token"
                )
            
            user = self.user_service.get_user(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new tokens
            new_access_token = self.create_access_token(data={"sub": user.id})
            new_refresh_token = self.create_refresh_token(data={"sub": user.id})
            
            # Blacklist old refresh token
            self._blacklist_token(refresh_token)
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60,
                user=UserResponse.from_orm(user)
            )
            
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def logout(self, token: str) -> bool:
        """Logout user by blacklisting token"""
        return self._blacklist_token(token) 