from sqlmodel import create_engine, SQLModel, Session
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from data.models import (
            Company, Product, User, Campaign, ContentAsset,
            Metric, CustomerSegment, Schedule, SetupConfiguration,
            Transaction
        )
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        # Load demo data if database is empty
        with Session(engine) as session:
            company_count = session.query(Company).count()
            if company_count == 0:
                logger.info("Database is empty, loading demo data...")
                from data.demo_loader import load_demo_data
                load_demo_data()
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session