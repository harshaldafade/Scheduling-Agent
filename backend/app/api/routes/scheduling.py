from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import logging

from app.agents.scheduling_agent import SchedulingAgent
from app.services.user_service import UserService
from app.services.schedule_service import ScheduleService
from app.services.auth_service import AuthService
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Initialize services
scheduling_agent = SchedulingAgent()
user_service = UserService()
schedule_service = ScheduleService()
auth_service = AuthService()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

class SchedulingRequest(BaseModel):
    request_text: str
    participants: Optional[List[int]] = []
    duration_minutes: Optional[int] = 60
    meeting_type: Optional[str] = "general"
    constraints: Optional[Dict[str, Any]] = {}

class SchedulingResponse(BaseModel):
    success: bool
    message: str
    meeting_proposal: Optional[Dict[str, Any]] = None
    alternative_slots: Optional[List[Dict[str, Any]]] = None
    meetings: Optional[List[Dict[str, Any]]] = None
    agent_reasoning: Optional[str] = None
    raw_ai_output: Optional[str] = None

class MeetingProposal(BaseModel):
    title: str
    description: Optional[str] = None
    participants: List[int]
    start_time: datetime
    end_time: datetime
    meeting_type: str = "general"
    constraints: Optional[Dict[str, Any]] = {}

class ConflictResolutionRequest(BaseModel):
    meeting_id: int
    conflict_type: str = "time_conflict"
    user_feedback: Optional[str] = None

class PreferenceLearningRequest(BaseModel):
    feedback: str
    meeting_context: Optional[Dict[str, Any]] = {}

class ConfirmationRequest(BaseModel):
    meeting_id: int = 0  # Optional for creation
    action: str  # "confirm_delete", "confirm_delete_all", "confirm_update", "confirm_create"
    updates: Optional[Dict[str, Any]] = None
    meeting_proposal: Optional[Dict[str, Any]] = None

@router.post("/schedule", response_model=SchedulingResponse)
async def schedule_meeting(
    request: SchedulingRequest,
    current_user = Depends(get_current_user)
):
    print("=== /schedule endpoint called ===")
    try:
        print("Validating participants...")
        # Validate participants exist
        if request.participants:
            for participant_id in request.participants:
                participant = user_service.get_user(participant_id)
                if not participant:
                    print(f"Participant {participant_id} not found!")
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Participant {participant_id} not found"
                    )
        print("Calling scheduling_agent.process_message...")
        # Process the message with conversation context using current user
        agent_response = await scheduling_agent.process_message(current_user.id, request.request_text)
        print(f"Agent response: {agent_response}")
        if not agent_response["success"]:
            print(f"Agent error: {agent_response.get('message', 'Unknown error')}")
            # Return the error and raw LLM output to the frontend for debugging
            return SchedulingResponse(
                success=False,
                message=agent_response.get("message", "Request could not be processed"),
                agent_reasoning=agent_response.get("agent_reasoning"),
                alternative_slots=None,
                meetings=None,
                meeting_proposal=None,
                raw_ai_output=agent_response.get("raw_ai_output")
            )
        print("Returning SchedulingResponse...")
        # Return the structured response
        return SchedulingResponse(
            success=True,
            message=agent_response.get("message", "Request processed successfully"),
            meeting_proposal=agent_response.get("meeting_proposal"),
            alternative_slots=agent_response.get("alternative_slots"),
            meetings=agent_response.get("meetings"),
            agent_reasoning=agent_response.get("agent_reasoning"),
            raw_ai_output=agent_response.get("raw_ai_output")
        )
    except HTTPException:
        print("HTTPException raised!")
        raise
    except Exception as e:
        print(f"Exception in /schedule: {e}")
        import traceback
        print(traceback.format_exc())
        logger.error(f"Error scheduling meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/propose-meeting", response_model=Dict[str, Any])
