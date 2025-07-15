import pandas as pd
import os
from sqlmodel import Session
from data.database import engine
from data.models import Company, Product, User, ContentAsset, Metric
from uuid import UUID
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

def load_demo_data():
    """Load demo data from CSV files"""
    demo_path = os.path.join(os.path.dirname(__file__), "demo")
    
    with Session(engine) as session:
        # Check if data already exists
        existing_companies = session.query(Company).count()
        if existing_companies > 0:
            logger.info("Demo data already loaded, skipping...")
            return
            
        try:
            # Load companies
            if os.path.exists(os.path.join(demo_path, "companies.csv")):
                logger.info("Loading companies...")
                companies_df = pd.read_csv(os.path.join(demo_path, "companies.csv"))
                for _, row in companies_df.iterrows():
                    # Check if company already exists
                    if 'id' in row and pd.notna(row['id']):
                        existing = session.get(Company, UUID(row['id']))
                        if existing:
                            continue
                    
                    company = Company(
                        id=UUID(row['id']) if 'id' in row and pd.notna(row['id']) else None,
                        company_name=row.get('company_name'),
                        industry=row.get('industry'),
                        brand_voice=row.get('brand_voice'),
                        created_at=pd.to_datetime(row['created_at']) if 'created_at' in row and pd.notna(row['created_at']) else datetime.utcnow()
                    )
                    session.add(company)
                session.commit()
                logger.info(f"Loaded {len(companies_df)} companies")
            
            # Load products
            if os.path.exists(os.path.join(demo_path, "products.csv")):
                logger.info("Loading products...")
                products_df = pd.read_csv(os.path.join(demo_path, "products.csv"))
                for _, row in products_df.iterrows():
                    product = Product(
                        id=UUID(row['id']) if 'id' in row and pd.notna(row['id']) else None,
                        company_id=UUID(row['company_id']) if 'company_id' in row and pd.notna(row['company_id']) else None,
                        product_name=row.get('product_name'),
                        description=row.get('description'),
                        launch_date=pd.to_datetime(row['launch_date']).date() if 'launch_date' in row and pd.notna(row['launch_date']) else None,
                        target_skin_type=row.get('target_skin_type')
                    )
                    session.add(product)
                session.commit()
                logger.info(f"Loaded {len(products_df)} products")
            
            # Load users
            if os.path.exists(os.path.join(demo_path, "users.csv")):
                logger.info("Loading users...")
                users_df = pd.read_csv(os.path.join(demo_path, "users.csv"))
                for _, row in users_df.iterrows():
                    user = User(
                        id=str(row['id']),
                        age=int(row['age']) if pd.notna(row.get('age')) else None,
                        location=row.get('location'),
                        skin_type=row.get('skin_type'),
                        channels_engaged=row.get('channels_engaged'),
                        purchase_history=row.get('purchase_history')
                    )
                    session.add(user)
                session.commit()
                logger.info(f"Loaded {len(users_df)} users")
            
            # Load content assets
            if os.path.exists(os.path.join(demo_path, "content_assets.csv")):
                logger.info("Loading content assets...")
                assets_df = pd.read_csv(os.path.join(demo_path, "content_assets.csv"))
                if not assets_df.empty:
                    for _, row in assets_df.iterrows():
                        asset = ContentAsset(
                            id=UUID(row['id']) if 'id' in row and pd.notna(row['id']) else None,
                            campaign_id=UUID(row['campaign_id']) if 'campaign_id' in row and pd.notna(row['campaign_id']) else None,
                            platform=row.get('platform'),
                            asset_type=row.get('asset_type'),
                            copy_text=row.get('copy_text'),
                            visual_url=row.get('visual_url'),
                            status=row.get('status', 'draft')
                        )
                        session.add(asset)
                    session.commit()
                    logger.info(f"Loaded {len(assets_df)} content assets")
            
            # Load metrics
            if os.path.exists(os.path.join(demo_path, "metrics.csv")):
                logger.info("Loading metrics...")
                metrics_df = pd.read_csv(os.path.join(demo_path, "metrics.csv"))
                if not metrics_df.empty:
                    for _, row in metrics_df.iterrows():
                        metric = Metric(
                            id=UUID(row['id']) if 'id' in row and pd.notna(row['id']) else None,
                            campaign_id=UUID(row['campaign_id']) if 'campaign_id' in row and pd.notna(row['campaign_id']) else None,
                            platform=row.get('platform'),
                            clicks=int(row['clicks']) if pd.notna(row.get('clicks')) else 0,
                            impressions=int(row['impressions']) if pd.notna(row.get('impressions')) else 0,
                            engagement_rate=float(row['engagement_rate']) if pd.notna(row.get('engagement_rate')) else 0.0,
                            conversion_rate=float(row['conversion_rate']) if pd.notna(row.get('conversion_rate')) else 0.0,
                            cpa=float(row['cpa']) if pd.notna(row.get('cpa')) else 0.0,
                            timestamp=pd.to_datetime(row['timestamp']) if 'timestamp' in row and pd.notna(row['timestamp']) else datetime.utcnow()
                        )
                        session.add(metric)
                    session.commit()
                    logger.info(f"Loaded {len(metrics_df)} metrics")
            
            # NOTE: Not loading any SetupConfiguration to ensure wizard runs
            logger.info("Demo data loaded successfully (no setup configuration)")
            
        except Exception as e:
            logger.error(f"Error loading demo data: {str(e)}")
            session.rollback()
            raise

