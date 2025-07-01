from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

# Initialize service
user_service = UserService()

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        user = user_service.create_user(user_data)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users", response_model=List[UserResponse])
async def get_all_users():
    """Get all active users"""
    try:
        users = user_service.get_all_users()
        return [UserResponse.from_orm(user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    """Update user information"""
    try:
        user = user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Soft delete user"""
    try:
        success = user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") 