async def propose_meeting(
    proposal: MeetingProposal,
    current_user = Depends(get_current_user)
):
    """Create a meeting proposal"""
    try:
        # Validate participants exist
        for participant_id in proposal.participants:
            participant = user_service.get_user(participant_id)
            if not participant:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Participant {participant_id} not found"
                )
        
        # Create meeting with current user as organizer
        meeting_data = {
            "title": proposal.title,
            "description": proposal.description,
            "organizer_id": current_user.id,
            "participants": proposal.participants,
            "start_time": proposal.start_time,
            "end_time": proposal.end_time,
            "duration_minutes": int((proposal.end_time - proposal.start_time).total_seconds() / 60),
            "meeting_type": proposal.meeting_type,
            "constraints": proposal.constraints or {},
            "status": "proposed"
        }
        
        meeting = schedule_service.create_meeting(meeting_data)
        if not meeting:
            raise HTTPException(status_code=500, detail="Failed to create meeting")
        
        return {
            "success": True,
            "meeting_id": meeting.id,
            "title": meeting.title,
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat(),
            "participants": meeting.participants,
            "status": meeting.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error proposing meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/resolve-conflicts", response_model=Dict[str, Any])
async def resolve_conflicts(
    request: ConflictResolutionRequest,
    current_user = Depends(get_current_user)
):
    """Resolve scheduling conflicts"""
    try:
        # Validate meeting exists and user has access
        meeting = schedule_service.get_meeting(request.meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.organizer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this meeting")
        
        # Use agent to resolve conflicts
        agent_response = await scheduling_agent.run(
            f"Resolve conflicts for meeting {request.meeting_id}. "
            f"Conflict type: {request.conflict_type}. "
            f"User feedback: {request.user_feedback or 'No feedback provided'}"
        )
        
        if not agent_response["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Agent error: {agent_response['error']}"
            )
        
        # Parse agent response
        try:
            response_data = json.loads(agent_response["output"])
            return {
                "success": True,
                "meeting_id": request.meeting_id,
                "conflict_type": request.conflict_type,
                "resolution": response_data,
                "agent_reasoning": agent_response["output"]
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "meeting_id": request.meeting_id,
                "conflict_type": request.conflict_type,
                "agent_reasoning": agent_response["output"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving conflicts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/learn-preferences", response_model=Dict[str, Any])
async def learn_user_preferences(
    request: PreferenceLearningRequest,
    current_user = Depends(get_current_user)
):
    """Learn user preferences from feedback"""
    try:
        # Update user preferences based on feedback
        preferences_update = {
            "feedback_history": request.meeting_context.get("feedback_history", []) + [request.feedback],
            "last_updated": datetime.now().isoformat()
        }
        
        updated_user = user_service.update_user_preferences(current_user.id, preferences_update)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "user_id": current_user.id,
            "preferences": updated_user.preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error learning preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/optimize-schedule", response_model=Dict[str, Any])
async def optimize_user_schedule(
    target_date: str,
    current_user = Depends(get_current_user)
):
    """Optimize user's schedule for a specific date"""
    try:
        # Parse target date
        try:
            target_datetime = datetime.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
        
        # Get schedule optimizations
        optimizations = schedule_service.optimize_schedule(current_user.id, target_datetime)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "target_date": target_date,
            "optimizations": optimizations,
            "optimization_count": len(optimizations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics", response_model=Dict[str, Any])
async def get_meeting_analytics(
    start_date: str, 
    end_date: str,
    current_user = Depends(get_current_user)
):
    """Get meeting analytics for current user in a date range"""
    try:
        # Parse dates
        try:
            start_datetime = datetime.fromisoformat(start_date)
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
        
        # Get analytics
        analytics = schedule_service.get_meeting_analytics(current_user.id, start_datetime, end_datetime)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/auto-reschedule", response_model=Dict[str, Any])
async def auto_reschedule_conflicts(
    meeting_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Automatically reschedule conflicting meetings"""
    try:
        # Validate required fields
        required_fields = ["start_time", "end_time", "participants"]
        for field in required_fields:
            if field not in meeting_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Parse times
        try:
            start_time = datetime.fromisoformat(meeting_data["start_time"])
            end_time = datetime.fromisoformat(meeting_data["end_time"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use ISO format")
        
        # Validate participants
        for participant_id in meeting_data["participants"]:
            participant = user_service.get_user(participant_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found")
        
        # Auto-reschedule conflicting meetings
        rescheduled_meetings = schedule_service.auto_reschedule_conflicting_meetings(meeting_data)
        
        return {
            "success": True,
            "rescheduled_meetings": rescheduled_meetings,
            "rescheduled_count": len(rescheduled_meetings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-rescheduling: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/find-optimal-time", response_model=Dict[str, Any])
async def find_optimal_meeting_time(
    participant_ids: str,  # Comma-separated user IDs
    duration_minutes: int = 60,
    start_date: str = None,
    end_date: str = None,
    preferences: Optional[Dict[str, Any]] = None,
    current_user = Depends(get_current_user)
):
    """Find the optimal meeting time for participants"""
    try:
        # Parse participant IDs
        try:
            participant_id_list = [int(pid.strip()) for pid in participant_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid participant IDs format")
        
        # Validate participants exist
        for participant_id in participant_id_list:
            participant = user_service.get_user(participant_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found")
        
        # Parse dates
        if not start_date:
            start_date = datetime.now().isoformat()
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        try:
            start_datetime = datetime.fromisoformat(start_date)
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format")
        
        # Find optimal time
        optimal_time = schedule_service.find_optimal_meeting_time(
            participant_id_list, duration_minutes, start_datetime, end_datetime, preferences
        )
        
        return {
            "success": True,
            "participants": participant_id_list,
            "duration_minutes": duration_minutes,
            "optimal_time": optimal_time,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding optimal time: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/meetings/{meeting_id}", response_model=Dict[str, Any])
async def update_meeting(
    meeting_id: int,
    updates: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Update meeting information"""
    try:
        # Validate meeting exists and user has access
        meeting = schedule_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.organizer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this meeting")
        
        # Create MeetingUpdate object
        from app.models.schedule import MeetingUpdate
        meeting_update = MeetingUpdate(**updates)
        
        # Update meeting
        updated_meeting = schedule_service.update_meeting(meeting_id, meeting_update)
        if not updated_meeting:
            raise HTTPException(status_code=500, detail="Failed to update meeting")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "message": "Meeting updated successfully",
            "meeting": {
                "id": updated_meeting.id,
                "title": updated_meeting.title,
                "start_time": updated_meeting.start_time.isoformat(),
                "end_time": updated_meeting.end_time.isoformat(),
                "status": updated_meeting.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/meetings/{meeting_id}", response_model=Dict[str, Any])
async def delete_meeting(
    meeting_id: int,
    current_user = Depends(get_current_user)
):
    """Delete a meeting"""
    try:
        # Validate meeting exists and user has access
        meeting = schedule_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.organizer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this meeting")
        
        # Delete meeting
        deleted_meeting = schedule_service.delete_meeting(meeting_id, current_user.id)
        if not deleted_meeting:
            raise HTTPException(status_code=500, detail="Failed to delete meeting")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "message": "Meeting deleted successfully",
            "deleted_meeting": {
                "id": deleted_meeting.id,
                "title": deleted_meeting.title,
                "start_time": deleted_meeting.start_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reschedule/{meeting_id}", response_model=Dict[str, Any])
async def reschedule_meeting(
    meeting_id: int,
    new_start_time: str,
    current_user = Depends(get_current_user)
):
    """Reschedule a meeting to a new time"""
    try:
        # Validate meeting exists and user has access
        meeting = schedule_service.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.organizer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to reschedule this meeting")
        
        # Parse new start time
        try:
            start_time = datetime.fromisoformat(new_start_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use ISO format")
        
        # Reschedule meeting
        rescheduled_meeting = scheduling_agent._reschedule_meeting(meeting_id, new_start_time)
        if not rescheduled_meeting:
            raise HTTPException(status_code=500, detail="Failed to reschedule meeting")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "message": "Meeting rescheduled successfully",
            "new_start_time": new_start_time,
            "meeting": {
                "id": rescheduled_meeting.id,
                "title": rescheduled_meeting.title,
                "start_time": rescheduled_meeting.start_time.isoformat(),
                "end_time": rescheduled_meeting.end_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rescheduling meeting: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/meetings", response_model=List[Dict[str, Any]])
async def get_user_meetings(
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get current user's meetings"""
    try:
        meetings = schedule_service.get_user_meetings(current_user.id, status)
        
        meetings_data = []
        for meeting in meetings:
            meetings_data.append({
                "id": meeting.id,
                "title": meeting.title,
                "description": meeting.description,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat(),
                "duration_minutes": meeting.duration_minutes,
                "location": getattr(meeting, "location", None),
                "status": meeting.status,
                "organizer_id": meeting.organizer_id,
                "participants": meeting.participants,
                "meeting_type": meeting.meeting_type,
                "constraints": meeting.constraints
            })
        
        return meetings_data
        
    except Exception as e:
        logger.error(f"Error getting user meetings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/suggestions", response_model=Dict[str, Any])
async def get_meeting_suggestions(
    participant_ids: str, 
    duration_minutes: int = 60,
    start_date: str = None,
    end_date: str = None,
    current_user = Depends(get_current_user)
):
    """Get meeting time suggestions for participants"""
    try:
        # Parse participant IDs
        try:
            participant_id_list = [int(pid.strip()) for pid in participant_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid participant IDs format")
        
        # Validate participants exist
        for participant_id in participant_id_list:
            participant = user_service.get_user(participant_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found")
        
        # Parse dates
        if not start_date:
            start_date = datetime.now().isoformat()
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        try:
            start_datetime = datetime.fromisoformat(start_date)
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format")
        
        # Get suggestions
        suggestions = schedule_service.get_meeting_suggestions(
            participant_id_list, duration_minutes, start_datetime, end_datetime
        )
        
        return {
            "success": True,
            "participants": participant_id_list,
            "duration_minutes": duration_minutes,
            "suggestions": suggestions,
            "suggestion_count": len(suggestions),
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting meeting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/conversation", response_model=Dict[str, Any])
async def get_conversation_history(current_user = Depends(get_current_user)):
    """Get conversation history for current user"""
    try:
        # Get conversation history from agent
        history = scheduling_agent.conversation_history.get(current_user.id, [])
        
        return {
            "success": True,
            "user_id": current_user.id,
            "conversation_history": history,
            "message_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/availability", response_model=Dict[str, Any])
async def get_availability_suggestions(
    participants: str,  # Comma-separated user IDs
    duration_minutes: int = 60,
    start_date: str = None,
    end_date: str = None,
    current_user = Depends(get_current_user)
):
    """Get availability suggestions for meeting scheduling"""
    try:
        # Parse participant IDs
        try:
            participant_id_list = [int(pid.strip()) for pid in participants.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid participant IDs format")
        
        # Validate participants exist
        for participant_id in participant_id_list:
            participant = user_service.get_user(participant_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found")
        
        # Parse dates
        if not start_date:
            start_date = datetime.now().isoformat()
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        try:
            start_datetime = datetime.fromisoformat(start_date)
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format")
        
        # Get availability suggestions
        suggestions = await scheduling_agent.get_availability_suggestions(
            current_user.id, participant_id_list, duration_minutes, start_date, end_date
        )
        
        return {
            "success": True,
            "user_id": current_user.id,
            "participants": participant_id_list,
            "duration_minutes": duration_minutes,
            "suggestions": suggestions.get("suggestions", []),
            "total_slots": suggestions.get("total_slots", 0),
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting availability suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/test-meetings/{user_id}")
async def test_user_meetings(user_id: int):
    """Test endpoint to get meetings for a specific user (no auth required for debugging)"""
    try:
        logger.info(f"Testing meetings for user {user_id}")
        
        # Get meetings for the user
        meetings = schedule_service.get_user_meetings(user_id)
        
        # Convert to JSON-serializable format
        meetings_data = []
        for meeting in meetings:
            meetings_data.append({
                "id": meeting.id,
                "title": meeting.title,
                "description": meeting.description,
                "start_time": meeting.start_time.isoformat(),
                "end_time": meeting.end_time.isoformat(),
                "duration_minutes": meeting.duration_minutes,
                "organizer_id": meeting.organizer_id,
                "participants": meeting.participants,
                "status": meeting.status
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "meetings_count": len(meetings),
            "meetings": meetings_data
        }
        
    except Exception as e:
        logger.error(f"Error testing meetings for user {user_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/test-create-meeting")
async def test_create_meeting():
    """Test endpoint to create a meeting (no auth required for debugging)"""
    try:
        # Create a test meeting
        meeting_data = {
            "title": "Test Meeting",
            "description": "This is a test meeting",
            "duration_minutes": 60,
            "start_time": datetime.now() + timedelta(hours=1),
            "end_time": datetime.now() + timedelta(hours=2),
            "organizer_id": 1,  # Use user ID 1
            "participants": [1],  # User 1 is also a participant
            "status": "confirmed"
        }
        
        meeting = schedule_service.create_meeting(meeting_data)
        
        if meeting:
            return {
                "success": True,
                "message": "Test meeting created successfully",
                "meeting_id": meeting.id,
                "meeting": {
                    "id": meeting.id,
                    "title": meeting.title,
                    "start_time": meeting.start_time.isoformat(),
                    "organizer_id": meeting.organizer_id,
                    "participants": meeting.participants
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to create test meeting"
            }
        
    except Exception as e:
        logger.error(f"Error creating test meeting: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/confirm-action", response_model=SchedulingResponse)
async def confirm_action(
    request: ConfirmationRequest,
    current_user = Depends(get_current_user)
):
    """Handle confirmation of destructive actions and meeting creation"""
    try:
        if request.action == "confirm_delete":
            # Delete the specific meeting
            deleted_meeting = schedule_service.delete_meeting(request.meeting_id, current_user.id)
            if deleted_meeting:
                return SchedulingResponse(
                    success=True,
                    message=f"Successfully cancelled the meeting: {deleted_meeting.title}",
                    agent_reasoning="Meeting deleted after user confirmation"
                )
            else:
                raise HTTPException(status_code=404, detail="Meeting not found or already deleted")
        
        elif request.action == "confirm_delete_all":
            # Delete all user's meetings
            meetings = schedule_service.get_user_meetings(current_user.id)
            deleted_count = 0
            for meeting in meetings:
                if schedule_service.delete_meeting(meeting.id, current_user.id):
                    deleted_count += 1
            
            return SchedulingResponse(
                success=True,
                message=f"Successfully cancelled {deleted_count} meeting(s)",
                agent_reasoning=f"Bulk deletion completed after user confirmation"
            )
        
        elif request.action == "confirm_update":
            # Update the meeting
            if not request.updates:
                raise HTTPException(status_code=400, detail="No updates provided")
            
            meeting = schedule_service.get_meeting(request.meeting_id)
            if not meeting:
                raise HTTPException(status_code=404, detail="Meeting not found")
            
            if meeting.organizer_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to modify this meeting")
            
            # Process the updates
            updated_meeting = schedule_service.update_meeting(request.meeting_id, request.updates)
            if updated_meeting:
                return SchedulingResponse(
                    success=True,
                    message=f"Meeting '{updated_meeting.title}' has been updated successfully!",
                    meeting_proposal={
                        "id": updated_meeting.id,
                        "title": updated_meeting.title,
                        "start_time": updated_meeting.start_time.isoformat(),
                        "end_time": updated_meeting.end_time.isoformat(),
                        "duration_minutes": updated_meeting.duration_minutes
                    },
                    agent_reasoning="Meeting updated after user confirmation"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to update meeting")
        
        elif request.action == "confirm_create":
            # Create the meeting from the proposal
            if not request.meeting_proposal:
                raise HTTPException(status_code=400, detail="No meeting proposal provided")
            meeting_data = request.meeting_proposal.copy()
            meeting_data["organizer_id"] = current_user.id
            # Parse start_time and end_time if needed
            if isinstance(meeting_data.get("start_time"), str):
                meeting_data["start_time"] = datetime.fromisoformat(meeting_data["start_time"])
            if "duration_minutes" in meeting_data and "start_time" in meeting_data:
                meeting_data["end_time"] = meeting_data["start_time"] + timedelta(minutes=meeting_data["duration_minutes"])
            meeting = schedule_service.create_meeting(meeting_data)
            if meeting:
                return SchedulingResponse(
                    success=True,
                    message=f"Meeting '{meeting.title}' has been scheduled successfully!",
                    meeting_proposal={
                        "id": meeting.id,
                        "title": meeting.title,
                        "start_time": meeting.start_time.isoformat(),
                        "end_time": meeting.end_time.isoformat(),
                        "duration_minutes": meeting.duration_minutes,
                        "participants": meeting.participants,
                        "location": getattr(meeting, "location", "TBD"),
                        "description": getattr(meeting, "description", "")
                    },
                    agent_reasoning="Meeting created after user confirmation"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to create meeting")
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming action: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 