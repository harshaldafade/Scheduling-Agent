#!/usr/bin/env python3
"""
Migration script to add OAuth fields to User table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine, SessionLocal
import logging

logger = logging.getLogger(__name__)

def migrate_oauth_fields():
    """Add OAuth fields to User table"""
    try:
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Add provider column if it doesn't exist
            if 'provider' not in columns:
                logger.info("Adding provider column to users table")
                connection.execute(text("ALTER TABLE users ADD COLUMN provider VARCHAR"))
                logger.info("✅ Added provider column")
            else:
                logger.info("Provider column already exists")
            
            # Add provider_id column if it doesn't exist
            if 'provider_id' not in columns:
                logger.info("Adding provider_id column to users table")
                connection.execute(text("ALTER TABLE users ADD COLUMN provider_id VARCHAR"))
                logger.info("✅ Added provider_id column")
            else:
                logger.info("Provider_id column already exists")
            
            # Add avatar_url column if it doesn't exist
            if 'avatar_url' not in columns:
                logger.info("Adding avatar_url column to users table")
                connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
                logger.info("✅ Added avatar_url column")
            else:
                logger.info("Avatar_url column already exists")
            
            # Add access_token column if it doesn't exist
            if 'access_token' not in columns:
                logger.info("Adding access_token column to users table")
                connection.execute(text("ALTER TABLE users ADD COLUMN access_token VARCHAR"))
                logger.info("✅ Added access_token column")
            else:
                logger.info("Access_token column already exists")
            
            # Add refresh_token column if it doesn't exist
            if 'refresh_token' not in columns:
                logger.info("Adding refresh_token column to users table")
                connection.execute(text("ALTER TABLE users ADD COLUMN refresh_token VARCHAR"))
                logger.info("✅ Added refresh_token column")
            else:
                logger.info("Refresh_token column already exists")
            
            connection.commit()
            logger.info("🎉 OAuth migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    print("🔄 Starting OAuth fields migration...")
    migrate_oauth_fields()
    print("✅ Migration completed!") 