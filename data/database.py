from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager
import os

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///campaign.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Set to False in production
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()