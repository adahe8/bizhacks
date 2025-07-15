
# backend/agents/segmentation_agent.py

from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any, Union
import json
import logging
import os
import traceback
import uuid
from uuid import UUID

from backend.core.config import settings
from backend.services.clustering_service import ClusteringService

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def ensure_uuid(value: Union[str, UUID]) -> UUID:
    """Convert string to UUID if needed"""
    if isinstance(value, str):
        return UUID(value)
    return value

def ensure_str(value: Union[str, UUID]) -> str:
    """Convert UUID to string if needed"""
    if isinstance(value, UUID):
        return str(value)
    return value

def create_naming_agent() -> Agent:
    """Create an agent for naming customer segments"""
    logger.debug("Creating naming agent...")
    
    # Check if API key is configured
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        error_msg = (
            "GEMINI_API_KEY not configured. Please set GEMINI_API_KEY in your .env file. "
            "Get your API key from https://makersuite.google.com/app/apikey"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        logger.debug(f"Initializing ChatGoogleGenerativeAI with API key: {settings.GEMINI_API_KEY[:10]}...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
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
        
        logger.info("Successfully created naming agent")
        return agent
    except Exception as e:
        logger.error(f"Failed to create naming agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def generate_customer_segments(
    product_id: Union[str, UUID],
    market_details: Dict[str, Any],
    strategic_goals: str
) -> List[Dict[str, Any]]:
    """Generate customer segments using clustering and AI naming"""
    logger.info("=== Starting generate_customer_segments ===")
    
    # Ensure product_id is a UUID
    product_uuid = ensure_uuid(product_id)
    product_id_str = ensure_str(product_uuid)
    
    logger.info(f"Product ID (UUID): {product_uuid}")
    logger.info(f"Product ID (str): {product_id_str}")
    logger.info(f"Market details: {market_details}")
    logger.info(f"Strategic goals: {strategic_goals}")
    
    try:
        # First, perform k-means clustering
        logger.info("Step 1: Starting k-means clustering...")
        clustering_service = ClusteringService()
        clusters_data = await clustering_service.perform_clustering()
        
        if not clusters_data:
            logger.error("No clusters generated - check if users data is loaded")
            logger.info("Checking user count in database...")
            
            from sqlmodel import Session, select
            from data.database import engine
            from data.models import User
            
            with Session(engine) as session:
                user_count = session.query(User).count()
                logger.info(f"Found {user_count} users in database")
                if user_count == 0:
                    logger.error("No users found in database! Please load demo data.")
                elif user_count < settings.NUM_CLUSTERS:
                    logger.error(f"Not enough users ({user_count}) for {settings.NUM_CLUSTERS} clusters")
            
            return []
        
        logger.info(f"Successfully generated {len(clusters_data)} clusters")
        for i, cluster in enumerate(clusters_data):
            logger.debug(f"Cluster {i}: Size={cluster['size']}%, Channels={cluster['channel_distribution']}")
        
        # Get product info for context
        logger.info("Step 2: Fetching product information...")
        from sqlmodel import Session
        from data.database import engine
        from data.models import Product
        
        with Session(engine) as session:
            # Use UUID object for database query
            product = session.get(Product, product_uuid)
            if not product:
                logger.error(f"Product not found with ID: {product_uuid}")
                raise ValueError("Product not found")
            
            logger.info(f"Product: {product.product_name} - {product.description}")
        
        # Try to create naming agent and generate names
        segment_names = []
        try:
            logger.info("Step 3: Creating AI naming agent...")
            # Create naming agent
            agent = create_naming_agent()
            
            logger.info("Step 4: Generating segment names with AI...")
            # Create naming task
            task_description = f"""
            Based on the following customer clusters, create memorable names and descriptions for each segment.

            Product: {product.product_name} - {product.description}
            Market Context: {json.dumps(market_details)}
            Strategic Goals: {strategic_goals}

            Clusters Data:
            {json.dumps(clusters_data, indent=2)}

            For each cluster, provide:
            1. A UNIQUE catchy, memorable name (2-3 words max) - Each name MUST be different
            2. A brief description (1-2 sentences) that captures their key characteristics

            Focus on:
            - Age demographics
            - Channel preferences (Email, Facebook, Google)
            - PURCHASE BEHAVIOR (average purchases, high vs low purchasers)
            - Location patterns
            - Skin type (if relevant)

            IMPORTANT: All {len(clusters_data)} segment names must be completely unique and different from each other.

            Return as JSON array with objects containing: cluster_id, name, description

            Example format:
            [
                {{"cluster_id": 0, "name": "Digital Natives", "description": "Young, tech-savvy customers who engage across all channels with high purchase frequency."}},
                {{"cluster_id": 1, "name": "Email Loyalists", "description": "Mature customers who prefer email communication and have moderate purchase activity."}},
                {{"cluster_id": 2, "name": "Social Browsers", "description": "Facebook-focused users with low purchase history, primarily window shopping."}}
            ]
            """
            
            task = Task(
                description=task_description,
                agent=agent,
                expected_output="JSON array of segment names and descriptions"
            )
            
            logger.debug("Executing naming task...")
            # Execute task
            result = task.execute()
            logger.debug(f"AI Agent response: {result}")
            
            # Parse the result
            segment_names = json.loads(result)
            # Ensure unique names
            segment_names = ensure_unique_segment_names(segment_names)
            logger.info(f"Successfully generated {len(segment_names)} unique AI segment names")
            for name in segment_names:
                logger.debug(f"Segment {name['cluster_id']}: {name['name']} - {name['description']}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI-generated segment names: {str(e)}")
            logger.error(f"Raw result: {result if 'result' in locals() else 'No result'}")
            segment_names = []
        except Exception as e:
            logger.error(f"Error generating segment names with AI: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.info("Falling back to default segment names")
            segment_names = []
        
        # If AI naming failed, use default names
        if not segment_names:
            logger.info("Using default segment naming...")
            segment_names = generate_default_segment_names(clusters_data)
            logger.info(f"Generated {len(segment_names)} default segment names")
        
        # Save clusters with names
        logger.info("Step 5: Saving segments to database...")
        saved_segments = await clustering_service.save_clusters(clusters_data, segment_names)
        logger.info(f"Successfully saved {len(saved_segments)} segments to database")
        
        # Format response - ensure all IDs are strings for JSON serialization
        segments = []
        for segment in saved_segments:
            segment_data = {
                "id": ensure_str(segment.id),
                "name": segment.name,
                "description": segment.description,
                "size": segment.size,
                "channel_distribution": json.loads(segment.channel_distribution) if segment.channel_distribution else {},
                "criteria": json.loads(segment.criteria) if segment.criteria else {}
            }
            segments.append(segment_data)
            logger.debug(f"Formatted segment: {segment_data['name']} (ID: {segment_data['id']})")
        
        logger.info(f"=== Completed generate_customer_segments: Generated {len(segments)} segments ===")
        return segments
        
    except Exception as e:
        logger.error(f"Fatal error in generate_customer_segments: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

def generate_default_segment_names(clusters_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Generate default segment names based on cluster characteristics"""
    logger.debug("Generating default segment names...")
    default_names = []
    
    # Pre-define unique name patterns to avoid duplicates
    name_patterns = [
        ("Premium", "High-Value"),
        ("Engaged", "Active"),
        ("Potential", "Emerging")
    ]
    
    for i, cluster in enumerate(clusters_data):
        characteristics = cluster.get("characteristics", {})
        channel_dist = cluster.get("channel_distribution", {})
        
        # Determine purchase level
        avg_purchases = characteristics.get("avg_purchases", 0)
        if avg_purchases >= 2:
            purchase_level = "Frequent Buyers"
        elif avg_purchases >= 1:
            purchase_level = "Regular Shoppers"
        else:
            purchase_level = "New Prospects"
        
        # Determine primary channel
        primary_channel = max(channel_dist.items(), key=lambda x: x[1])[0] if channel_dist else "multi"
        channel_name = {
            "email": "Email",
            "facebook": "Social",
            "google_seo": "Search",
            "multi": "Multi-Channel"
        }.get(primary_channel, "Digital")
        
        # Use pattern to ensure uniqueness
        pattern = name_patterns[i % len(name_patterns)]
        name = f"{pattern[0]} {channel_name} {purchase_level}"
        
        description = f"Customers aged {characteristics.get('age_range', 'various')} who primarily engage via {primary_channel}. "
        description += f"Average {avg_purchases:.1f} purchases per user, with {characteristics.get('high_purchasers_pct', 0)}% being frequent buyers."
        
        default_names.append({
            "cluster_id": i,
            "name": name,
            "description": description
        })
        
        logger.debug(f"Default name for cluster {i}: {name}")
    
    return default_names

def ensure_unique_segment_names(segment_names: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure all segment names are unique by appending numbers if needed"""
    seen_names = {}
    unique_names = []
    
    for segment in segment_names:
        base_name = segment.get("name", f"Segment {segment.get('cluster_id', 0) + 1}")
        
        if base_name in seen_names:
            seen_names[base_name] += 1
            unique_name = f"{base_name} {seen_names[base_name]}"
        else:
            seen_names[base_name] = 1
            unique_name = base_name
        
        unique_names.append({
            **segment,
            "name": unique_name
        })
    
    return unique_names