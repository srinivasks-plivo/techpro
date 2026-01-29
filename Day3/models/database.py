"""
Database connection and setup.

This file handles:
1. Creating the database engine (the connection pool)
2. Creating the session factory (for making database queries)
3. Defining the Base model (all our models inherit from this)

Think of it like this:
- Engine = The connection to the database (like opening a door)
- Session = A conversation with the database (like talking through that door)
- Base = A template that all tables follow
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_config

# Get configuration settings
config = get_config()

# ===== CREATE ENGINE =====
# The engine is a connection pool to PostgreSQL
# pool_pre_ping=True: Before using a connection, ping it to make sure it's alive
#                      This prevents "connection lost" errors
engine = create_engine(
    config.DATABASE_URL,
    echo=config.FLASK_DEBUG,  # Print SQL queries to console if in debug mode
    pool_pre_ping=True,        # Check connection is alive before using it
    pool_size=10,              # Keep 10 connections ready
    max_overflow=20            # Allow up to 20 extra connections if needed
)

# ===== CREATE SESSION FACTORY =====
# SessionLocal() creates a new session each time it's called
# A session is like a conversation with the database
# You make queries within a session, then close it
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit (we control when to save)
    autoflush=False,   # Don't auto-flush (we control when to send queries)
    bind=engine        # Use our engine for connections
)

# ===== CREATE BASE MODEL =====
# All our database models (tables) will inherit from Base
# This is like a template - SQLAlchemy uses it to know how to create tables
Base = declarative_base()


def get_db():
    """
    Dependency function to get a database session.

    Usage:
        def my_route():
            db = get_db()
            users = db.query(User).all()
            db.close()

    This is a generator function - it:
    1. Creates a session
    2. Yields (gives) the session to the caller
    3. Closes the session when done

    Why use try/finally? To ensure the session is ALWAYS closed,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to the caller
    finally:
        db.close()  # Always close, even if error occurred


def init_db():
    """
    Initialize the database by creating all tables.

    Call this once at startup to create all tables defined by our models.

    Usage:
        from models.database import init_db
        init_db()
    """
    print("Creating database tables...")

    # Create all tables that inherit from Base
    Base.metadata.create_all(bind=engine)

    print("✓ Database tables created successfully!")


def drop_all_tables():
    """
    Drop all tables. Use this only for development/testing!

    WARNING: This deletes all data! Use carefully.

    Usage:
        from models.database import drop_all_tables
        drop_all_tables()  # Careful!
    """
    print("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")
