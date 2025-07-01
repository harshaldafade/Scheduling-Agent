from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.preference_service import PreferenceService
from app.services.user_service import UserService
from app.services.auth_service import AuthService

router = APIRouter()

# Initialize services
preference_service = PreferenceService()
user_service = UserService()
auth_service = AuthService()
security = HTTPBearer()

class PreferenceUpdateRequest(BaseModel):
    preferences: Dict[str, Any]

class FeedbackRequest(BaseModel):
    feedback: str
    meeting_context: Optional[Dict[str, Any]] = {}

class SimilarUsersRequest(BaseModel):
    limit: Optional[int] = 5

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

@router.get("/preferences", response_model=Dict[str, Any])
async def get_user_preferences(current_user = Depends(get_current_user)):
    """Get current user's preferences"""
    try:
        preferences = preference_service.get_user_preferences(current_user.id)
        return {
            "user_id": current_user.id,
            "preferences": preferences,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    request: PreferenceUpdateRequest,
    current_user = Depends(get_current_user)
):
    """Update current user's preferences"""
    try:
        # Update preferences
        updated_user = user_service.update_user_preferences(current_user.id, request.preferences)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {
            "user_id": current_user.id,
            "preferences": updated_user.preferences,
            "message": "Preferences updated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/preferences/feedback", response_model=Dict[str, Any])
async def process_feedback(
    request: FeedbackRequest,
    current_user = Depends(get_current_user)
):
    """Process user feedback and learn preferences"""
    try:
        # Learn from feedback
        updated_preferences = preference_service.learn_from_feedback(
            current_user.id, 
            request.feedback, 
            request.meeting_context or {}
        )
        
        return {
            "user_id": current_user.id,
            "feedback_processed": request.feedback,
            "updated_preferences": updated_preferences,
            "message": "Feedback processed and preferences updated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/preferences/similar-users", response_model=Dict[str, Any])
async def find_similar_users(
    request: SimilarUsersRequest,
    current_user = Depends(get_current_user)
):
    """Find users with similar preferences"""
    try:
        # Find similar users
        similar_users = preference_service.find_similar_users(
            current_user.id, 
            request.limit
        )
        
        return {
            "user_id": current_user.id,
            "similar_users": similar_users,
            "count": len(similar_users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/preferences/recommendations", response_model=Dict[str, Any])
async def get_preference_recommendations(current_user = Depends(get_current_user)):
    """Get personalized recommendations based on user preferences"""
    try:
        # Get recommendations
        recommendations = preference_service.get_preference_recommendations(current_user.id)
        
        return {
            "user_id": current_user.id,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/preferences/analytics", response_model=Dict[str, Any])
async def get_preference_analytics(current_user = Depends(get_current_user)):
    """Get analytics about user preferences"""
    try:
        preferences = preference_service.get_user_preferences(current_user.id)
        similar_users = preference_service.find_similar_users(current_user.id, limit=10)
        
        # Calculate analytics
        analytics = {
            "total_preferences": len(preferences),
            "preference_categories": list(preferences.keys()),
            "similar_users_count": len(similar_users),
            "average_similarity": sum(u["similarity_score"] for u in similar_users) / len(similar_users) if similar_users else 0,
            "preference_completeness": _calculate_completeness(preferences),
            "most_common_preferences": _get_most_common_preferences(preferences)
        }
        
        return {
            "user_id": current_user.id,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

def _calculate_completeness(preferences: Dict[str, Any]) -> float:
    """Calculate how complete the user's preferences are"""
    # Define expected preference categories
    expected_categories = [
        "preferred_time_slots",
        "preferred_duration", 
        "preferred_meeting_types",
        "timezone",
        "availability_patterns"
    ]
    
    filled_categories = sum(1 for cat in expected_categories if cat in preferences and preferences[cat])
    return filled_categories / len(expected_categories)

def _get_most_common_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Get the most common preference values"""
    common_prefs = {}
    
    if "preferred_time_slots" in preferences:
        common_prefs["time_slots"] = preferences["preferred_time_slots"]
    
    if "preferred_duration" in preferences:
        common_prefs["duration"] = preferences["preferred_duration"]
    
    if "preferred_meeting_types" in preferences:
        common_prefs["meeting_types"] = preferences["preferred_meeting_types"]
    
    return common_prefs 