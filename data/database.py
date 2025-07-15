# backend/data/database.py
from sqlmodel import create_engine, SQLModel, Session, text
from backend.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Ensure the directory for the database exists
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    # Skip directory creation for in-memory databases
    if not db_path.startswith(":memory:"):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def verify_tables():
    """Verify all required tables exist"""
    required_tables = [
        "companies",
        "products", 
        "users",
        "campaigns",
        "content_assets",
        "metrics",
        "customer_segments",
        "schedules",
        "setup_configurations",
        "transactions",
        "game_state",
        "campaign_metrics"
    ]
    
    with engine.connect() as conn:
        # Get existing tables
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        existing_tables = [row[0] for row in result]
        
        # Check for missing tables
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            logger.warning(f"Missing database tables: {missing_tables}")
            return False
        
        logger.info(f"All {len(required_tables)} required tables present")
        return True

def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from data.models import (
            Company, Product, User, Campaign, ContentAsset,
            Metric, CustomerSegment, Schedule, SetupConfiguration,
            Transaction, GameState, CampaignMetrics
        )
        
        # Check if database exists and has tables
        tables_exist = False
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table';"))
                table_count = result.scalar()
                tables_exist = table_count > 0
        except Exception:
            pass
        
        if tables_exist:
            # Database exists, verify all tables are present
            if not verify_tables():
                logger.info("Creating missing tables...")
                # Create only missing tables (SQLModel will skip existing ones)
                SQLModel.metadata.create_all(engine)
                verify_tables()  # Verify again
        else:
            # Create all tables from scratch
            logger.info("Creating all database tables...")
            SQLModel.metadata.create_all(engine)
            verify_tables()
        
        logger.info(f"Database initialized successfully at: {settings.DATABASE_URL}")
        
        # Load demo data if database is empty
        with Session(engine) as session:
            from data.models import Company
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