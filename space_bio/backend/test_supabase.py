#!/usr/bin/env python3
"""
Test script to verify Supabase database connection and functionality.
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import async_sessionmaker
from models import Thread, Message

async def test_supabase_connection():
    """Test Supabase database connection and basic operations."""
    print("Testing Supabase database connection...")
    
    async with async_sessionmaker() as session:
        try:
            # Test 1: Create a thread
            print("\n1. Testing thread creation...")
            thread_id = str(uuid.uuid4())
            thread = Thread(
                id=thread_id,
                title="Test Thread",
                context={"test": "data"}
            )
            session.add(thread)
            await session.commit()
            await session.refresh(thread)
            print(f"SUCCESS: Thread created: {thread_id}")
            
            # Test 2: Create messages
            print("\n2. Testing message creation...")
            user_message = Message(
                id=str(uuid.uuid4()),
                thread_id=thread_id,
                role="user",
                content="What is space biology?",
                meta={}
            )
            assistant_message = Message(
                id=str(uuid.uuid4()),
                thread_id=thread_id,
                role="assistant",
                content="Space biology is the study of how living organisms are affected by space conditions.",
                meta={}
            )
            
            session.add(user_message)
            session.add(assistant_message)
            await session.commit()
            print("SUCCESS: Messages created successfully")
            
            # Test 3: Query thread with messages
            print("\n3. Testing thread retrieval...")
            stmt = select(Thread).where(Thread.id == thread_id)
            result = await session.execute(stmt)
            retrieved_thread = result.scalar_one_or_none()
            
            if retrieved_thread:
                print(f"SUCCESS: Thread retrieved: {retrieved_thread.title}")
                print(f"   Context: {retrieved_thread.context}")
                print(f"   Created: {retrieved_thread.created_at}")
            else:
                print("ERROR: Thread not found")
                return False
            
            # Test 4: Query messages
            print("\n4. Testing message retrieval...")
            messages_stmt = select(Message).where(
                Message.thread_id == thread_id
            ).order_by(Message.created_at.asc())
            
            messages_result = await session.execute(messages_stmt)
            messages = messages_result.scalars().all()
            
            print(f"SUCCESS: Retrieved {len(messages)} messages:")
            for msg in messages:
                print(f"   {msg.role}: {msg.content[:50]}...")
            
            # Test 5: Clean up
            print("\n5. Cleaning up test data...")
            await session.delete(retrieved_thread)  # This will cascade delete messages
            await session.commit()
            print("SUCCESS: Test data cleaned up")
            
            return True
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            await session.rollback()
            return False

async def test_conversation_flow():
    """Test a complete conversation flow."""
    print("\n" + "="*50)
    print("Testing complete conversation flow...")
    
    async with async_sessionmaker() as session:
        try:
            # Create thread
            thread_id = str(uuid.uuid4())
            thread = Thread(
                id=thread_id,
                title="Space Biology Conversation",
                context={"organism": "human", "conditions": ["microgravity"]}
            )
            session.add(thread)
            await session.commit()
            await session.refresh(thread)
            
            # Simulate conversation
            conversation = [
                ("user", "What is space biology?"),
                ("assistant", "Space biology is the study of how living organisms are affected by and adapt to the unique environmental conditions of space."),
                ("user", "How does microgravity affect humans?"),
                ("assistant", "Microgravity affects humans in several ways, including muscle atrophy, bone density loss, and fluid redistribution."),
                ("user", "What about radiation exposure?"),
                ("assistant", "Radiation exposure in space is a major concern, as astronauts are exposed to galactic cosmic rays and solar particle events.")
            ]
            
            for role, content in conversation:
                message = Message(
                    id=str(uuid.uuid4()),
                    thread_id=thread_id,
                    role=role,
                    content=content,
                    meta={}
                )
                session.add(message)
            
            await session.commit()
            print("SUCCESS: Conversation stored successfully")
            
            # Retrieve and display conversation
            messages_stmt = select(Message).where(
                Message.thread_id == thread_id
            ).order_by(Message.created_at.asc())
            
            messages_result = await session.execute(messages_stmt)
            messages = messages_result.scalars().all()
            
            print(f"\nConversation History ({len(messages)} messages):")
            for i, msg in enumerate(messages, 1):
                print(f"{i}. {msg.role.upper()}: {msg.content}")
            
            # Clean up
            await session.delete(thread)
            await session.commit()
            print("\nSUCCESS: Conversation test completed and cleaned up")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Conversation test failed: {str(e)}")
            await session.rollback()
            return False

async def main():
    """Run all tests."""
    print("Starting Supabase Database Tests")
    print("="*50)
    
    # Test basic connection
    basic_test = await test_supabase_connection()
    
    if basic_test:
        # Test conversation flow
        conversation_test = await test_conversation_flow()
        
        if conversation_test:
            print("\nSUCCESS: All tests passed! Supabase is working correctly.")
            print("\nYour chatbot can now:")
            print("   - Store conversation threads")
            print("   - Save user and assistant messages")
            print("   - Retrieve conversation history")
            print("   - Support follow-up questions")
        else:
            print("\nERROR: Conversation flow test failed!")
    else:
        print("\nERROR: Basic connection test failed!")
        print("Please check your Supabase configuration.")

if __name__ == "__main__":
    asyncio.run(main())
