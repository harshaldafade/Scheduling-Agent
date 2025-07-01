#!/usr/bin/env python3
"""
Example usage of the enhanced scheduling agent with date context
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.scheduling_agent import SchedulingAgent

async def demonstrate_natural_language_scheduling():
    """Demonstrate natural language scheduling with date context"""
    print("🎯 Enhanced Scheduling Agent - Natural Language Examples")
    print("=" * 60)
    
    # Initialize the scheduling agent
    agent = SchedulingAgent()
    
    # Example user interactions
    examples = [
        {
            "user_input": "Schedule a team meeting tomorrow at 2pm",
            "description": "Basic scheduling with relative date and time"
        },
        {
            "user_input": "Book a call with John next Monday at 10am",
            "description": "Scheduling with specific day reference"
        },
        {
            "user_input": "Set up a project review this Friday",
            "description": "Scheduling with day reference, no specific time"
        },
        {
            "user_input": "Create a meeting in 3 days at 1:30pm",
            "description": "Scheduling with relative days"
        },
        {
            "user_input": "Schedule a weekly standup next Tuesday",
            "description": "Recurring meeting concept"
        },
        {
            "user_input": "Show me my meetings",
            "description": "Viewing existing meetings"
        },
        {
            "user_input": "Reschedule my 2pm meeting to tomorrow",
            "description": "Rescheduling existing meeting"
        },
        {
            "user_input": "Cancel the team meeting",
            "description": "Canceling a meeting"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {example['description']}")
        print("-" * 50)
        print(f"User: {example['user_input']}")
        
        try:
            # Simulate processing (in real usage, this would be user_id=1)
            response = await agent.process_message(user_id=1, message=example['user_input'])
            
            if response["success"]:
                print(f"Agent: {response['message']}")
                if response.get('meeting_proposal'):
                    print(f"📅 Meeting Details: {response['meeting_proposal']}")
                if response.get('meetings'):
                    print(f"📋 Meetings Found: {len(response['meetings'])}")
                if response.get('alternative_slots'):
                    print(f"🕐 Alternative Times: {len(response['alternative_slots'])} suggestions")
            else:
                print(f"❌ Error: {response['message']}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Natural Language Scheduling Examples Completed!")
    print("\n💡 Key Benefits:")
    print("• No need to remember specific date formats")
    print("• Intuitive natural language interaction")
    print("• Automatic date and time parsing")
    print("• Context-aware scheduling")
    print("• Intelligent conflict resolution")
    print("• Business hours consideration")

def show_date_parsing_examples():
    """Show examples of date parsing capabilities"""
    print("\n🔍 Date Parsing Examples")
    print("=" * 40)
    
    agent = SchedulingAgent()
    
    date_examples = [
        "today at 2pm",
        "tomorrow morning",
        "next Monday at 3pm",
        "this Friday",
        "in 5 days at 1:30pm",
        "next week Tuesday",
        "2pm today",
        "9am tomorrow"
    ]
    
    for example in date_examples:
        try:
            parsed = agent._parse_relative_datetime(example)
            print(f"'{example}' → {parsed.strftime('%Y-%m-%d %I:%M %p')}")
        except Exception as e:
            print(f"'{example}' → ERROR: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Scheduling Agent Examples")
    
    # Show date parsing examples
    show_date_parsing_examples()
    
    # Run natural language examples
    asyncio.run(demonstrate_natural_language_scheduling())
    
    print("\n📚 For more information, see DATE_HANDLING_GUIDE.md") 