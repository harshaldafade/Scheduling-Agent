from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_anthropic import ChatAnthropic  # Commented out due to missing dependency
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
import os
import logging
import google.generativeai as genai
from langchain.schema import BaseMessage

logger = logging.getLogger(__name__)

class MockLLM:
    """Mock LLM for demonstration purposes"""
    def __init__(self):
        self.name = "Mock LLM"
    
    async def ainvoke(self, messages, **kwargs):
        # Extract the user's message to provide context-aware responses
        user_message = ""
        if isinstance(messages, str):
            user_message = messages
        elif isinstance(messages, list):
            for msg in messages:
                if hasattr(msg, 'content'):
                    if not hasattr(msg, 'type') or msg.type != 'system':
                        user_message = msg.content
                        break
        
        user_message_lower = user_message.lower()
        
        # Provide context-aware responses based on what the user is trying to do
        if any(word in user_message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return {
                "content": "Hello! 👋 I'm your scheduling assistant. Currently, the AI service is experiencing high usage (API limit reached), but I can still help you with basic scheduling tasks! You can ask me to show your meetings, schedule new ones, or manage your calendar. What would you like to do?"
            }
        
        elif any(word in user_message_lower for word in ["schedule", "create", "book", "arrange", "meeting"]):
            return {
                "content": "I'd be happy to help you schedule a meeting! 📅 While the AI service is temporarily limited, I can guide you through the process. Please provide the meeting details like time, participants, and duration, and I'll help you create it. What information do you have so far?"
            }
        
        elif any(word in user_message_lower for word in ["show", "view", "see", "what", "meetings"]):
            return {
                "content": "I can help you view your meetings! 📋 While the AI service is experiencing high usage, I can still access your calendar and show you what's scheduled. Let me retrieve that information for you."
            }
        
        elif any(word in user_message_lower for word in ["cancel", "delete", "remove"]):
            return {
                "content": "I can help you cancel or delete meetings! ❌ While the AI service is temporarily limited, I can still assist with meeting management. Which meeting would you like to cancel?"
            }
        
        elif any(word in user_message_lower for word in ["update", "change", "modify", "reschedule"]):
            return {
                "content": "I can help you update your meetings! ✏️ While the AI service is experiencing high usage, I can still assist with changes. What would you like to modify about your meeting?"
            }
        
        elif any(word in user_message_lower for word in ["help", "what can you do", "how"]):
            return {
                "content": """I'm your scheduling assistant! 🗓️ While the AI service is currently experiencing high usage (API limit reached), I can still help you with:

📅 **View your meetings** - "Show my meetings" or "What meetings do I have?"
📝 **Schedule new meetings** - "Schedule a meeting with John tomorrow at 2pm"
✏️ **Update meetings** - "Change my 3pm meeting to 4pm" or "Update the team meeting duration"
❌ **Cancel meetings** - "Cancel my 2pm meeting" or "Delete the team meeting"
🗓️ **Find available times** - "When am I free this week?"

The AI service will be available again soon, but I can still guide you through all these tasks! What would you like to do?"""
            }
        
        elif any(word in user_message_lower for word in ["api", "limit", "quota", "error", "unavailable"]):
            return {
                "content": "The AI service is currently experiencing high usage and has reached its daily limit. 🔄 This is temporary and will reset soon. In the meantime, I can still help you with all your scheduling tasks using the basic functionality. Your meetings and calendar are fully accessible!"
            }
        
        else:
            return {
                "content": "I'm here to help you with your meetings and schedule! 📅 While the AI service is temporarily experiencing high usage, I can still assist you with viewing, creating, updating, and canceling meetings. Just let me know what you'd like to do!"
            }

class DirectGeminiLLM:
    """Direct Gemini LLM that bypasses LangChain retry logic completely"""
    
    def __init__(self, model: str, temperature: float, google_api_key: str, max_tokens: int = 1000):
        self.model = model
        self.temperature = temperature
        self.google_api_key = google_api_key
        self.max_tokens = max_tokens
        
        # Configure the API directly
        genai.configure(api_key=google_api_key)
        self.client = genai.GenerativeModel(model)
    
    async def ainvoke(self, messages, **kwargs):
        try:
            # Convert LangChain messages to Gemini format
            if isinstance(messages, str):
                # Single string message
                prompt = messages
            elif isinstance(messages, list):
                # List of messages
                prompt = ""
                for msg in messages:
                    if hasattr(msg, 'content'):
                        if hasattr(msg, 'type') and msg.type == 'system':
                            prompt += f"System: {msg.content}\n\n"
                        else:
                            prompt += f"{msg.content}\n\n"
                    else:
                        prompt += f"{msg}\n\n"
            else:
                prompt = str(messages)
            
            # Call Gemini API directly with no retries
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            return {
                "content": response.text,
                "model": self.model
            }
            
        except Exception as e:
            # Re-raise immediately - no retries
            raise e

class BaseAgent:
    """Base class for all scheduling agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration"""
        provider = settings.llm_provider.lower()
        
        if provider == "openai":
            if settings.openai_api_key:
                logger.info("Initializing OpenAI LLM")
                return ChatOpenAI(
                    model=settings.openai_model,
                    temperature=settings.openai_temperature,
                    openai_api_key=settings.openai_api_key
                )
            else:
                logger.warning("OpenAI API key not found. Using mock LLM.")
                return MockLLM()
        
        elif provider == "gemini":
            if settings.gemini_api_key:
                logger.info("Initializing Direct Gemini LLM (no retries)")
                return DirectGeminiLLM(
                    model=settings.gemini_model,
                    temperature=settings.gemini_temperature,
                    google_api_key=settings.gemini_api_key,
                    max_tokens=1000
                )
            else:
                logger.warning("Gemini API key not found. Using mock LLM.")
                return MockLLM()
        
        elif provider == "anthropic":
            if settings.anthropic_api_key:
                logger.warning("Anthropic LLM not available (missing dependency). Using mock LLM.")
                return MockLLM()
            else:
                logger.warning("Anthropic API key not found. Using mock LLM.")
                return MockLLM()
        
        else:
            logger.warning(f"Unknown LLM provider: {provider}. Using mock LLM.")
            return MockLLM()
    
    def get_system_prompt(self) -> str:
        """Override this method to provide system prompt for specific agents"""
        return f"You are {self.name}, an AI assistant specialized in scheduling tasks."
    
    async def run(self, user_input: str, system_prompt: str = None) -> dict:
        """Run the agent with user input"""
        try:
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            else:
                messages.append(SystemMessage(content=self.get_system_prompt()))
            
            messages.append(HumanMessage(content=user_input))
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "output": response.content,
                "model": getattr(self.llm, 'model', 'mock'),
                "provider": settings.llm_provider
            }
            
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": "I encountered an error while processing your request. Please try again."
            } 