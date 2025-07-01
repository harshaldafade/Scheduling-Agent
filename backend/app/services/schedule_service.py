from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from app.models.schedule import Meeting, Schedule, MeetingCreate, MeetingUpdate, ScheduleCreate
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class ScheduleService:
    """Service class for schedule and meeting-related operations"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Optional[Meeting]:
        """Create a new meeting"""
        try:
            meeting = Meeting(
                title=meeting_data["title"],
                description=meeting_data.get("description"),
                duration_minutes=meeting_data["duration_minutes"],
                start_time=meeting_data["start_time"],
                end_time=meeting_data["end_time"],
                organizer_id=meeting_data["organizer_id"],
                participants=meeting_data["participants"],
                meeting_type=meeting_data.get("meeting_type", "general"),
                constraints=meeting_data.get("constraints", {}),
                status=meeting_data.get("status", "proposed")
            )
            
            self.db.add(meeting)
            self.db.commit()
            self.db.refresh(meeting)
            
            logger.info(f"Created meeting {meeting.id}: {meeting.title}")
            return meeting
        except Exception as e:
            logger.error(f"Error creating meeting: {str(e)}")
            self.db.rollback()
            return None
    
    def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        """Get meeting by ID"""
        try:
            return self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        except Exception as e:
            logger.error(f"Error getting meeting {meeting_id}: {str(e)}")
            return None
    
    def get_user_meetings(self, user_id: int, status: Optional[str] = None) -> List[Meeting]:
        """Get meetings for a user (as organizer or participant)"""
        try:
            logger.info(f"Getting meetings for user {user_id}")
            
            # Get all meetings
            query = self.db.query(Meeting)
            
            # Filter by status if provided
            if status:
                query = query.filter(Meeting.status == status)
            
            # Get all meetings and filter in Python for better JSON handling
            all_meetings = query.all()
            logger.info(f"Found {len(all_meetings)} total meetings in database")
            
            # Filter meetings where user is organizer or participant
            user_meetings = []
            for meeting in all_meetings:
                logger.info(f"Checking meeting {meeting.id}: organizer_id={meeting.organizer_id}, participants={meeting.participants}")
                # Check if user is organizer
                if meeting.organizer_id == user_id:
                    logger.info(f"User {user_id} is organizer of meeting {meeting.id}")
                    user_meetings.append(meeting)
                # Check if user is participant (handle JSON array)
                elif meeting.participants and user_id in meeting.participants:
                    logger.info(f"User {user_id} is participant of meeting {meeting.id}")
                    user_meetings.append(meeting)
            
            logger.info(f"Found {len(user_meetings)} meetings for user {user_id}")
            
            # Sort by start time (most recent first)
            user_meetings.sort(key=lambda x: x.start_time, reverse=True)
            
            return user_meetings
        except Exception as e:
            logger.error(f"Error getting meetings for user {user_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def update_meeting(self, meeting_id: int, meeting_data: MeetingUpdate) -> Optional[Meeting]:
        """Update meeting information"""
        try:
            meeting = self.get_meeting(meeting_id)
            if not meeting:
                logger.warning(f"Meeting {meeting_id} not found for update")
                return None
            
            # Update fields if provided
            if meeting_data.title is not None:
                meeting.title = meeting_data.title
            if meeting_data.description is not None:
                meeting.description = meeting_data.description
            if meeting_data.duration_minutes is not None:
                meeting.duration_minutes = meeting_data.duration_minutes
            if meeting_data.start_time is not None:
                meeting.start_time = meeting_data.start_time
            if meeting_data.end_time is not None:
                meeting.end_time = meeting_data.end_time
            if meeting_data.participants is not None:
                meeting.participants = meeting_data.participants
            if meeting_data.status is not None:
                meeting.status = meeting_data.status
            if meeting_data.constraints is not None:
                meeting.constraints = meeting_data.constraints
            
            self.db.commit()
            self.db.refresh(meeting)
            
            logger.info(f"Updated meeting {meeting_id}")
            return meeting
        except Exception as e:
            logger.error(f"Error updating meeting {meeting_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def delete_meeting(self, meeting_id: int, user_id: Optional[int] = None) -> Optional[Meeting]:
        """Delete a meeting. Optionally verify user has permission to delete it."""
        try:
            meeting = self.get_meeting(meeting_id)
            if not meeting:
                logger.warning(f"Meeting {meeting_id} not found for deletion")
                return None
            
            # If user_id is provided, verify the user has permission to delete this meeting
            if user_id is not None:
                if meeting.organizer_id != user_id:
                    logger.warning(f"User {user_id} does not have permission to delete meeting {meeting_id}")
                    return None
            
            # Store meeting info before deletion
            deleted_meeting = Meeting(
                id=meeting.id,
                title=meeting.title,
                description=meeting.description,
                duration_minutes=meeting.duration_minutes,
                start_time=meeting.start_time,
                end_time=meeting.end_time,
                organizer_id=meeting.organizer_id,
                participants=meeting.participants,
                status=meeting.status,
                meeting_type=meeting.meeting_type,
                constraints=meeting.constraints,
                created_at=meeting.created_at,
                updated_at=meeting.updated_at
            )
            
            self.db.delete(meeting)
            self.db.commit()
            
            logger.info(f"Deleted meeting {meeting_id}")
            return deleted_meeting
        except Exception as e:
            logger.error(f"Error deleting meeting {meeting_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def get_user_schedule(self, user_id: int, target_date: datetime) -> Optional[Schedule]:
        """Get user's schedule for a specific date"""
        try:
            # Convert to date for comparison
            target_date_only = target_date.date()
            
            schedule = self.db.query(Schedule).filter(
                Schedule.user_id == user_id,
                Schedule.date >= target_date_only,
                Schedule.date < target_date_only + timedelta(days=1)
            ).first()
            
            return schedule
        except Exception as e:
            logger.error(f"Error getting schedule for user {user_id} on {target_date}: {str(e)}")
            return None
    
    def create_user_schedule(self, schedule_data: ScheduleCreate) -> Optional[Schedule]:
        """Create a user's schedule for a specific date"""
        try:
            schedule = Schedule(
                user_id=schedule_data.user_id,
                date=schedule_data.date,
                available_slots=schedule_data.available_slots,
                busy_slots=schedule_data.busy_slots
            )
            
            self.db.add(schedule)
            self.db.commit()
            self.db.refresh(schedule)
            
            logger.info(f"Created schedule for user {schedule_data.user_id} on {schedule_data.date}")
            return schedule
        except Exception as e:
            logger.error(f"Error creating schedule: {str(e)}")
            self.db.rollback()
            return None
    
    def update_user_schedule(self, user_id: int, target_date: datetime, 
                           available_slots: List[Dict], busy_slots: List[Dict]) -> Optional[Schedule]:
        """Update user's schedule for a specific date"""
        try:
            schedule = self.get_user_schedule(user_id, target_date)
            
            if schedule:
                # Update existing schedule
                schedule.available_slots = available_slots
                schedule.busy_slots = busy_slots
            else:
                # Create new schedule
                schedule_data = ScheduleCreate(
                    user_id=user_id,
                    date=target_date,
                    available_slots=available_slots,
                    busy_slots=busy_slots
                )
                schedule = self.create_user_schedule(schedule_data)
            
            if schedule:
                self.db.commit()
                self.db.refresh(schedule)
                logger.info(f"Updated schedule for user {user_id} on {target_date}")
            
            return schedule
        except Exception as e:
            logger.error(f"Error updating schedule for user {user_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def check_meeting_conflicts(self, user_id: int, start_time: datetime, end_time: datetime) -> List[Meeting]:
        """Check for meeting conflicts for a user in a given time range"""
        try:
            conflicts = self.db.query(Meeting).filter(
                (Meeting.organizer_id == user_id) | (Meeting.participants.contains([user_id])),
                Meeting.status.in_(["proposed", "confirmed"]),
                Meeting.start_time < end_time,
                Meeting.end_time > start_time
            ).all()
            
            return conflicts
        except Exception as e:
            logger.error(f"Error checking conflicts for user {user_id}: {str(e)}")
            return []
    
    def get_meeting_suggestions(self, participant_ids: List[int], duration_minutes: int, 
                              start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get meeting time suggestions for multiple participants"""
        try:
            suggestions = []
            
            # This is a simplified implementation
            # In a real system, you'd implement sophisticated scheduling algorithms
            
            current_date = start_date
            while current_date <= end_date:
                # Generate time slots for the day
                for hour in range(9, 17):  # 9 AM to 5 PM
                    slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Check if all participants are available
                    all_available = True
                    for user_id in participant_ids:
                        conflicts = self.check_meeting_conflicts(user_id, slot_start, slot_end)
                        if conflicts:
                            all_available = False
                            break
                    
                    if all_available:
                        suggestions.append({
                            "start_time": slot_start.isoformat(),
                            "end_time": slot_end.isoformat(),
                            "date": current_date.date().isoformat(),
                            "participant_count": len(participant_ids)
                        })
                
                current_date += timedelta(days=1)
            
            return suggestions[:10]  # Return top 10 suggestions
        except Exception as e:
            logger.error(f"Error getting meeting suggestions: {str(e)}")
            return []
    
    def find_optimal_meeting_time(self, participant_ids: List[int], duration_minutes: int, 
                                start_date: datetime, end_date: datetime, 
                                preferences: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find the optimal meeting time based on participant preferences and availability"""
        try:
            suggestions = self.get_meeting_suggestions(participant_ids, duration_minutes, start_date, end_date)
            
            if not suggestions:
                return None
            
            # Score each suggestion based on preferences
            scored_suggestions = []
            for suggestion in suggestions:
                score = 0
                slot_start = datetime.fromisoformat(suggestion["start_time"])
                
                # Prefer morning meetings (9-11 AM)
                if 9 <= slot_start.hour <= 11:
                    score += 3
                # Prefer afternoon meetings (2-4 PM)
                elif 14 <= slot_start.hour <= 16:
                    score += 2
                # Avoid lunch time (12-1 PM)
                elif 12 <= slot_start.hour <= 13:
                    score -= 1
                
                # Prefer weekdays over weekends
                if slot_start.weekday() < 5:  # Monday to Friday
                    score += 2
                
                # Consider participant count (more participants = higher priority)
                score += suggestion["participant_count"] * 0.5
                
                scored_suggestions.append((score, suggestion))
            
            # Sort by score (highest first)
            scored_suggestions.sort(key=lambda x: x[0], reverse=True)
            
            return scored_suggestions[0][1] if scored_suggestions else None
            
        except Exception as e:
            logger.error(f"Error finding optimal meeting time: {str(e)}")
            return None
    
    def auto_reschedule_conflicting_meetings(self, new_meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Automatically reschedule conflicting meetings to accommodate a new meeting"""
        try:
            start_time = new_meeting_data["start_time"]
            end_time = new_meeting_data["end_time"]
            participants = new_meeting_data["participants"]
            
            rescheduled_meetings = []
            
            for participant_id in participants:
                conflicts = self.check_meeting_conflicts(participant_id, start_time, end_time)
                
                for conflict in conflicts:
                    # Try to find a new time for the conflicting meeting
                    new_suggestions = self.get_meeting_suggestions(
                        conflict.participants, 
                        conflict.duration_minutes,
                        start_time + timedelta(days=1),  # Start looking from tomorrow
                        start_time + timedelta(days=7)   # Look up to 7 days ahead
                    )
                    
                    if new_suggestions:
                        # Reschedule the conflicting meeting
                        new_time = new_suggestions[0]
                        meeting_update = MeetingUpdate(
                            start_time=datetime.fromisoformat(new_time["start_time"]),
                            end_time=datetime.fromisoformat(new_time["end_time"])
                        )
                        
                        updated_meeting = self.update_meeting(conflict.id, meeting_update)
                        if updated_meeting:
                            rescheduled_meetings.append({
                                "meeting_id": conflict.id,
                                "title": conflict.title,
                                "old_start_time": conflict.start_time.isoformat(),
                                "new_start_time": new_time["start_time"],
                                "reason": "Auto-rescheduled to accommodate new meeting"
                            })
            
            return rescheduled_meetings
            
        except Exception as e:
            logger.error(f"Error auto-rescheduling conflicting meetings: {str(e)}")
            return []
    
    def get_meeting_analytics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics about user's meetings in a date range"""
        try:
            meetings = self.db.query(Meeting).filter(
                (Meeting.organizer_id == user_id) | (Meeting.participants.contains([user_id])),
                Meeting.start_time >= start_date,
                Meeting.start_time <= end_date
            ).all()
            
            total_meetings = len(meetings)
            total_duration = sum(meeting.duration_minutes for meeting in meetings)
            
            # Group by day of week
            day_stats = {}
            for meeting in meetings:
                day = meeting.start_time.strftime("%A")
                if day not in day_stats:
                    day_stats[day] = {"count": 0, "duration": 0}
                day_stats[day]["count"] += 1
                day_stats[day]["duration"] += meeting.duration_minutes
            
            # Group by hour
            hour_stats = {}
            for meeting in meetings:
                hour = meeting.start_time.hour
                if hour not in hour_stats:
                    hour_stats[hour] = {"count": 0, "duration": 0}
                hour_stats[hour]["count"] += 1
                hour_stats[hour]["duration"] += meeting.duration_minutes
            
            return {
                "total_meetings": total_meetings,
                "total_duration_minutes": total_duration,
                "average_duration_minutes": total_duration / total_meetings if total_meetings > 0 else 0,
                "day_stats": day_stats,
                "hour_stats": hour_stats,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting meeting analytics: {str(e)}")
            return {}
    
    def optimize_schedule(self, user_id: int, target_date: datetime) -> List[Dict[str, Any]]:
        """Optimize user's schedule for a specific date by suggesting improvements"""
        try:
            # Get all meetings for the user on the target date
            start_of_day = datetime.combine(target_date.date(), datetime.min.time())
            end_of_day = start_of_day + timedelta(days=1)
            
            meetings = self.db.query(Meeting).filter(
                (Meeting.organizer_id == user_id) | (Meeting.participants.contains([user_id])),
                Meeting.start_time >= start_of_day,
                Meeting.start_time < end_of_day,
                Meeting.status.in_(["confirmed", "proposed"])
            ).order_by(Meeting.start_time).all()
            
            optimizations = []
            
            # Check for gaps that could be filled
            for i in range(len(meetings) - 1):
                current_meeting = meetings[i]
                next_meeting = meetings[i + 1]
                
                gap_start = current_meeting.end_time
                gap_end = next_meeting.start_time
                gap_duration = (gap_end - gap_start).total_seconds() / 60
                
                if gap_duration >= 30:  # Gap of 30 minutes or more
                    optimizations.append({
                        "type": "gap_detected",
                        "start_time": gap_start.isoformat(),
                        "end_time": gap_end.isoformat(),
                        "duration_minutes": gap_duration,
                        "suggestion": f"Consider scheduling a {int(gap_duration)}-minute task or meeting in this gap"
                    })
            
            # Check for back-to-back meetings
            for i in range(len(meetings) - 1):
                current_meeting = meetings[i]
                next_meeting = meetings[i + 1]
                
                if (next_meeting.start_time - current_meeting.end_time).total_seconds() <= 300:  # 5 minutes or less
                    optimizations.append({
                        "type": "back_to_back",
                        "meeting1": current_meeting.title,
                        "meeting2": next_meeting.title,
                        "gap_minutes": (next_meeting.start_time - current_meeting.end_time).total_seconds() / 60,
                        "suggestion": "Consider adding a break between these meetings"
                    })
            
            # Check for long meetings that could be split
            for meeting in meetings:
                if meeting.duration_minutes > 120:  # 2 hours or more
                    optimizations.append({
                        "type": "long_meeting",
                        "meeting_title": meeting.title,
                        "duration_minutes": meeting.duration_minutes,
                        "suggestion": "Consider breaking this long meeting into shorter sessions"
                    })
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {str(e)}")
            return []
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db'):
            self.db.close() 