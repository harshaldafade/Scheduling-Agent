from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime
from app.services.user_service import UserService
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class PreferenceService:
    """Service class for user preference learning and analysis"""
    
    def __init__(self):
        self.user_service = UserService()
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
    def learn_from_feedback(self, user_id: int, feedback: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from user feedback to improve future scheduling suggestions"""
        try:
            user = self.user_service.get_user(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for preference learning")
                return {}
            
            current_preferences = user.preferences or {}
            
            # Analyze feedback sentiment and extract preferences
            extracted_preferences = self._extract_preferences_from_feedback(feedback, context)
            
            # Update user preferences
            updated_preferences = self._merge_preferences(current_preferences, extracted_preferences)
            
            # Save updated preferences
            self.user_service.update_user_preferences(user_id, updated_preferences)
            
            logger.info(f"Updated preferences for user {user_id} based on feedback")
            return updated_preferences
            
        except Exception as e:
            logger.error(f"Error learning from feedback for user {user_id}: {str(e)}")
            return {}
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            user = self.user_service.get_user(user_id)
            if not user:
                return {}
            
            return user.preferences or {}
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
            return {}
    
    def find_similar_users(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find users with similar preferences"""
        try:
            target_user = self.user_service.get_user(user_id)
            if not target_user:
                return []
            
            all_users = self.user_service.get_all_users()
            similar_users = []
            
            target_preferences = target_user.preferences or {}
            
            for user in all_users:
                if user.id == user_id:
                    continue
                
                user_preferences = user.preferences or {}
                similarity_score = self._calculate_preference_similarity(
                    target_preferences, user_preferences
                )
                
                if similarity_score > 0.3:  # Threshold for similarity
                    similar_users.append({
                        "user_id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "similarity_score": similarity_score,
                        "preferences": user_preferences
                    })
            
            # Sort by similarity score and return top results
            similar_users.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similar_users[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar users for {user_id}: {str(e)}")
            return []
    
    def get_preference_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Get personalized recommendations based on user preferences"""
        try:
            user_preferences = self.get_user_preferences(user_id)
            similar_users = self.find_similar_users(user_id, limit=3)
            
            recommendations = {
                "preferred_meeting_times": self._extract_preferred_times(user_preferences),
                "preferred_meeting_duration": self._extract_preferred_duration(user_preferences),
                "preferred_meeting_types": self._extract_preferred_types(user_preferences),
                "similar_user_patterns": self._analyze_similar_user_patterns(similar_users),
                "suggested_improvements": self._generate_suggestions(user_preferences, similar_users)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
            return {}
    
    def _extract_preferences_from_feedback(self, feedback: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract preferences from user feedback using NLP techniques"""
        preferences = {}
        
        # Simple keyword-based preference extraction
        feedback_lower = feedback.lower()
        
        # Time preferences
        if any(word in feedback_lower for word in ["morning", "early", "9am", "10am"]):
            preferences["preferred_time_slots"] = ["morning"]
        elif any(word in feedback_lower for word in ["afternoon", "2pm", "3pm", "4pm"]):
            preferences["preferred_time_slots"] = ["afternoon"]
        elif any(word in feedback_lower for word in ["evening", "late", "5pm", "6pm"]):
            preferences["preferred_time_slots"] = ["evening"]
        
        # Duration preferences
        if any(word in feedback_lower for word in ["short", "quick", "30min", "30 minutes"]):
            preferences["preferred_duration"] = "short"
        elif any(word in feedback_lower for word in ["long", "extended", "2 hours", "2hr"]):
            preferences["preferred_duration"] = "long"
        else:
            preferences["preferred_duration"] = "standard"
        
        # Meeting type preferences
        if any(word in feedback_lower for word in ["interview", "technical", "coding"]):
            preferences["preferred_meeting_types"] = ["interview"]
        elif any(word in feedback_lower for word in ["team", "collaboration", "planning"]):
            preferences["preferred_meeting_types"] = ["team_meeting"]
        elif any(word in feedback_lower for word in ["client", "customer", "external"]):
            preferences["preferred_meeting_types"] = ["client_meeting"]
        
        # Sentiment analysis
        positive_words = ["good", "great", "perfect", "excellent", "love", "prefer"]
        negative_words = ["bad", "terrible", "hate", "avoid", "never", "conflict"]
        
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)
        
        if positive_count > negative_count:
            preferences["feedback_sentiment"] = "positive"
        elif negative_count > positive_count:
            preferences["feedback_sentiment"] = "negative"
        else:
            preferences["feedback_sentiment"] = "neutral"
        
        # Add context information
        if context:
            preferences["context"] = context
        
        return preferences
    
    def _merge_preferences(self, current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new preferences with existing ones"""
        merged = current.copy()
        
        for key, value in new.items():
            if key in merged:
                if isinstance(merged[key], list) and isinstance(value, list):
                    # Merge lists, avoiding duplicates
                    merged[key] = list(set(merged[key] + value))
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    # Recursively merge dictionaries
                    merged[key] = self._merge_preferences(merged[key], value)
                else:
                    # Override with new value
                    merged[key] = value
            else:
                merged[key] = value
        
        return merged
    
    def _calculate_preference_similarity(self, pref1: Dict[str, Any], pref2: Dict[str, Any]) -> float:
        """Calculate similarity between two preference sets"""
        try:
            # Convert preferences to text for vectorization
            text1 = json.dumps(pref1, sort_keys=True)
            text2 = json.dumps(pref2, sort_keys=True)
            
            # Vectorize and calculate cosine similarity
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating preference similarity: {str(e)}")
            return 0.0
    
    def _extract_preferred_times(self, preferences: Dict[str, Any]) -> List[str]:
        """Extract preferred meeting times from preferences"""
        time_slots = preferences.get("preferred_time_slots", [])
        if not time_slots:
            return ["morning", "afternoon"]  # Default preferences
        return time_slots
    
    def _extract_preferred_duration(self, preferences: Dict[str, Any]) -> str:
        """Extract preferred meeting duration from preferences"""
        return preferences.get("preferred_duration", "standard")
    
    def _extract_preferred_types(self, preferences: Dict[str, Any]) -> List[str]:
        """Extract preferred meeting types from preferences"""
        meeting_types = preferences.get("preferred_meeting_types", [])
        if not meeting_types:
            return ["general"]  # Default type
        return meeting_types
    
    def _analyze_similar_user_patterns(self, similar_users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns from similar users"""
        if not similar_users:
            return {}
        
        patterns = {
            "common_time_slots": [],
            "common_durations": [],
            "common_meeting_types": []
        }
        
        for user in similar_users:
            prefs = user.get("preferences", {})
            
            # Collect common patterns
            if "preferred_time_slots" in prefs:
                patterns["common_time_slots"].extend(prefs["preferred_time_slots"])
            
            if "preferred_duration" in prefs:
                patterns["common_durations"].append(prefs["preferred_duration"])
            
            if "preferred_meeting_types" in prefs:
                patterns["common_meeting_types"].extend(prefs["preferred_meeting_types"])
        
        # Get most common patterns
        from collections import Counter
        
        patterns["common_time_slots"] = [item for item, count in Counter(patterns["common_time_slots"]).most_common(3)]
        patterns["common_durations"] = [item for item, count in Counter(patterns["common_durations"]).most_common(2)]
        patterns["common_meeting_types"] = [item for item, count in Counter(patterns["common_meeting_types"]).most_common(3)]
        
        return patterns
    
    def _generate_suggestions(self, preferences: Dict[str, Any], similar_users: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on preferences and similar users"""
        suggestions = []
        
        # Check for missing preferences
        if "preferred_time_slots" not in preferences:
            suggestions.append("Consider setting preferred meeting times to get better scheduling suggestions")
        
        if "preferred_duration" not in preferences:
            suggestions.append("Set your preferred meeting duration for more accurate scheduling")
        
        if "preferred_meeting_types" not in preferences:
            suggestions.append("Specify your preferred meeting types for better categorization")
        
        # Suggestions based on similar users
        if similar_users:
            similar_patterns = self._analyze_similar_user_patterns(similar_users)
            
            if similar_patterns.get("common_time_slots"):
                suggestions.append(f"Users similar to you often prefer {', '.join(similar_patterns['common_time_slots'])} meetings")
            
            if similar_patterns.get("common_durations"):
                suggestions.append(f"Consider {similar_patterns['common_durations'][0]} duration meetings like similar users")
        
        return suggestions[:5]  # Limit to 5 suggestions 