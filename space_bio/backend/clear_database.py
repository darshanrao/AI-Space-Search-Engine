#!/usr/bin/env python3
"""
Script to clear all records from the Supabase database.
Use with caution - this will delete all data!
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db import async_sessionmaker

async def clear_database():
    """Clear all records from the database."""
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print("Tables to be cleared: threads, messages")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("Operation cancelled.")
        return
    
    async with async_sessionmaker() as session:
        try:
            print("Clearing messages table...")
            await session.execute(text("DELETE FROM messages"))
            
            print("Clearing threads table...")
            await session.execute(text("DELETE FROM threads"))
            
            await session.commit()
            print("✅ Database cleared successfully!")
            
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(clear_database())
