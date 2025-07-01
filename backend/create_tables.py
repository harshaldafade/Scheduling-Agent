#!/usr/bin/env python3
"""
Database initialization script for AI Scheduling Agent
"""

import asyncio
from sqlalchemy import create_engine, text
from app.core.database import Base
from app.models.user import User
from app.models.schedule import Meeting, Schedule
from app.core.config import settings

async def create_tables():
    """Create all database tables"""
    engine = create_engine(settings.database_url)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

async def create_sample_data():
    """Create sample data for testing"""
    from app.services.user_service import UserService
    from app.services.schedule_service import ScheduleService
    from app.models.user import UserCreate
    
    user_service = UserService()
    schedule_service = ScheduleService()
    
    # Create sample users
    sample_users = [
        UserCreate(
            email="john@example.com",
            name="John Doe",
            timezone="America/New_York",
            preferences={
                "preferred_time_slots": ["9:00 AM", "2:00 PM", "4:00 PM"],
                "preferred_duration": "standard",
                "preferred_meeting_types": ["one-on-one", "team-meeting"]
            }
        ),
        UserCreate(
            email="jane@example.com",
            name="Jane Smith",
            timezone="America/Los_Angeles",
            preferences={
                "preferred_time_slots": ["10:00 AM", "3:00 PM"],
                "preferred_duration": "long",
                "preferred_meeting_types": ["client-meeting", "presentation"]
            }
        ),
        UserCreate(
            email="bob@example.com",
            name="Bob Wilson",
            timezone="Europe/London",
            preferences={
                "preferred_time_slots": ["11:00 AM", "2:00 PM", "5:00 PM"],
                "preferred_duration": "short",
                "preferred_meeting_types": ["standup", "planning"]
            }
        ),
        UserCreate(
            email="val@gmail.com",
            name="Val",
            timezone="America/New_York",
            preferences={
                "preferred_time_slots": ["1:00 PM", "3:00 PM", "4:00 PM"],
                "preferred_duration": "standard",
                "preferred_meeting_types": ["project-meeting", "discussion"]
            }
        ),
        UserCreate(
            email="harshal.dafade@gmail.com",
            name="Harshal Dafade",
            timezone="America/New_York",
            preferences={
                "preferred_time_slots": ["9:00 AM", "1:00 PM", "3:00 PM"],
                "preferred_duration": "standard",
                "preferred_meeting_types": ["project-meeting", "discussion"]
            }
        )
    ]
    
    try:
        for user_data in sample_users:
            user = user_service.create_user(user_data)
            if user:
                print(f"✅ Created user: {user.name}")
            else:
                print(f"❌ Failed to create user: {user_data.name}")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Initializing AI Scheduling Agent Database...")
    
    # Create tables
    asyncio.run(create_tables())
    
    # Create sample data
    print("\n📊 Creating sample data...")
    asyncio.run(create_sample_data())
    
    print("\n🎉 Database initialization complete!")
    print("You can now use the AI Scheduling Agent with real data.") 