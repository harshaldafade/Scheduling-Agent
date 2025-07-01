from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.user import User, UserCreate, UserUpdate, UserResponse
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related operations"""
    
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = self._get_db()
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        db = self._get_db()
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
        finally:
            db.close()
    
    def get_user_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        """Get user by OAuth provider and provider ID"""
        db = self._get_db()
        try:
            return db.query(User).filter(
                User.provider == provider,
                User.provider_id == provider_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting user by provider {provider}:{provider_id}: {str(e)}")
            return None
        finally:
            db.close()
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user from dictionary data (supports OAuth)"""
        db = self._get_db()
        try:
            # Check if user already exists by email
            existing_user = self.get_user_by_email(user_data["email"])
            if existing_user:
                logger.warning(f"User with email {user_data['email']} already exists")
                return existing_user
            
            # Check if user exists by provider and provider_id
            if user_data.get("provider") and user_data.get("provider_id"):
                existing_user = self.get_user_by_provider(user_data["provider"], user_data["provider_id"])
                if existing_user:
                    logger.warning(f"User with provider {user_data['provider']}:{user_data['provider_id']} already exists")
                    return existing_user
            
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                timezone=user_data.get("timezone", "UTC"),
                preferences=user_data.get("preferences", {}),
                provider=user_data.get("provider"),
                provider_id=user_data.get("provider_id"),
                avatar_url=user_data.get("avatar_url")
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created user {user.id} with email {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def create_user_from_model(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user from UserCreate model (legacy method)"""
        db = self._get_db()
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning(f"User with email {user_data.email} already exists")
                return existing_user
            
            user = User(
                email=user_data.email,
                name=user_data.name,
                timezone=user_data.timezone,
                preferences=user_data.preferences or {},
                provider=user_data.provider,
                provider_id=user_data.provider_id,
                avatar_url=user_data.avatar_url
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created user {user.id} with email {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        db = self._get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return None
            
            # Update fields if provided
            if user_data.name is not None:
                user.name = user_data.name
            if user_data.timezone is not None:
                user.timezone = user_data.timezone
            if user_data.preferences is not None:
                user.preferences = user_data.preferences
            if user_data.availability_patterns is not None:
                user.availability_patterns = user_data.availability_patterns
            if user_data.avatar_url is not None:
                user.avatar_url = user_data.avatar_url
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Updated user {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Optional[User]:
        """Update user preferences"""
        db = self._get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for preference update")
                return None
            
            # Merge with existing preferences
            current_preferences = user.preferences or {}
            current_preferences.update(preferences)
            user.preferences = current_preferences
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Updated preferences for user {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        db = self._get_db()
        try:
            return db.query(User).all()
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
        finally:
            db.close()
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user from database"""
        db = self._get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            db.delete(user)
            db.commit()
            
            logger.info(f"Deleted user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        """Get multiple users by their IDs"""
        db = self._get_db()
        try:
            return db.query(User).filter(User.id.in_(user_ids)).all()
        except Exception as e:
            logger.error(f"Error getting users by IDs {user_ids}: {str(e)}")
            return []
        finally:
            db.close() 