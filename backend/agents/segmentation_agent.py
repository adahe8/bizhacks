from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import json
import logging

from core.config import settings
from services.clustering_service import ClusteringService

logger = logging.getLogger(__name__)

def create_naming_agent() -> Agent:
    """Create an agent for naming customer segments"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7
    )
    
    agent = Agent(
        role="Customer Segment Naming Specialist",
        goal="Create memorable and descriptive names for customer segments based on their characteristics",
        backstory="""You are an expert in marketing and customer analytics.
        You excel at creating catchy, descriptive names that capture the essence
        of customer segments and make them easy to remember and discuss.""",
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
    """Generate customer segments using clustering and AI naming"""
    
    # First, perform k-means clustering
    clustering_service = ClusteringService()
    clusters_data = await clustering_service.perform_clustering()
    
    if not clusters_data:
        logger.error("No clusters generated")
        return []
    
    # Get product info for context
    from sqlmodel import Session
    from data.database import engine
    from data.models import Product
    
    with Session(engine) as session:
        product = session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
    
    # Create naming agent
    agent = create_naming_agent()
    
    # Create naming task
    task = Task(
        description=f"""
        Based on the following customer clusters, create memorable names and descriptions for each segment.
        
        Product: {product.product_name} - {product.description}
        Market Context: {json.dumps(market_details)}
        Strategic Goals: {strategic_goals}
        
        Clusters Data:
        {json.dumps(clusters_data, indent=2)}
        
        For each cluster, provide:
        1. A catchy, memorable name (2-3 words max)
        2. A brief description (1-2 sentences) that captures their key characteristics
        
        Focus on:
        - Age demographics
        - Channel preferences (Email, Facebook, Google)
        - Purchase behavior
        - Location patterns
        - Skin type (if relevant)
        
        Return as JSON array with objects containing: cluster_id, name, description
        """,
        agent=agent,
        expected_output="JSON array of segment names and descriptions"
    )
    
    # Execute task
    result = task.execute()
    
    try:
        # Parse the result
        segment_names = json.loads(result)
        
        # Save clusters with names
        saved_segments = await clustering_service.save_clusters(clusters_data, segment_names)
        
        # Format response
        segments = []
        for segment in saved_segments:
            segments.append({
                "id": str(segment.id),
                "name": segment.name,
                "description": segment.description,
                "size": segment.size,
                "channel_distribution": json.loads(segment.channel_distribution) if segment.channel_distribution else {},
                "criteria": json.loads(segment.criteria) if segment.criteria else {}
            })
        
        logger.info(f"Generated and saved {len(segments)} customer segments")
        return segments
        
    except json.JSONDecodeError:
        logger.error("Failed to parse segment names")
        # Fallback: save with default names
        default_names = [
            {"cluster_id": i, "name": f"Segment {i+1}", "description": f"Customer segment {i+1}"}
            for i in range(len(clusters_data))
        ]
        saved_segments = await clustering_service.save_clusters(clusters_data, default_names)
        
        return [{
            "id": str(seg.id),
            "name": seg.name,
            "description": seg.description,
            "size": seg.size,
            "channel_distribution": json.loads(seg.channel_distribution) if seg.channel_distribution else {},
            "criteria": json.loads(seg.criteria) if seg.criteria else {}
        } for seg in saved_segments]