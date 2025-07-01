#!/usr/bin/env python3
"""
Script to create test meetings for testing natural language understanding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.schedule_service import ScheduleService
from app.models.schedule import MeetingCreate
from datetime import datetime, timedelta
import pytz

def create_test_meetings():
    """Create test meetings for testing"""
    print("🗓️ Creating Test Meetings")
    print("=" * 40)
    
    schedule_service = ScheduleService()
    user_id = 1
    
    # Get current time in UTC
    now = datetime.now(pytz.UTC)
    
    # Create test meetings
    test_meetings = [
        {
            "title": "Project Update with Val",
            "description": "Discussion on project updates.",
            "start_time": now.replace(hour=13, minute=0, second=0, microsecond=0),  # 1 PM
            "duration_minutes": 60,
            "participants": [1, 2],
            "location": "Conference Room A"
        },
        {
            "title": "Project Update with Val", 
            "description": "Discussion on project updates.",
            "start_time": now.replace(hour=10, minute=0, second=0, microsecond=0),  # 10 AM
            "duration_minutes": 60,
            "participants": [1, 2],
            "location": "Conference Room B"
        },
        {
            "title": "Team Standup",
            "description": "Daily team standup meeting.",
            "start_time": now.replace(hour=9, minute=0, second=0, microsecond=0),  # 9 AM
            "duration_minutes": 30,
            "participants": [1, 2, 3],
            "location": "Virtual"
        },
        {
            "title": "Client Review",
            "description": "Review meeting with client.",
            "start_time": now.replace(hour=15, minute=0, second=0, microsecond=0),  # 3 PM
            "duration_minutes": 90,
            "participants": [1, 4],
            "location": "Conference Room C"
        }
    ]
    
    created_meetings = []
    
    for i, meeting_data in enumerate(test_meetings, 1):
        print(f"Creating meeting {i}: {meeting_data['title']}")
        print(f"  Time: {meeting_data['start_time'].strftime('%I:%M %p')}")
        print(f"  Duration: {meeting_data['duration_minutes']} minutes")
        
        try:
            # Calculate end time
            end_time = meeting_data["start_time"] + timedelta(minutes=meeting_data["duration_minutes"])
            
            # Create meeting using the service
            meeting_dict = {
                "title": meeting_data["title"],
                "description": meeting_data["description"],
                "start_time": meeting_data["start_time"],
                "end_time": end_time,
                "duration_minutes": meeting_data["duration_minutes"],
                "organizer_id": user_id,
                "participants": meeting_data["participants"],
                "meeting_type": "general",
                "status": "confirmed"
            }
            
            meeting = schedule_service.create_meeting(meeting_dict)
            
            if meeting:
                created_meetings.append(meeting)
                print(f"  ✅ Created meeting ID: {meeting.id}")
            else:
                print(f"  ❌ Failed to create meeting")
                
        except Exception as e:
            print(f"  ❌ Error creating meeting: {str(e)}")
        
        print()
    
    print(f"📊 Summary: Created {len(created_meetings)} test meetings")
    
    # Show all meetings
    print("\n📋 All Meetings in Database:")
    print("-" * 30)
    
    try:
        all_meetings = schedule_service.get_user_meetings(user_id)
        
        if all_meetings:
            for meeting in all_meetings:
                print(f"ID: {meeting.id}")
                print(f"Title: {meeting.title}")
                print(f"Time: {meeting.start_time.strftime('%I:%M %p')}")
                print(f"Date: {meeting.start_time.strftime('%Y-%m-%d')}")
                print(f"Duration: {meeting.duration_minutes} minutes")
                print(f"Location: {getattr(meeting, 'location', 'N/A')}")
                print("-" * 20)
        else:
            print("No meetings found in database")
            
    except Exception as e:
        print(f"Error getting meetings: {str(e)}")
    
    return created_meetings

if __name__ == "__main__":
    print("🚀 Creating Test Meetings for Natural Language Testing")
    print("=" * 60)
    
    meetings = create_test_meetings()
    
    print(f"\n✅ Test meetings created successfully!")
    print(f"📝 You can now test natural language commands like:")
    print(f"   - 'cancel the 1 pm meeting'")
    print(f"   - 'delete the 10am meeting'")
    print(f"   - 'show me my meetings'")
    print(f"   - 'cancel the project update meeting'") 