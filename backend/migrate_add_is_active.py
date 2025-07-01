#!/usr/bin/env python3
"""
Migration script to add is_active field to users table
"""
import sqlite3
import os
from pathlib import Path

def migrate_add_is_active():
    """Add is_active column to users table"""
    db_path = Path("scheduling_agent.db")
    
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if is_active column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_active' not in columns:
            print("Adding is_active column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            conn.commit()
            print("Successfully added is_active column")
        else:
            print("is_active column already exists")
        
        conn.close()
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_add_is_active() 