# Create demo CSV files if they don't exist
def create_demo_files():
    """Create sample demo CSV files"""
    demo_path = os.path.join(os.path.dirname(__file__), "demo")
    os.makedirs(demo_path, exist_ok=True)
    
    # Sample companies
    companies_data = {
        'id': ['550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002'],
        'company_name': ['Glow Beauty Inc.', 'Natural Skincare Co.'],
        'industry': ['Beauty & Cosmetics', 'Beauty & Cosmetics'],
        'brand_voice': ['Modern, inclusive, empowering', 'Natural, sustainable, caring'],
        'created_at': ['2024-01-01 00:00:00', '2024-01-01 00:00:00']
    }
    pd.DataFrame(companies_data).to_csv(os.path.join(demo_path, "companies.csv"), index=False)
    
    # Sample products
    products_data = {
        'id': ['650e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440002'],
        'company_id': ['550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002'],
        'product_name': ['Radiant Glow Serum', 'Pure Cleanse Face Wash'],
        'description': ['Vitamin C serum for brightening', 'Gentle daily cleanser'],
        'launch_date': ['2024-03-01', '2024-02-15'],
        'target_skin_type': ['All skin types', 'Sensitive skin']
    }
    pd.DataFrame(products_data).to_csv(os.path.join(demo_path, "products.csv"), index=False)
    
    # Sample users
    users_data = {
        'id': ['user001', 'user002', 'user003'],
        'age': [25, 32, 28],
        'location': ['New York, NY', 'Los Angeles, CA', 'Chicago, IL'],
        'skin_type': ['Oily', 'Dry', 'Combination'],
        'channels_engaged': ['["facebook", "email"]', '["google", "email"]', '["facebook", "google", "email"]'],
        'purchase_history': ['[{"product": "serum", "date": "2024-01-15"}]', '[]', '[{"product": "cleanser", "date": "2024-02-01"}]']
    }
    pd.DataFrame(users_data).to_csv(os.path.join(demo_path, "users.csv"), index=False)
    
    # Empty content assets and metrics files
    pd.DataFrame(columns=['id', 'campaign_id', 'platform', 'asset_type', 'copy_text', 'visual_url', 'status']).to_csv(
        os.path.join(demo_path, "content_assets.csv"), index=False
    )
    
    pd.DataFrame(columns=['id', 'campaign_id', 'platform', 'clicks', 'impressions', 'engagement_rate', 'conversion_rate', 'cpa', 'timestamp']).to_csv(
        os.path.join(demo_path, "metrics.csv"), index=False
    )

if __name__ == "__main__":
    create_demo_files()
    load_demo_data()