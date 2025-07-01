from app.agents.base_agent import BaseAgent
from app.models.schedule import MeetingRequest, MeetingResponse
from app.services.schedule_service import ScheduleService
from app.services.user_service import UserService
from app.services.preference_service import PreferenceService
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import json
import re
import logging
from dateutil import parser, relativedelta
import pytz
from langchain.schema import SystemMessage, HumanMessage
import ast

logger = logging.getLogger(__name__)

class SchedulingAgent(BaseAgent):
    """Conversational scheduling agent that acts like a helpful assistant"""
    
    def __init__(self):
        super().__init__("Scheduling Assistant")
        self.schedule_service = ScheduleService()
        self.user_service = UserService()
        self.preference_service = PreferenceService()
        self.conversation_history = {}  # Store conversation context per user
        self.pending_actions = {}  # Store pending actions that need clarification
        self.timezone = pytz.timezone('UTC')
    
    def get_system_prompt(self) -> str:
        return """You are a friendly and helpful scheduling assistant. You help users manage their meetings and calendar in a natural, conversational way.

YOUR PERSONALITY:
- Be warm, helpful, and conversational
- Ask clarifying questions when you need more information
- Confirm details before making changes
- Be proactive in suggesting solutions
- Use natural language, not technical jargon

WHAT YOU CAN DO:
1. View and show meetings
2. Schedule new meetings
3. Update existing meetings
4. Cancel/delete meetings
5. Suggest available time slots
6. Ask for missing details when needed

CONVERSATION FLOW:
- When a user wants to schedule a meeting, ask for missing details (time, participants, duration, etc.)
- When they want to update/cancel a meeting, confirm which meeting they mean
- Always show them their current meetings when relevant
- Suggest alternatives when there are conflicts

EXAMPLES OF GOOD RESPONSES:
- "I'd be happy to help you schedule a meeting! What time would you like to meet?"
- "I see you have a team meeting at 2pm. Would you like to reschedule that one?"
- "I found a conflict with your existing meeting. Would you prefer 3pm instead?"
- "Let me show you your meetings for today..."

Remember: You're a helpful assistant, not a command parser. Have natural conversations and guide users through the scheduling process."""

    async def process_message(self, user_id: int, message: str) -> Dict[str, Any]:
        """Process user message in a conversational way with LLM enhancement"""
        try:
            # Add to conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now()
            })
            
            # Check if there's a pending action that needs clarification
            if user_id in self.pending_actions:
                response = await self._handle_pending_action(user_id, message)
            else:
                # Analyze the message and determine intent
                intent = self._analyze_intent(message)
                response = await self._handle_intent(user_id, message, intent)
            
            # Enhance response with LLM if it's a simple response
            if response.get("success") and not response.get("needs_llm_enhancement", False):
                enhanced_response = await self._enhance_response_with_llm(user_id, message, response)
                if enhanced_response:
                    response = enhanced_response
            
            # Add response to conversation history
            self.conversation_history[user_id].append({
                "role": "assistant", 
                "content": response["message"],
                "timestamp": datetime.now()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in conversational agent: {str(e)}")
            return {
                "success": False, 
                "message": "I'm having trouble right now. Could you try again in a moment?"
            }

    def _analyze_intent(self, message: str) -> str:
        """Analyze user message to determine intent"""
        message_lower = message.lower()
        
        # View meetings
        if any(word in message_lower for word in ["show", "view", "see", "what", "meetings", "schedule", "calendar"]):
            if any(word in message_lower for word in ["my", "have", "scheduled"]):
                return "view_meetings"
        
        # Create meeting
        if any(word in message_lower for word in ["schedule", "create", "set up", "book", "arrange", "meeting"]):
            if any(word in message_lower for word in ["new", "a", "with"]):
                return "create_meeting"
        
        # Update meeting
        if any(word in message_lower for word in ["change", "update", "modify", "move", "reschedule", "edit"]):
            return "update_meeting"
        
        # Delete meeting
        if any(word in message_lower for word in ["cancel", "delete", "remove", "clear"]):
            return "delete_meeting"
        
        # Delete all meetings
        if any(word in message_lower for word in ["all", "everything", "clear all"]):
            if any(word in message_lower for word in ["cancel", "delete", "remove"]):
                return "delete_all_meetings"
        
        return "conversation"

    async def _handle_intent(self, user_id: int, message: str, intent: str) -> Dict[str, Any]:
        """Handle different user intents conversationally"""
        
        if intent == "view_meetings":
            return await self._handle_view_meetings_conversational(user_id)
        
        elif intent == "create_meeting":
            return await self._handle_create_meeting_conversational(user_id, message)
        
        elif intent == "update_meeting":
            return await self._handle_update_meeting_conversational(user_id, message)
        
        elif intent == "delete_meeting":
            return await self._handle_delete_meeting_conversational(user_id, message)
        
        elif intent == "delete_all_meetings":
            return await self._handle_delete_all_meetings_conversational(user_id)
        
        else:
            # General conversation - be helpful and ask what they need
            return await self._handle_general_conversation(user_id, message)

    async def _handle_view_meetings_conversational(self, user_id: int) -> Dict[str, Any]:
        """Handle viewing meetings in a conversational way"""
        try:
            meetings = self.schedule_service.get_user_meetings(user_id)
            
            if not meetings:
                return {
                    "success": True,
                    "message": "You don't have any meetings scheduled right now. Would you like me to help you schedule one?"
                }
            
            # Format meetings nicely
            if len(meetings) == 1:
                meeting = meetings[0]
                message = f"You have one meeting scheduled: **{meeting.title}** on {meeting.start_time.strftime('%A, %B %d')} at {meeting.start_time.strftime('%I:%M %p')} ({meeting.duration_minutes} minutes)."
            else:
                message = f"You have {len(meetings)} meetings scheduled:\n\n"
                for i, meeting in enumerate(meetings, 1):
                    message += f"{i}. **{meeting.title}** - {meeting.start_time.strftime('%A, %B %d at %I:%M %p')} ({meeting.duration_minutes} min)\n"
            
            message += "\nIs there anything you'd like to do with these meetings?"
            
            return {"success": True, "message": message}
            
        except Exception as e:
            logger.error(f"Error viewing meetings: {str(e)}")
            return {"success": False, "message": "I'm having trouble accessing your meetings right now. Could you try again?"}

    async def _handle_create_meeting_conversational(self, user_id: int, message: str) -> Dict[str, Any]:
        """Handle meeting creation conversationally with structured LLM output, conflict checking, and confirmation flow"""
        try:
            context = self._build_conversation_context(user_id, message)
            prompt = f"""You are a helpful scheduling assistant. The user wants to schedule a meeting.

Context:
{context}

INSTRUCTIONS:
- Carefully review the user's current meetings (see the JSON list above).
- If the requested meeting time conflicts with any existing meeting, suggest an alternative time or ask the user how to resolve the conflict.
- Respond ONLY with a JSON object describing the action to take. Example:
{{
  \"action\": \"create_meeting\",
  \"title\": \"Team Sync\",
  \"start_time\": \"2024-06-10T14:00:00Z\",
  \"duration_minutes\": 60,
  \"participants\": [\"alice@example.com\", \"bob@example.com\"]
}}
If there is a conflict, set \"action\": \"suggest_alternative\" and propose a new time in the JSON.
If any information is missing, include only what you know and set missing fields to null or empty. Do NOT add extra text.

User message: {message}
"""
            llm_response = await self.llm.ainvoke(prompt)
            llm_content = self._get_llm_content(llm_response).strip()
            action_data = self._extract_json_from_llm_output(llm_content)
            if not action_data or action_data.get("action") not in ["create_meeting", "suggest_alternative"]:
                meeting_info = self._extract_meeting_info(message)
            else:
                meeting_info = {
                    "title": action_data.get("title"),
                    "start_time": action_data.get("start_time"),
                    "duration_minutes": action_data.get("duration_minutes"),
                    "participants": action_data.get("participants"),
                    "description": action_data.get("description", ""),
                    "location": action_data.get("location", "TBD")
                }
                if action_data.get("action") == "suggest_alternative":
                    alt_time = action_data.get("start_time")
                    alt_msg = f"The requested time conflicts with an existing meeting. Would you like to schedule at {alt_time} instead, or suggest another time?"
                    self.pending_actions[user_id] = {
                        "action": "create_meeting",
                        "partial_info": meeting_info,
                        "missing_fields": [],
                        "suggested_alternative": alt_time
                    }
                    return {"success": True, "message": alt_msg}
            # Backend validation for required fields
            missing_info = []
            if not meeting_info.get("title"):
                missing_info.append("meeting title")
            if not meeting_info.get("start_time"):
                missing_info.append("date and time")
            if not meeting_info.get("participants"):
                missing_info.append("participants")
            if not meeting_info.get("duration_minutes"):
                missing_info.append("duration")
            if missing_info:
                try:
                    context = self._build_conversation_context(user_id, message)
                    prompt = f"""You are a helpful scheduling assistant. The user wants to schedule a meeting but is missing some information.

Context:
{context}

Information we have: {meeting_info}
Missing information: {missing_info}

Please ask for the missing information in a natural, conversational way. Be helpful and specific about what you need.

Response:"""
                    llm_response = await self.llm.ainvoke(prompt)
                    natural_question = self._get_llm_content(llm_response).strip()
                    self.pending_actions[user_id] = {
                        "action": "create_meeting",
                        "partial_info": meeting_info,
                        "missing_fields": missing_info
                    }
                    return {
                        "success": True,
                        "message": natural_question
                    }
                except Exception as e:
                    logger.warning(f"LLM failed for meeting creation question (using fallback): {str(e)}")
                    fallback_msg = f"I'd be happy to help you schedule a meeting! I just need a few more details: {', '.join(missing_info)}. What would you like to include?"
                    self.pending_actions[user_id] = {
                        "action": "create_meeting",
                        "partial_info": meeting_info,
                        "missing_fields": missing_info
                    }
                    return {
                        "success": True,
                        "message": fallback_msg
                    }
            # If all info is present, ask for confirmation or more info
            self.pending_actions[user_id] = {
                "action": "confirm_create_meeting",
                "meeting_proposal": meeting_info
            }
            summary = f"Here's the meeting I have ready to schedule:\n\nTitle: {meeting_info.get('title')}\nTime: {meeting_info.get('start_time')}\nDuration: {meeting_info.get('duration_minutes')} minutes\nParticipants: {meeting_info.get('participants')}\nLocation: {meeting_info.get('location', 'TBD')}\nDescription: {meeting_info.get('description', '')}"
            confirm_msg = summary + "\n\nWould you like to add more info, or should I go ahead and schedule this meeting? (Reply 'add info' to provide more details, or 'yes'/'that's enough' to confirm and schedule.)"
            return {"success": True, "message": confirm_msg}
        except Exception as e:
            logger.error(f"Error in create meeting: {str(e)}")
            return {"success": False, "message": "I'm having trouble understanding the meeting details. Could you try again?"}

    async def _handle_update_meeting_conversational(self, user_id: int, message: str) -> Dict[str, Any]:
        """Handle meeting updates conversationally with structured LLM output"""
        try:
            context = self._build_conversation_context(user_id, message)
            prompt = f"""You are a helpful scheduling assistant. The user wants to update a meeting.

Context:
{context}

Respond ONLY with a JSON object describing the action to take. Example:
{{
  \"action\": \"update_meeting\",
  \"target_title\": \"Team Sync\",
  \"updates\": {{
    \"start_time\": \"2024-06-10T15:00:00Z\",
    \"duration_minutes\": 90
  }}
}}

If any information is missing, include only what you know and set missing fields to null or empty. Do NOT add extra text.

User message: {message}
"""
            llm_response = await self.llm.ainvoke(prompt)
            llm_content = self._get_llm_content(llm_response).strip()
            action_data = self._extract_json_from_llm_output(llm_content)

            meetings = self.schedule_service.get_user_meetings(user_id)
            target_meeting = None
            updates = None
            if action_data and action_data.get("action") == "update_meeting":
                # Try to find the meeting by title
                if action_data.get("target_title"):
                    for m in meetings:
                        if m.title.lower() == action_data["target_title"].lower():
                            target_meeting = m
                            break
                updates = action_data.get("updates")
            if not target_meeting or not updates:
                # Fallback to old extraction logic
                target_meeting = self._identify_meeting_from_message(message, meetings)
                updates = self._extract_update_info(message)

            if not meetings:
                return {
                    "success": True,
                    "message": "You don't have any meetings to update. Would you like to schedule a new meeting instead?"
                }
            if not target_meeting:
                # Ask them to specify which meeting
                message_text = "I'd be happy to help you update a meeting! Which meeting would you like to change?\n\n"
                for i, meeting in enumerate(meetings, 1):
                    message_text += f"{i}. {meeting.title} - {meeting.start_time.strftime('%A, %B %d at %I:%M %p')}\n"
                self.pending_actions[user_id] = {
                    "action": "update_meeting",
                    "available_meetings": meetings
                }
                return {"success": True, "message": message_text}
            if not updates:
                # Ask what they want to change
                self.pending_actions[user_id] = {
                    "action": "update_meeting_details",
                    "target_meeting": target_meeting
                }
                return {
                    "success": True,
                    "message": f"Great! I found your meeting '{target_meeting.title}'. What would you like to change about it? (time, duration, title, etc.)"
                }
            # Apply updates
            updated_meeting = self._update_meeting_from_data(target_meeting.id, updates)
            if updated_meeting:
                return {
                    "success": True,
                    "message": f"Perfect! I've updated '{updated_meeting.title}'. Is there anything else you'd like me to help you with?"
                }
            else:
                return {"success": False, "message": "I couldn't update the meeting. Please try again."}
        except Exception as e:
            logger.error(f"Error in update meeting: {str(e)}")
            return {"success": False, "message": "I'm having trouble with that. Could you try again?"}

    async def _handle_delete_meeting_conversational(self, user_id: int, message: str) -> Dict[str, Any]:
        """Handle meeting deletion conversationally with structured LLM output and confirmation flow"""
        try:
            context = self._build_conversation_context(user_id, message)
            prompt = f"""You are a helpful scheduling assistant. The user wants to delete/cancel a meeting.

Context:
{context}

INSTRUCTIONS:
- Carefully review the user's current meetings (see the JSON list above).
- Identify the meeting the user wants to delete (by title, time, duration, etc.).
- Respond ONLY with a JSON object describing the action to take. Example:
{{
  \"action\": \"delete_meeting\",
  \"target_title\": \"Team Sync\",
  \"start_time\": \"2024-06-10T14:00:00Z\"
}}
If you cannot identify the meeting, set \"action\": \"clarify_delete\" and specify what info is missing in the JSON.
Do NOT add extra text.

User message: {message}
"""
            llm_response = await self.llm.ainvoke(prompt)
            llm_content = self._get_llm_content(llm_response).strip()
            action_data = self._extract_json_from_llm_output(llm_content)

            meetings = self.schedule_service.get_user_meetings(user_id)
            target_meeting = None
            if action_data and action_data.get("action") == "delete_meeting":
                # Try to find the meeting by title and/or time
                for m in meetings:
                    if action_data.get("target_title") and m.title.lower() == action_data["target_title"].lower():
                        if not action_data.get("start_time") or m.start_time.isoformat().startswith(action_data["start_time"][:16]):
                            target_meeting = m
                            break
            if not meetings:
                return {
                    "success": True,
                    "message": "You don't have any meetings to cancel."
                }
            if not target_meeting:
                # If LLM says clarify, ask for more info
                if action_data and action_data.get("action") == "clarify_delete":
                    missing = action_data.get("missing", "details")
                    return {"success": True, "message": f"I need more information to identify the meeting you want to cancel. Could you specify the {missing}?"}
                # Otherwise, ask user to specify
                message_text = "Which meeting would you like to cancel?\n\n"
                for i, meeting in enumerate(meetings, 1):
                    message_text += f"{i}. {meeting.title} - {meeting.start_time.strftime('%A, %B %d at %I:%M %p')}\n"
                self.pending_actions[user_id] = {
                    "action": "delete_meeting",
                    "available_meetings": meetings
                }
                return {"success": True, "message": message_text}
            # Hold pending delete proposal and ask for confirmation
            self.pending_actions[user_id] = {
                "action": "confirm_delete_meeting",
                "target_meeting": target_meeting
            }
            summary = f"Here's the meeting I found:\n\nTitle: {target_meeting.title}\nTime: {target_meeting.start_time.strftime('%A, %B %d at %I:%M %p')}\nDuration: {getattr(target_meeting, 'duration_minutes', 'N/A')} minutes\nParticipants: {getattr(target_meeting, 'participants', [])}\nLocation: {getattr(target_meeting, 'location', 'TBD')}\nDescription: {getattr(target_meeting, 'description', '')}"
            confirm_msg = summary + "\n\nAre you sure you want to delete this meeting? (Reply 'yes' to confirm, or 'no' to cancel.)"
            return {"success": True, "message": confirm_msg}
        except Exception as e:
            logger.error(f"Error in delete meeting: {str(e)}")
            return {"success": False, "message": "I'm having trouble with that. Could you try again?"}

    async def _handle_delete_all_meetings_conversational(self, user_id: int) -> Dict[str, Any]:
        """Handle deleting all meetings conversationally"""
        try:
            meetings = self.schedule_service.get_user_meetings(user_id)
            
            if not meetings:
                return {
                    "success": True,
                    "message": "You don't have any meetings to cancel."
                }
            
            # Confirm deletion
            self.pending_actions[user_id] = {
                "action": "confirm_delete_all",
                "meeting_count": len(meetings)
            }
            
            return {
                "success": True,
                "message": f"Are you sure you want to cancel all {len(meetings)} of your meetings? This cannot be undone. (yes/no)"
            }
            
        except Exception as e:
            logger.error(f"Error in delete all meetings: {str(e)}")
            return {"success": False, "message": "I'm having trouble with that. Could you try again?"}

    async def _handle_general_conversation(self, user_id: int, message: str) -> Dict[str, Any]:
        """Handle general conversation with LLM enhancement"""
        message_lower = message.lower()
        
        # Check if they're asking for help
        if any(word in message_lower for word in ["help", "what can you do", "how", "?"]):
            return {
                "success": True,
                "message": """I'm your scheduling assistant! I can help you with:

📅 **View your meetings** - "Show my meetings" or "What meetings do I have?"
📝 **Schedule new meetings** - "Schedule a meeting with John tomorrow at 2pm"
✏️ **Update meetings** - "Change my 3pm meeting to 4pm" or "Update the team meeting duration"
❌ **Cancel meetings** - "Cancel my 2pm meeting" or "Delete the team meeting"
🗓️ **Find available times** - "When am I free this week?"

Just tell me what you'd like to do, and I'll guide you through it!""",
                "needs_llm_enhancement": True
            }
        
        # Check if they're greeting
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return {
                "success": True,
                "message": "Hello! I'm here to help you manage your meetings and schedule. What would you like to do today?",
                "needs_llm_enhancement": True
            }
        
        # For other general conversation, use LLM to generate a helpful response
        try:
            context = self._build_conversation_context(user_id, message)
            prompt = f"""You are a helpful scheduling assistant. The user said: "{message}"

Context:
{context}

Please respond naturally and helpfully. If they're asking about scheduling, guide them. If they're just chatting, be friendly and ask how you can help with their schedule.

Response:"""

            try:
                llm_response = await self.llm.ainvoke(prompt)
                return {
                    "success": True,
                    "message": self._get_llm_content(llm_response).strip()
                }
            except Exception as e:
                # Any error - immediately fall back, no retries
                logger.warning(f"LLM failed for general conversation (using fallback): {str(e)}")
                # Check if it's a rate limit error and provide informative message
                if "429" in str(e) or "quota" in str(e).lower():
                    return {
                        "success": True,
                        "message": "I'm here to help you with your meetings and schedule! 📅 The AI service is currently experiencing high usage, but I can still assist you with all your scheduling tasks. You can ask me to show your meetings, schedule new ones, update existing ones, or cancel them. What would you like to do?"
                    }
                else:
                    return {
                        "success": True,
                        "message": "I'm here to help you with your meetings and schedule! You can ask me to show your meetings, schedule new ones, update existing ones, or cancel them. What would you like to do?"
                    }
                
        except Exception as e:
            logger.error(f"Error in general conversation: {str(e)}")
            return {
                "success": True,
                "message": "I'm here to help you with your meetings and schedule! What would you like to do?"
            }

    async def _handle_pending_action(self, user_id: int, message: str) -> Dict[str, Any]:
        """Handle responses to pending actions that need clarification or confirmation"""
        pending = self.pending_actions[user_id]
        action = pending["action"]
        try:
            if action == "create_meeting":
                return await self._handle_create_meeting_clarification(user_id, message, pending)
            elif action == "confirm_create_meeting":
                # Confirmation or add info
                if message.strip().lower() in ["yes", "that's enough", "confirm", "ok", "go ahead"]:
                    meeting_info = pending["meeting_proposal"]
                    del self.pending_actions[user_id]
                    return await self._create_meeting_with_info(user_id, meeting_info)
                elif message.strip().lower() in ["add info", "add more", "more info", "add details"]:
                    # Ask LLM to update the proposal with new info
                    context = self._build_conversation_context(user_id, message)
                    proposal = pending["meeting_proposal"]
                    prompt = f"""You are a helpful scheduling assistant. The user wants to add more information to the following meeting proposal.

Current proposal:
{json.dumps(proposal, indent=2)}

User message: {message}

Update the proposal with any new details provided. Respond ONLY with the updated JSON object."""
                    llm_response = await self.llm.ainvoke(prompt)
                    llm_content = self._get_llm_content(llm_response).strip()
                    updated_proposal = self._extract_json_from_llm_output(llm_content)
                    if updated_proposal:
                        self.pending_actions[user_id]["meeting_proposal"] = updated_proposal
                        summary = f"Here's the updated meeting proposal:\n\nTitle: {updated_proposal.get('title')}\nTime: {updated_proposal.get('start_time')}\nDuration: {updated_proposal.get('duration_minutes')} minutes\nParticipants: {updated_proposal.get('participants')}\nLocation: {updated_proposal.get('location', 'TBD')}\nDescription: {updated_proposal.get('description', '')}"
                        confirm_msg = summary + "\n\nWould you like to add more info, or should I go ahead and schedule this meeting? (Reply 'add info' to provide more details, or 'yes'/'that's enough' to confirm and schedule.)"
                        return {"success": True, "message": confirm_msg}
                    else:
                        return {"success": False, "message": "Sorry, I couldn't update the proposal. Please try again."}
                else:
                    # Treat as more info
                    return await self._handle_create_meeting_clarification(user_id, message, pending)
            elif action == "delete_meeting":
                return await self._handle_delete_meeting_selection(user_id, message, pending)
            elif action == "confirm_delete_meeting":
                # Confirmation for delete
                if message.strip().lower() in ["yes", "y", "confirm", "ok"]:
                    target_meeting = pending["target_meeting"]
                    self.schedule_service.delete_meeting(target_meeting.id)
                    del self.pending_actions[user_id]
                    return {
                        "success": True,
                        "message": f"I've deleted the meeting '{target_meeting.title}' on {target_meeting.start_time.strftime('%A, %B %d at %I:%M %p')}. Is there anything else I can help you with?"
                    }
                else:
                    del self.pending_actions[user_id]
                    return {
                        "success": True,
                        "message": "No problem! The meeting is still scheduled. Is there anything else you'd like me to help you with?"
                    }
            elif action == "update_meeting":
                return await self._handle_update_meeting_selection(user_id, message, pending)
            elif action == "update_meeting_details":
                return await self._handle_update_meeting_details(user_id, message, pending)
            elif action == "confirm_delete":
                return await self._handle_confirm_delete(user_id, message, pending)
            elif action == "confirm_delete_all":
                return await self._handle_confirm_delete_all(user_id, message, pending)
            else:
                del self.pending_actions[user_id]
                return await self._handle_general_conversation(user_id, message)
        except Exception as e:
            logger.error(f"Error handling pending action: {str(e)}")
            del self.pending_actions[user_id]
            return {"success": False, "message": "I'm having trouble with that. Let's start over - what would you like to do?"}

    async def _handle_create_meeting_clarification(self, user_id: int, message: str, pending: dict) -> Dict[str, Any]:
        """Handle clarification for meeting creation with LLM enhancement"""
        partial_info = pending["partial_info"]
        missing_fields = pending["missing_fields"]
        
        print(f"🔄 Meeting clarification - current partial info: {partial_info}")
        print(f"🔄 Meeting clarification - missing fields: {missing_fields}")
        print(f"🔄 Meeting clarification - user message: '{message}'")
        
        # Extract additional info from the message
        new_info = self._extract_meeting_info(message)
        print(f"🔄 Meeting clarification - new info extracted: {new_info}")
        
        partial_info.update(new_info)
        print(f"🔄 Meeting clarification - updated partial info: {partial_info}")
        
        # Check what's still missing - FIXED: Check the updated partial_info, not the original missing_fields
        still_missing = []
        if not partial_info.get("title"):
            still_missing.append("meeting title")
        if not partial_info.get("start_time"):
            still_missing.append("date and time")
        if not partial_info.get("participants"):
            still_missing.append("participants")
        if not partial_info.get("duration_minutes"):
            still_missing.append("duration")
        
        print(f"🔄 Meeting clarification - still missing: {still_missing}")
        
        if still_missing:
            # Still need more info - use LLM for natural follow-up
            try:
                context = self._build_conversation_context(user_id, message)
                prompt = f"""You are a helpful scheduling assistant. The user is providing information for a meeting, but we still need more details.

Context:
{context}

Information we have so far: {partial_info}
Still missing: {still_missing}

Please ask for the remaining information in a natural, conversational way. Acknowledge what they've provided and ask for what's still needed.

Response:"""

                llm_response = await self.llm.ainvoke(prompt)
                natural_followup = self._get_llm_content(llm_response).strip()
                
                pending["partial_info"] = partial_info
                pending["missing_fields"] = still_missing
                
                return {
                    "success": True,
                    "message": natural_followup
                }
                
            except Exception as e:
                # Any error - immediately fall back, no retries
                logger.warning(f"LLM failed for meeting clarification (using fallback): {str(e)}")
                
                # Create more intelligent follow-up messages
                if len(still_missing) == 1:
                    missing_text = still_missing[0]
                    if missing_text == "meeting title":
                        followup_msg = "Great! What would you like to call this meeting?"
                    elif missing_text == "date and time":
                        followup_msg = "Great! When would you like to have this meeting?"
                    elif missing_text == "participants":
                        followup_msg = "Great! Who would you like to invite to this meeting?"
                    elif missing_text == "duration":
                        followup_msg = "Great! How long should this meeting be?"
                    else:
                        followup_msg = f"Great! I just need to know the {missing_text}."
                else:
                    missing_text = ", ".join(still_missing[:-1])
                    if len(still_missing) > 1:
                        missing_text += f" and {still_missing[-1]}"
                    else:
                        missing_text = still_missing[0]
                    followup_msg = f"Great! I just need a bit more: {missing_text}. What would you like to include?"
                
                pending["partial_info"] = partial_info
                pending["missing_fields"] = still_missing
                
                return {
                    "success": True,
                    "message": followup_msg
                }
        else:
            # We have everything, create the meeting
            print(f"✅ Meeting clarification - all info complete, creating meeting")
            del self.pending_actions[user_id]
            return await self._create_meeting_with_info(user_id, partial_info)

    async def _handle_update_meeting_selection(self, user_id: int, message: str, pending: dict) -> Dict[str, Any]:
        """Handle meeting selection for updates"""
        meetings = pending["available_meetings"]
        
        # Try to parse selection (number or name)
        try:
            if message.strip().isdigit():
                index = int(message.strip()) - 1
                if 0 <= index < len(meetings):
                    target_meeting = meetings[index]
                else:
                    return {"success": True, "message": "That number doesn't match any meeting. Please try again."}
            else:
                target_meeting = self._identify_meeting_from_message(message, meetings)
                if not target_meeting:
                    return {"success": True, "message": "I couldn't find that meeting. Please try again."}
        except:
            return {"success": True, "message": "I didn't understand that. Please try again."}
        
        # Update pending action
        self.pending_actions[user_id] = {
            "action": "update_meeting_details",
            "target_meeting": target_meeting
        }
        
        return {
            "success": True,
            "message": f"Perfect! I found '{target_meeting.title}'. What would you like to change about it? (time, duration, title, etc.)"
        }

    async def _handle_update_meeting_details(self, user_id: int, message: str, pending: dict) -> Dict[str, Any]:
        """Handle updating meeting details"""
        target_meeting = pending["target_meeting"]
        
        # Extract update information
        updates = self._extract_update_info(message)
        
        if not updates:
            return {
                "success": True,
                "message": "I didn't understand what you want to change. Could you be more specific? (e.g., 'change the time to 3pm' or 'make it 30 minutes')"
            }
        
        # Apply updates
        try:
            updated_meeting = self._update_meeting_from_data(target_meeting.id, updates)
            del self.pending_actions[user_id]
            
            if updated_meeting:
                return {
                    "success": True,
                    "message": f"Perfect! I've updated '{updated_meeting.title}'. Is there anything else you'd like me to help you with?"
                }
            else:
                return {"success": False, "message": "I couldn't update the meeting. Please try again."}
                
        except Exception as e:
            logger.error(f"Error updating meeting: {str(e)}")
            return {"success": False, "message": "I'm having trouble updating the meeting. Please try again."}

    async def _handle_delete_meeting_selection(self, user_id: int, message: str, pending: dict) -> Dict[str, Any]:
        """Handle meeting selection for deletion"""
        meetings = pending["available_meetings"]
        
        # Try to parse selection
        try:
            if message.strip().isdigit():
                index = int(message.strip()) - 1
                if 0 <= index < len(meetings):
                    target_meeting = meetings[index]
                else:
                    return {"success": True, "message": "That number doesn't match any meeting. Please try again."}
            else:
                target_meeting = self._identify_meeting_from_message(message, meetings)
                if not target_meeting:
                    return {"success": True, "message": "I couldn't find that meeting. Please try again."}
        except:
            return {"success": True, "message": "I didn't understand that. Please try again."}
        
        # Confirm deletion
        self.pending_actions[user_id] = {
            "action": "confirm_delete_meeting",
            "target_meeting": target_meeting
        }
        
        return {
            "success": True,
            "message": f"Are you sure you want to delete '{target_meeting.title}' on {target_meeting.start_time.strftime('%A, %B %d')} at {target_meeting.start_time.strftime('%I:%M %p')}? (yes/no)"
        }

    async def _handle_confirm_delete(self, user_id: int, message: str, pending: dict) -> Dict[str, Any]:
        """Handle confirmation for meeting deletion"""
        target_meeting = pending["target_meeting"]
        
        if message.lower().strip() in ["yes", "y", "confirm", "ok"]:
            try:
                self.schedule_service.delete_meeting(target_meeting.id)
                del self.pending_actions[user_id]
                return {
                    "success": True,
                    "message": f"I've cancelled '{target_meeting.title}' for you. Is there anything else you'd like me to help you with?"
                }
            except Exception as e:
                logger.error(f"Error deleting meeting: {str(e)}")
                return {"success": False, "message": "I couldn't cancel the meeting. Please try again."}
        else:
            del self.pending_actions[user_id]
            return {
                "success": True,
                "message": "No problem! The meeting is still scheduled. Is there anything else you'd like me to help you with?"
            }

    async def _handle_confirm_delete_all(self, user_id: int, message: str, pending: dict) -> Dict[str, Any]:
        """Handle confirmation for deleting all meetings"""
        meeting_count = pending["meeting_count"]
        
        if message.lower().strip() in ["yes", "y", "confirm", "ok"]:
            try:
                meetings = self.schedule_service.get_user_meetings(user_id)
                for meeting in meetings:
                    self.schedule_service.delete_meeting(meeting.id)
                del self.pending_actions[user_id]
                return {
                    "success": True,
                    "message": f"I've cancelled all {meeting_count} meetings for you. Is there anything else you'd like me to help you with?"
                }
            except Exception as e:
                logger.error(f"Error deleting all meetings: {str(e)}")
                return {"success": False, "message": "I couldn't cancel the meetings. Please try again."}
        else:
            del self.pending_actions[user_id]
            return {
                "success": True,
                "message": "No problem! All your meetings are still scheduled. Is there anything else you'd like me to help you with?"
            }

    async def _create_meeting_with_info(self, user_id: int, meeting_info: dict) -> Dict[str, Any]:
        """Create a meeting with the provided information"""
        try:
            # Set defaults for missing fields
            meeting_info = {
                "title": meeting_info.get("title", "Untitled Meeting"),
                "description": meeting_info.get("description", ""),
                "duration_minutes": meeting_info.get("duration_minutes", 60),
                "participants": meeting_info.get("participants", [user_id]),
                "start_time": meeting_info.get("start_time", ""),
                "location": meeting_info.get("location", "TBD")
            }
            
            if not meeting_info["start_time"]:
                return {"success": False, "message": "I need a date and time for the meeting. Could you provide that?"}
            
            # Create the meeting
            meeting = self._create_meeting_from_data(meeting_info, user_id)
            
            if meeting:
                # Use LLM to generate a natural success message
                try:
                    context = self._build_conversation_context(user_id, "Meeting created successfully")
                    prompt = f"""You are a helpful scheduling assistant. The user just successfully created a meeting.

Context:
{context}

Meeting details:
- Title: {meeting.title}
- Date: {meeting.start_time.strftime('%A, %B %d')}
- Time: {meeting.start_time.strftime('%I:%M %p')}
- Duration: {meeting.duration_minutes} minutes

Please provide a warm, natural confirmation message. Be enthusiastic and helpful. Ask if there's anything else they need help with.

Response:"""

                    llm_response = await self.llm.ainvoke(prompt)
                    success_message = self._get_llm_content(llm_response).strip()
                    
                    return {
                        "success": True,
                        "message": success_message
                    }
                    
                except Exception as e:
                    # Any error - immediately fall back, no retries
                    logger.warning(f"LLM failed for success message (using fallback): {str(e)}")
                    return {
                        "success": True,
                        "message": f"Perfect! I've scheduled '{meeting.title}' for {meeting.start_time.strftime('%A, %B %d')} at {meeting.start_time.strftime('%I:%M %p')} ({meeting.duration_minutes} minutes). Is there anything else you'd like me to help you with?"
                    }
            else:
                return {"success": False, "message": "I couldn't schedule the meeting. Please try again."}
                
        except Exception as e:
            logger.error(f"Error creating meeting: {str(e)}")
            return {"success": False, "message": "I'm having trouble scheduling the meeting. Please try again."}

    def _extract_meeting_info(self, message: str) -> dict:
        """Extract meeting information from natural language"""
        info = {}
        message_lower = message.lower()
        
        print(f"🔍 Extracting meeting info from: '{message}'")
        
        # Extract title (look for quotes or specific patterns)
        title_match = re.search(r'"([^"]+)"', message)
        if title_match:
            info["title"] = title_match.group(1)
        elif "meeting" in message_lower:
            # Try to extract title from context
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() == "meeting" and i > 0:
                    # Look for title before "meeting"
                    potential_title = " ".join(words[max(0, i-2):i])
                    if potential_title and len(potential_title) > 2:
                        info["title"] = potential_title
                    break
        
        # Extract time
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):(\d{2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) == 3:  # 1:30pm format
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    period = match.group(3)
                elif len(match.groups()) == 2:  # 2pm format
                    hour = int(match.group(1))
                    minute = 0
                    period = match.group(2)
                else:  # 24h format
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    period = "am" if hour < 12 else "pm"
                
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                # Combine with today's date for now
                today = datetime.now().date()
                info["start_time"] = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)).isoformat()
                break
        
        # Extract duration - improved pattern to handle "2 hours", "30 minutes", etc.
        duration_patterns = [
            r'(\d+)\s*(hour|hours|hr|hrs)',
            r'(\d+)\s*(minute|minutes|min|mins)',
            r'(\d+)\s*(hour|hours|hr|hrs)\s*(\d+)\s*(minute|minutes|min|mins)',  # "1 hour 30 minutes"
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, message_lower)
            if match:
                print(f"⏱️ Duration match found: {match.groups()}")
                if len(match.groups()) == 2:  # Single unit
                    value = int(match.group(1))
                    unit = match.group(2)
                    if unit in ["hour", "hours", "hr", "hrs"]:
                        info["duration_minutes"] = value * 60
                    else:
                        info["duration_minutes"] = value
                    print(f"⏱️ Extracted duration: {info['duration_minutes']} minutes")
                    break
                elif len(match.groups()) == 4:  # "1 hour 30 minutes" format
                    hours = int(match.group(1))
                    minutes = int(match.group(3))
                    info["duration_minutes"] = hours * 60 + minutes
                    print(f"⏱️ Extracted duration: {info['duration_minutes']} minutes")
                    break
        
        # Extract participants (look for "with" followed by names)
        with_match = re.search(r'with\s+([^,]+)', message_lower)
        if with_match:
            participants_text = with_match.group(1)
            # For now, just store as text - in a real app you'd look up user IDs
            info["participants"] = [participants_text.strip()]
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            info["emails"] = emails
        
        # Extract topic/description (look for "about" or "regarding")
        about_match = re.search(r'about\s+([^,]+)', message_lower)
        if about_match:
            topic = about_match.group(1).strip()
            if topic and len(topic) > 2:
                info["description"] = topic
        
        print(f"📋 Extracted meeting info: {info}")
        return info

    def _extract_update_info(self, message: str) -> dict:
        """Extract update information from natural language"""
        updates = {}
        message_lower = message.lower()
        
        # Extract time changes
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) == 3:
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    period = match.group(3)
                else:
                    hour = int(match.group(1))
                    minute = 0
                    period = match.group(2)
                
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                today = datetime.now().date()
                updates["start_time"] = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)).isoformat()
                break
        
        # Extract duration changes
        duration_match = re.search(r'(\d+)\s*(min|minute|minutes|hour|hours)', message_lower)
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            if unit in ["hour", "hours"]:
                updates["duration_minutes"] = value * 60
            else:
                updates["duration_minutes"] = value
        
        # Extract title changes
        title_match = re.search(r'title\s+(?:to\s+)?"([^"]+)"', message_lower)
        if title_match:
            updates["title"] = title_match.group(1)
        
        return updates

    def _identify_meeting_from_message(self, message: str, meetings: List) -> Optional[Any]:
        """Identify which meeting the user is referring to"""
        message_lower = message.lower()
        
        # Check for time references
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) == 3:
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    period = match.group(3)
                else:
                    hour = int(match.group(1))
                    minute = 0
                    period = match.group(2)
                
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                # Find meeting at this time
                for meeting in meetings:
                    if meeting.start_time.hour == hour and meeting.start_time.minute == minute:
                        return meeting
        
        # Check for title matches
        for meeting in meetings:
            if meeting.title.lower() in message_lower:
                return meeting
        
        # Check for "first", "second", etc.
        if "first" in message_lower or "1st" in message_lower:
            if meetings:
                return meetings[0]
        elif "second" in message_lower or "2nd" in message_lower:
            if len(meetings) > 1:
                return meetings[1]
        elif "last" in message_lower:
            if meetings:
                return meetings[-1]
        
        return None

    # Keep the existing helper methods for database operations
    def _create_meeting_from_data(self, meeting_data: Dict[str, Any], user_id: int) -> Any:
        """Create a meeting in the database from parsed data"""
        try:
            logger.info(f"Creating meeting with data: {meeting_data}")
            logger.info(f"User ID: {user_id}")
            
            # Parse start time
            start_time = datetime.fromisoformat(meeting_data["start_time"].replace('Z', '+00:00'))
            end_time = start_time + timedelta(minutes=meeting_data["duration_minutes"])
            
            logger.info(f"Parsed start_time: {start_time}, end_time: {end_time}")
            
            # Convert participant emails to user IDs if needed
            participant_ids = []
            for participant in meeting_data["participants"]:
                if isinstance(participant, str) and '@' in participant:
                    # It's an email, find the user
                    user = self.user_service.get_user_by_email(participant)
                    if user:
                        participant_ids.append(user.id)
                        logger.info(f"Found user for email {participant}: {user.id}")
                    else:
                        logger.warning(f"User with email {participant} not found")
                else:
                    # It's already a user ID
                    participant_ids.append(participant)
                    logger.info(f"Using participant ID: {participant}")
            
            logger.info(f"Final participant IDs: {participant_ids}")
            
            # Create meeting object
            meeting_obj = {
                "title": meeting_data["title"],
                "description": meeting_data.get("description", ""),
                "duration_minutes": meeting_data["duration_minutes"],
                "start_time": start_time,
                "end_time": end_time,
                "organizer_id": user_id,
                "participants": participant_ids,
                "location": meeting_data.get("location", "TBD"),
                "status": "confirmed"
            }
            
            logger.info(f"Meeting object to create: {meeting_obj}")
            
            # Save to database
            meeting = self.schedule_service.create_meeting(meeting_obj)
            logger.info(f"Meeting created: {meeting}")
            return meeting
            
        except Exception as e:
            logger.error(f"Error creating meeting: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _update_meeting_from_data(self, meeting_id: int, updates: Dict[str, Any]) -> Any:
        """Update a meeting in the database from parsed data"""
        try:
            from app.models.schedule import MeetingUpdate
            
            # Get existing meeting to preserve data not being updated
            existing_meeting = self.schedule_service.get_meeting(meeting_id)
            if not existing_meeting:
                logger.error(f"Meeting {meeting_id} not found for update")
                return None
            
            # Prepare update data
            update_data = {}
            if "title" in updates:
                update_data["title"] = updates["title"]
            if "description" in updates:
                update_data["description"] = updates["description"]
            if "location" in updates:
                update_data["location"] = updates["location"]
            
            # Handle duration and time updates
            new_duration = updates.get("duration_minutes", existing_meeting.duration_minutes)
            new_start_time = existing_meeting.start_time
            
            if "start_time" in updates:
                new_start_time = datetime.fromisoformat(updates["start_time"].replace('Z', '+00:00'))
                update_data["start_time"] = new_start_time
            
            if "duration_minutes" in updates:
                update_data["duration_minutes"] = new_duration
            
            # Always recalculate end_time based on start_time and duration
            new_end_time = new_start_time + timedelta(minutes=new_duration)
            update_data["end_time"] = new_end_time
            
            logger.info(f"Updating meeting {meeting_id} with data: {update_data}")
            
            # Create MeetingUpdate object
            meeting_update = MeetingUpdate(**update_data)
            
            # Update in database
            meeting = self.schedule_service.update_meeting(meeting_id, meeting_update)
            return meeting
            
        except Exception as e:
            logger.error(f"Error updating meeting: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def schedule_meeting(self, request: MeetingRequest) -> MeetingResponse:
        """Legacy method for backward compatibility"""
        return await self.process_message(request.user_id, request.request_text)

    async def _enhance_response_with_llm(self, user_id: int, user_message: str, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to enhance responses with more natural language"""
        try:
            # Get conversation context
            context = self._build_conversation_context(user_id, user_message)
            
            # Create prompt for LLM enhancement
            prompt = f"""You are a helpful scheduling assistant. The user said: "{user_message}"

Based on the conversation context and database state, I need to respond naturally and conversationally.

Context:
{context}

Current response: {response.get('message', '')}

Please enhance this response to be more natural, warm, and conversational while keeping the same information. 
Make it sound like a helpful human assistant, not a robot.

Enhanced response:"""

            # Try to get LLM enhancement with immediate fallback
            try:
                llm_response = await self.llm.ainvoke(prompt)
                enhanced_message = self._get_llm_content(llm_response).strip()
                
                # Use enhanced response if it's reasonable
                if len(enhanced_message) > 10 and len(enhanced_message) < 500:
                    return {
                        **response,
                        "message": enhanced_message
                    }
            except Exception as e:
                # Any error - immediately use original response, no retries
                logger.warning(f"LLM enhancement failed (using original): {str(e)}")
                # Add a subtle note about API limits if it's a rate limit error
                if "429" in str(e) or "quota" in str(e).lower():
                    original_message = response.get('message', '')
                    if not any(word in original_message.lower() for word in ["api", "limit", "quota", "temporarily"]):
                        response["message"] = original_message + "\n\n💡 *Note: AI service is experiencing high usage, but all functionality is available.*"
                pass
            
            return None  # Keep original response
            
        except Exception as e:
            logger.error(f"Error enhancing response: {str(e)}")
            return None

    def _build_conversation_context(self, user_id: int, current_message: str) -> str:
        """Build context for LLM enhancement, including a machine-readable JSON list of all current meetings"""
        try:
            # Get user's meetings
            meetings = self.schedule_service.get_user_meetings(user_id)
            meetings_context = ""
            meetings_json = []
            if meetings:
                meetings_context = "Current meetings (JSON):\n"
                for meeting in meetings:
                    meeting_info = {
                        "title": meeting.title,
                        "start_time": meeting.start_time.isoformat(),
                        "end_time": meeting.end_time.isoformat() if hasattr(meeting, 'end_time') else None,
                        "duration_minutes": getattr(meeting, 'duration_minutes', None)
                    }
                    meetings_json.append(meeting_info)
                meetings_context += json.dumps(meetings_json, indent=2)
            else:
                meetings_context = "No meetings currently scheduled."
            # Get recent conversation
            history = self.conversation_history.get(user_id, [])
            recent_context = ""
            if history:
                recent_context = "Recent conversation:\n"
                for exchange in history[-3:]:  # Last 3 exchanges
                    role = "User" if exchange["role"] == "user" else "Assistant"
                    recent_context += f"{role}: {exchange['content']}\n"
            return f"""User ID: {user_id}
{meetings_context}

{recent_context}

Current user message: {current_message}"""
        except Exception as e:
            logger.error(f"Error building context: {str(e)}")
            return f"User message: {current_message}"

    def _get_llm_content(self, llm_response):
        if isinstance(llm_response, dict):
            return llm_response.get("content", "")
        return getattr(llm_response, "content", "")

    def _extract_json_from_llm_output(self, output: str) -> Optional[dict]:
        """Try to robustly extract a JSON object from LLM output."""
        try:
            # Try direct JSON
            return json.loads(output)
        except Exception:
            pass
        # Try to extract JSON substring
        try:
            start = output.find('{')
            end = output.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = output[start:end+1]
                return json.loads(json_str)
        except Exception:
            pass
        # Try ast.literal_eval as a last resort
        try:
            return ast.literal_eval(output)
        except Exception:
            pass
        return None 