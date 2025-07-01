from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.schedule import Meeting

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    timezone = Column(String, default="UTC")
    preferences = Column(JSON, default={})
    availability_patterns = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    # OAuth fields
    provider = Column(String, nullable=True)  # 'google', 'github'
    provider_id = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    
    # Security fields
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organized_meetings = relationship("Meeting", back_populates="organizer", lazy="dynamic")

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    timezone: Optional[str] = "UTC"
    preferences: Optional[Dict[str, Any]] = {}
    availability_patterns: Optional[Dict[str, Any]] = {}
    provider: Optional[str] = None
    provider_id: Optional[str] = None
    avatar_url: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    availability_patterns: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    timezone: str
    preferences: Dict[str, Any]
    availability_patterns: Dict[str, Any]
    provider: Optional[str] = None
    provider_id: Optional[str] = None
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OAuthUserInfo(BaseModel):
    """OAuth user information from providers"""
    provider: str
    provider_id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None

class TokenResponse(BaseModel):
    """JWT token response with refresh token"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str

class OAuthCallbackRequest(BaseModel):
    """OAuth callback request with state validation"""
    code: str
    state: Optional[str] = None 