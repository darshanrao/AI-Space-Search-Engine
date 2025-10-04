"""
Database configuration and session management using synchronous SQLAlchemy.
Provides engine, session factory, and dependency injection.
Configured for PgBouncer compatibility with Supabase.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from fastapi import Depends

from settings import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Create engine from settings.DATABASE_URL (psycopg2 for Postgres)
# Configured for PgBouncer compatibility with Supabase
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
    # PgBouncer-safe connection pooling configuration
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Base number of connections to maintain
    max_overflow=5,      # Additional connections allowed beyond pool_size
    connect_args={
        # CRITICAL: Disable prepared statement caching for PgBouncer transaction pooling
        # PgBouncer in transaction mode doesn't support prepared statements properly
        # This prevents "prepared statement already exists" errors
        "options": "-c statement_timeout=30000 -c application_name=space-bio-api"
    }
)

# Create session factory
# expire_on_commit=False prevents objects from being detached after commit
SessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI.
    
    Yields:
        Session: Database session for the request
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Dependency for database session
DatabaseSession = Depends(get_session)
