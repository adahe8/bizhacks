# scripts/check_segments.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from data.database import engine
from data.models import CustomerSegment, User, SetupConfiguration
import asyncio
from backend.agents.segmentation_agent import generate_customer_segments
import logging

# Configure logging to see all output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_and_generate_segments():
    """Check current segments and try to generate new ones"""
    
    with Session(engine) as session:
        # Check existing segments
        segments = session.exec(select(CustomerSegment)).all()
        print(f"\n=== Current Segments: {len(segments)} ===")
        for seg in segments:
            print(f"- {seg.name}: {seg.size}% of users")
        
        # Check users
        users = session.exec(select(User)).all()
        print(f"\n=== Total Users: {len(users)} ===")
        
        if len(users) < 4:
            print("ERROR: Not enough users for clustering (need at least 4)")
            return
        
        # Check setup configuration
        setup = session.exec(select(SetupConfiguration).where(SetupConfiguration.is_active == True)).first()
        if not setup:
            print("ERROR: No active setup configuration found")
            return
        
        print(f"\n=== Setup Configuration ===")
        print(f"Product ID: {setup.product_id}")
        print(f"Company ID: {setup.company_id}")
        
        # Check environment
        gemini_key = os.getenv("GEMINI_API_KEY", "NOT_SET")
        print(f"\n=== API Configuration ===")
        print(f"GEMINI_API_KEY: {'SET' if gemini_key != 'NOT_SET' and gemini_key != 'your-gemini-api-key-here' else 'NOT SET'}")
        
        if segments:
            response = input("\nSegments already exist. Regenerate? (y/n): ")
            if response.lower() != 'y':
                return
        
        print("\n=== Generating Customer Segments ===")
        try:
            # Import here to avoid circular imports
            import json
            market_details = json.loads(setup.market_details) if setup.market_details else {}
            
            new_segments = await generate_customer_segments(
                product_id=str(setup.product_id),
                market_details=market_details,
                strategic_goals=setup.strategic_goals or ""
            )
            
            print(f"\n=== Generated {len(new_segments)} segments ===")
            for seg in new_segments:
                print(f"- {seg['name']}: {seg['size']}%")
                print(f"  {seg['description']}")
                
        except Exception as e:
            print(f"\nERROR generating segments: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_generate_segments())