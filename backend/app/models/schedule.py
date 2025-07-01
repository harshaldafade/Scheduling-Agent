from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=60)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    organizer_id = Column(Integer, ForeignKey("users.id"))
    participants = Column(JSON, default=[])  # List of user IDs
    status = Column(String, default="proposed")  # proposed, confirmed, cancelled
    meeting_type = Column(String, default="general")  # interview, team_meeting, etc.
    constraints = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organizer = relationship("User", back_populates="organized_meetings")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True))
    available_slots = Column(JSON, default=[])  # List of time slots
    busy_slots = Column(JSON, default=[])  # List of busy time slots
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MeetingRequest(BaseModel):
    """Request model for AI scheduling agent"""
    title: str
    description: Optional[str] = None
    duration: int = 60
    participants: List[str] = []  # List of participant names/emails
    preferred_date: str
    preferred_time: str
    location: Optional[str] = None
    organizer_id: int

class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int = 60
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    organizer_id: int
    participants: List[int] = []
    meeting_type: str = "general"
    constraints: Optional[Dict[str, Any]] = {}

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: Optional[List[int]] = None
    status: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None

class MeetingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration_minutes: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    organizer_id: int
    participants: List[int]
    status: str
    meeting_type: str
    constraints: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ScheduleCreate(BaseModel):
    user_id: int
    date: datetime
    available_slots: List[Dict[str, Any]] = []
    busy_slots: List[Dict[str, Any]] = []

class ScheduleResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    available_slots: List[Dict[str, Any]]
    busy_slots: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True 