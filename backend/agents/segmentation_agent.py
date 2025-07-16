# backend/agents/segmentation_agent.py

from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
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

# Pydantic models for segmentation
class SegmentCharacteristics(BaseModel):
    """Characteristics of a customer segment"""
    age_range: str = Field(
        description="Age range of the segment (e.g., '25-34')"
    )
    primary_locations: List[str] = Field(
        description="Top 2-3 locations",
        min_items=1,
        max_items=3
    )
    purchase_behavior: str = Field(
        description="Purchase behavior pattern",
        pattern="^(high_frequency|moderate|low_frequency|non_purchaser)$"
    )
    average_purchase_value: float = Field(
        description="Average purchase value",
        ge=0
    )
    channel_preference: str = Field(
        description="Primary channel preference"
    )
    skin_type_distribution: Dict[str, float] = Field(
        description="Distribution of skin types in percentage",
        default={}
    )

class SegmentName(BaseModel):
    """Model for a segment name and description"""
    cluster_id: int = Field(
        description="Cluster ID (0-based index)",
        ge=0
    )
    name: str = Field(
        description="Unique, catchy segment name (2-3 words)",
        min_length=5,
        max_length=30
    )
    description: str = Field(
        description="Brief description of segment characteristics (1-2 sentences)",
        min_length=20,
        max_length=200
    )
    marketing_focus: str = Field(
        description="Key marketing focus for this segment",
        min_length=10,
        max_length=100
    )
    
    @validator('name')
    def validate_name_format(cls, v):
        words = v.split()
        if len(words) < 2 or len(words) > 4:
            raise ValueError("Segment name should be 2-4 words")
        return v

class SegmentNameList(BaseModel):
    """List of segment names"""
    segments: List[SegmentName] = Field(
        description="List of segment names and descriptions"
    )
    
    @validator('segments')
    def validate_unique_names(cls, v):
        names = [seg.name for seg in v]
        if len(names) != len(set(names)):
            # Find duplicates
            seen = set()
            duplicates = set()
            for name in names:
                if name in seen:
                    duplicates.add(name)
                seen.add(name)
            raise ValueError(f"All segment names must be unique. Duplicates found: {duplicates}")
        return v
    
    @validator('segments')
    def validate_cluster_ids(cls, v):
        cluster_ids = [seg.cluster_id for seg in v]
        expected_ids = list(range(len(v)))
        if sorted(cluster_ids) != expected_ids:
            raise ValueError(f"Cluster IDs must be sequential starting from 0. Got: {cluster_ids}")
        return v

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
            of customer segments and make them easy to remember and discuss.
            You always provide structured output following the SegmentNameList model.""",
            llm=llm,
            verbose=True,
            allow_delegation=False,
            output_pydantic=SegmentNameList
        )
        
        logger.info("Successfully created naming agent with pydantic validation")
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
            1. A UNIQUE catchy, memorable name (2-3 words) - Each name MUST be completely different
            2. A brief description (1-2 sentences) that captures their key characteristics
            3. A marketing focus - what's the key approach for this segment

            Focus on:
            - Age demographics
            - Channel preferences (Email, Facebook, Google)
            - PURCHASE BEHAVIOR (average purchases, high vs low purchasers)
            - Location patterns
            - Skin type (if relevant)

            Create {len(clusters_data)} segments with cluster_id from 0 to {len(clusters_data)-1}.
            ALL segment names must be completely unique and different from each other.

            Return the segments following the SegmentNameList model structure.
            """
            
            task = Task(
                description=task_description,
                agent=agent,
                expected_output="Structured list of segment names following SegmentNameList model",
                output_pydantic=SegmentNameList
            )
            
            logger.debug("Executing naming task...")
            # Execute task
            result = task.execute()
            
            # Extract segment names from result
            if isinstance(result, SegmentNameList):
                segment_names = [seg.dict() for seg in result.segments]
                logger.info(f"Successfully generated {len(segment_names)} unique AI segment names")
            else:
                # Try to parse as JSON
                parsed = json.loads(result) if isinstance(result, str) else result
                validated = SegmentNameList(segments=parsed['segments'])
                segment_names = [seg.dict() for seg in validated.segments]
            
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
        ("Premium Beauty", "High-value customers seeking premium skincare solutions"),
        ("Social Shoppers", "Engaged customers who discover products through social media"),
        ("Email Enthusiasts", "Loyal customers who prefer email communications and offers")
    ]
    
    for i, cluster in enumerate(clusters_data):
        if i < len(name_patterns):
            name, base_desc = name_patterns[i]
        else:
            name = f"Segment {i + 1}"
            base_desc = "Customer segment with unique characteristics"
        
        characteristics = cluster.get("characteristics", {})
        channel_dist = cluster.get("channel_distribution", {})
        
        # Determine primary channel
        primary_channel = max(channel_dist.items(), key=lambda x: x[1])[0] if channel_dist else "multi"
        
        # Build description
        avg_purchases = characteristics.get("avg_purchases", 0)
        description = f"{base_desc}. "
        description += f"Average {avg_purchases:.1f} purchases per customer."
        
        # Marketing focus
        if avg_purchases >= 2:
            marketing_focus = "Retention and upselling to maximize customer lifetime value"
        elif avg_purchases >= 1:
            marketing_focus = "Engagement campaigns to increase purchase frequency"
        else:
            marketing_focus = "Conversion-focused campaigns to drive first purchases"
        
        default_names.append({
            "cluster_id": i,
            "name": name,
            "description": description,
            "marketing_focus": marketing_focus
        })
        
        logger.debug(f"Default name for cluster {i}: {name}")
    
    return default_names