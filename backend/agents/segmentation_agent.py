from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import json
import logging

from core.config import settings

logger = logging.getLogger(__name__)

def create_segmentation_agent(
    product_info: Dict[str, Any],
    market_details: Dict[str, Any],
    user_data: List[Dict[str, Any]]
) -> Agent:
    """Create an agent for customer segmentation"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7
    )
    
    agent = Agent(
        role="Customer Segmentation Specialist",
        goal="Analyze user data and market information to create meaningful customer segments",
        backstory="""You are an expert in customer analytics and market segmentation.
        You excel at identifying patterns in customer behavior and creating actionable
        segments that drive marketing effectiveness.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return agent

async def generate_customer_segments(
    product_id: str,
    market_details: Dict[str, Any],
    strategic_goals: str
) -> List[Dict[str, Any]]:
    """Generate customer segments based on product and market data"""
    
    # In a real implementation, this would analyze actual user data
    # For now, we'll use the agent to generate segments based on inputs
    
    from sqlmodel import Session, select
    from data.database import engine
    from data.models import Product, User
    
    with Session(engine) as session:
        # Get product info
        product = session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        
        # Get sample users
        users = session.exec(select(User).limit(100)).all()
        user_data = [
            {
                "age": user.age,
                "location": user.location,
                "skin_type": user.skin_type,
                "channels": user.channels_engaged_list,
                "purchase_history": user.purchase_history_list
            }
            for user in users
        ]
    
    # Create agent
    agent = create_segmentation_agent(
        product_info={
            "name": product.product_name,
            "description": product.description,
            "target_skin_type": product.target_skin_type
        },
        market_details=market_details,
        user_data=user_data
    )
    
    # Create segmentation task
    task = Task(
        description=f"""
        Analyze the provided user data and create customer segments for {product.product_name}.
        
        Product Information:
        - Name: {product.product_name}
        - Description: {product.description}
        - Target Skin Type: {product.target_skin_type}
        
        Market Details: {json.dumps(market_details)}
        
        Strategic Goals: {strategic_goals}
        
        Based on the user data patterns, create 3-5 distinct customer segments.
        For each segment, provide:
        1. Segment name
        2. Description (2-3 sentences)
        3. Key characteristics/criteria
        4. Estimated size (as percentage of total market)
        5. Preferred channels
        6. Messaging recommendations
        
        Return the segments as a JSON array.
        """,
        agent=agent,
        expected_output="JSON array of customer segments"
    )
    
    # Execute task
    result = task.execute()
    
    try:
        # Parse the result
        segments_data = json.loads(result)
        
        # Format segments
        segments = []
        for seg in segments_data:
            segments.append({
                "name": seg.get("name", ""),
                "description": seg.get("description", ""),
                "criteria": seg.get("characteristics", {}),
                "size": seg.get("size", 0),
                "channels": seg.get("preferred_channels", []),
                "messaging": seg.get("messaging_recommendations", "")
            })
        
        logger.info(f"Generated {len(segments)} customer segments")
        return segments
        
    except json.JSONDecodeError:
        logger.error("Failed to parse segmentation results")
        # Return default segments
        return [
            {
                "name": "Young Professionals",
                "description": "Urban professionals aged 25-35 focused on convenient, effective skincare",
                "criteria": {"age_range": "25-35", "location": "urban", "income": "medium-high"},
                "size": 35,
                "channels": ["email", "facebook"],
                "messaging": "Emphasize time-saving and professional appearance"
            },
            {
                "name": "Eco-Conscious Consumers",
                "description": "Environmentally aware customers seeking natural, sustainable products",
                "criteria": {"interests": ["sustainability", "natural"], "values": "eco-friendly"},
                "size": 25,
                "channels": ["email", "google_seo"],
                "messaging": "Highlight natural ingredients and sustainable practices"
            },
            {
                "name": "Mature Skin Care",
                "description": "Customers 45+ looking for anti-aging and restorative solutions",
                "criteria": {"age_range": "45+", "concerns": ["anti-aging", "restoration"]},
                "size": 40,
                "channels": ["facebook", "email"],
                "messaging": "Focus on proven results and skin restoration"
            }
        ]