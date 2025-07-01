#!/usr/bin/env python3
"""
Database migration script to add security fields to the user table.
Run this script to update the database schema with new security features.
"""

import sqlite3
import os
from datetime import datetime

def migrate_security_fields():
    """Add security fields to the user table"""
    
    # Database file path
    db_path = "scheduling_agent.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Creating new database...")
        conn = sqlite3.connect(db_path)
        conn.close()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if security fields already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add security fields if they don't exist
        if "last_login" not in columns:
            print("Adding last_login column...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
        
        if "failed_login_attempts" not in columns:
            print("Adding failed_login_attempts column...")
            cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
        
        if "locked_until" not in columns:
            print("Adding locked_until column...")
            cursor.execute("ALTER TABLE users ADD COLUMN locked_until DATETIME")
        
        if "refresh_token" not in columns:
            print("Adding refresh_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN refresh_token TEXT")
        
        # Commit changes
        conn.commit()
        print("Security fields migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(users)")
        print("\nUpdated table structure:")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]})")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting security fields migration...")
    migrate_security_fields()
    print("Migration completed!") 