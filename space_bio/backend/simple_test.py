#!/usr/bin/env python3
"""
Simple test to create a thread directly and see the exact error.
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import async_sessionmaker
from models import Thread

async def test_thread_creation():
    """Test thread creation directly."""
    print("Testing thread creation directly...")
    
    async with async_sessionmaker() as session:
        try:
            # Create thread
            thread_id = str(uuid.uuid4())
            thread = Thread(
                id=thread_id,
                title="Test Thread",
                context={"test": "data"}
            )
            
            print(f"Created thread object: {thread}")
            session.add(thread)
            print("Added thread to session")
            
            await session.commit()
            print("Committed to database")
            
            await session.refresh(thread)
            print(f"Refreshed thread: {thread}")
            
            # Try to retrieve it
            stmt = select(Thread).where(Thread.id == thread_id)
            result = await session.execute(stmt)
            retrieved_thread = result.scalar_one_or_none()
            
            if retrieved_thread:
                print(f"SUCCESS: Retrieved thread: {retrieved_thread.title}")
                return True
            else:
                print("ERROR: Thread not found after creation")
                return False
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return False

if __name__ == "__main__":
    result = asyncio.run(test_thread_creation())
    if result:
        print("\nSUCCESS: Thread creation works!")
    else:
        print("\nERROR: Thread creation failed!")
