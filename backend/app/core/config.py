from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "AI Scheduling Agent"
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./scheduling_agent.db")
    
    # For PostgreSQL (production)
    postgres_host: Optional[str] = os.getenv("POSTGRES_HOST")
    postgres_port: Optional[str] = os.getenv("POSTGRES_PORT", "5432")
    postgres_user: Optional[str] = os.getenv("POSTGRES_USER")
    postgres_password: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    postgres_db: Optional[str] = os.getenv("POSTGRES_DB")
    
    @property
    def get_database_url(self) -> str:
        """Get database URL based on environment"""
        if self.database_url.startswith("postgresql://"):
            return self.database_url
        
        # If we have PostgreSQL credentials, construct the URL
        if all([self.postgres_host, self.postgres_user, self.postgres_password, self.postgres_db]):
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
        # Fallback to SQLite
        return self.database_url
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    
    # Gemini Configuration
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = "gemini-1.5-flash"
    gemini_temperature: float = 0.7
    
    # Anthropic Configuration (Claude)
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-3-sonnet-20240229"
    anthropic_temperature: float = 0.7
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # LLM Provider (openai, gemini, anthropic, mock)
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    
    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY")
    if not secret_key:
        # Generate a secure random key if not provided
        secret_key = secrets.token_urlsafe(32)
        print(f"WARNING: No SECRET_KEY provided. Generated temporary key: {secret_key}")
        print("Please set SECRET_KEY in your .env file for production!")
    
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "900"))  # 15 minutes
    
    # OAuth Configuration
    # Google OAuth
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google")
    
    # GitHub OAuth
    github_client_id: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")
    github_redirect_uri: str = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/callback/github")
    
    # OAuth Security
    oauth_state_expire_minutes: int = int(os.getenv("OAUTH_STATE_EXPIRE_MINUTES", "10"))
    allowed_oauth_redirect_uris: List[str] = os.getenv("ALLOWED_OAUTH_REDIRECT_URIS", "http://localhost:3000/auth/callback/google,http://localhost:3000/auth/callback/github").split(",")
    
    # Frontend URLs
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    frontend_login_url: str = os.getenv("FRONTEND_LOGIN_URL", "http://localhost:3000/login")
    
    # CORS Configuration - More restrictive
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True
    
    # Security Headers
    enable_security_headers: bool = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    
    # Session Security
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    
    # Agent Configuration
    max_retries: int = 3
    timeout_seconds: int = 30
    max_participants: int = 10
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # JWT Claims
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "scheduling-agent")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "http://localhost:8000")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields

settings = Settings() 