import logging
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base

# Import models to ensure they are registered with SQLAlchemy
from app.models import user, schedule

from app.api.routes import scheduling, users, preferences, auth

# Set up logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Scheduling Agent API",
    description="An intelligent scheduling agent that coordinates meetings using AI",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Configure with your domain in production
    )

# Configure CORS with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "geolocation=()"
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    print(f"{request.method} {request.url.path} - {request.client.host if request.client else 'unknown'}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Include API routes
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(scheduling.router, prefix="/api/v1", tags=["scheduling"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(preferences.router, prefix="/api/v1", tags=["preferences"])

@app.get("/")
async def root():
    return {
        "message": "AI Scheduling Agent API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.environment
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 