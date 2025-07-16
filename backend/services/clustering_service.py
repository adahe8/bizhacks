# backend/services/clustering_service.py
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sqlmodel import Session, select
import json
import logging
from typing import List, Dict, Any
import traceback

from data.database import engine
from data.models import User, CustomerSegment
from backend.core.config import settings

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

class ClusteringService:
    """Service for customer segmentation using k-means clustering"""
    
    def __init__(self):
        self.n_clusters = settings.NUM_CLUSTERS
        self.random_state = settings.CLUSTER_RANDOM_STATE
        logger.info(f"Initialized ClusteringService with {self.n_clusters} clusters")
        
    def prepare_user_data(self, users: List[User]) -> tuple:
        """Prepare user data for clustering"""
        logger.debug(f"Preparing data for {len(users)} users...")
        
        # Convert users to dataframe
        data = []
        for user in users:
            try:
                channels = json.loads(user.channels_engaged) if user.channels_engaged else []
                purchase_history = json.loads(user.purchase_history) if user.purchase_history else []
                
                # Create binary features for channels
                has_email = 1 if "Email" in channels else 0
                has_facebook = 1 if "Facebook" in channels else 0
                has_google = 1 if "Google Ads SEO" in channels else 0
                
                # Count purchases
                num_purchases = len(purchase_history)
                
                # Encode location and skin type
                data.append({
                    'user_id': user.id,
                    'age': user.age or 0,
                    'location': user.location or 'Unknown',
                    'skin_type': user.skin_type or 'Unknown',
                    'has_email': has_email,
                    'has_facebook': has_facebook,
                    'has_google': has_google,
                    'num_channels': has_email + has_facebook + has_google,
                    'num_purchases': num_purchases
                })
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {str(e)}")
                continue
        
        if not data:
            logger.error("No valid user data to process!")
            return None, None, None
        
        df = pd.DataFrame(data)
        logger.debug(f"Created dataframe with shape: {df.shape}")
        logger.debug(f"Dataframe columns: {df.columns.tolist()}")
        logger.debug(f"Sample data:\n{df.head()}")
        
        # Encode categorical variables
        le_location = LabelEncoder()
        le_skin_type = LabelEncoder()
        
        df['location_encoded'] = le_location.fit_transform(df['location'])
        df['skin_type_encoded'] = le_skin_type.fit_transform(df['skin_type'])
        
        # Features for clustering
        features = ['age', 'location_encoded', 'skin_type_encoded', 
                   'has_email', 'has_facebook', 'has_google', 
                   'num_channels', 'num_purchases']
        
        X = df[features].values
        logger.debug(f"Feature matrix shape: {X.shape}")
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        logger.debug("Features standardized")
        
        return X_scaled, df, features
    
    def calculate_channel_distribution(self, cluster_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate channel distribution for a cluster"""
        total_users = len(cluster_df)
        if total_users == 0:
            return {"email": 0, "facebook": 0, "google_seo": 0}
        
        email_pct = (cluster_df['has_email'].sum() / total_users) * 100
        facebook_pct = (cluster_df['has_facebook'].sum() / total_users) * 100
        google_pct = (cluster_df['has_google'].sum() / total_users) * 100
        
        # Normalize to ensure they sum to 100
        total = email_pct + facebook_pct + google_pct
        if total > 0:
            email_pct = (email_pct / total) * 100
            facebook_pct = (facebook_pct / total) * 100
            google_pct = (google_pct / total) * 100
        
        distribution = {
            "email": round(email_pct, 2),
            "facebook": round(facebook_pct, 2),
            "google_seo": round(google_pct, 2)
        }
        
        logger.debug(f"Channel distribution: {distribution}")
        return distribution
    
    def get_cluster_characteristics(self, cluster_df: pd.DataFrame) -> Dict[str, Any]:
        """Extract key characteristics of a cluster"""
        characteristics = {
            "avg_age": round(cluster_df['age'].mean(), 1),
            "age_range": f"{int(cluster_df['age'].min())}-{int(cluster_df['age'].max())}",
            "top_locations": cluster_df['location'].value_counts().head(3).index.tolist(),
            "top_skin_types": cluster_df['skin_type'].value_counts().head(2).index.tolist(),
            "avg_purchases": round(cluster_df['num_purchases'].mean(), 1),
            "purchase_range": f"{int(cluster_df['num_purchases'].min())}-{int(cluster_df['num_purchases'].max())}",
            "high_purchasers_pct": round((cluster_df['num_purchases'] >= 2).sum() / len(cluster_df) * 100, 1),
            "multi_channel_users": round((cluster_df['num_channels'] > 1).sum() / len(cluster_df) * 100, 1)
        }
        logger.debug(f"Cluster characteristics: {characteristics}")
        return characteristics
    
    async def perform_clustering(self) -> List[Dict[str, Any]]:
        """Perform k-means clustering on user data"""
        logger.info("=== Starting perform_clustering ===")
        
        try:
            with Session(engine) as session:
                # Get all users
                logger.debug("Fetching users from database...")
                users = session.exec(select(User)).all()
                logger.info(f"Found {len(users)} users in database")
                
                if len(users) == 0:
                    logger.error("No users found in database!")
                    return []
                
                if len(users) < self.n_clusters:
                    logger.warning(f"Not enough users ({len(users)}) for {self.n_clusters} clusters")
                    # Adjust number of clusters
                    self.n_clusters = max(1, len(users) // 2)
                    logger.info(f"Adjusted number of clusters to {self.n_clusters}")
                
                # Prepare data
                X_scaled, df, features = self.prepare_user_data(users)
                
                if X_scaled is None:
                    logger.error("Failed to prepare user data")
                    return []
                
                # Perform clustering
                logger.info(f"Performing k-means clustering with {self.n_clusters} clusters...")
                kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
                cluster_labels = kmeans.fit_predict(X_scaled)
                logger.info("K-means clustering completed")
                
                # Add cluster labels to dataframe
                df['cluster'] = cluster_labels
                
                # Analyze each cluster
                clusters_data = []
                for cluster_id in range(self.n_clusters):
                    logger.debug(f"Analyzing cluster {cluster_id}...")
                    cluster_df = df[df['cluster'] == cluster_id]
                    
                    # Calculate size as percentage
                    size_pct = round(len(cluster_df) / len(df) * 100, 1)
                    logger.debug(f"Cluster {cluster_id} size: {size_pct}% ({len(cluster_df)} users)")
                    
                    # Get channel distribution
                    channel_dist = self.calculate_channel_distribution(cluster_df)
                    
                    # Get characteristics
                    characteristics = self.get_cluster_characteristics(cluster_df)
                    
                    # Get centroid
                    centroid = kmeans.cluster_centers_[cluster_id].tolist()
                    
                    clusters_data.append({
                        "cluster_id": cluster_id,
                        "size": size_pct,
                        "channel_distribution": channel_dist,
                        "characteristics": characteristics,
                        "centroid": centroid,
                        "user_ids": cluster_df['user_id'].tolist()
                    })
                
                # Sort by size descending
                clusters_data.sort(key=lambda x: x['size'], reverse=True)
                
                logger.info(f"=== Clustering completed: Created {len(clusters_data)} clusters from {len(users)} users ===")
                return clusters_data
                
        except Exception as e:
            logger.error(f"Error in perform_clustering: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def save_clusters(self, clusters_data: List[Dict[str, Any]], segment_names: List[Dict[str, str]]) -> List[CustomerSegment]:
        """Save clusters to database with generated names"""
        logger.info(f"=== Saving {len(clusters_data)} clusters to database ===")
        
        try:
            with Session(engine) as session:
                # Delete existing segments
                logger.debug("Deleting existing segments...")
                existing = session.exec(select(CustomerSegment)).all()
                for segment in existing:
                    session.delete(segment)
                session.commit()
                logger.info(f"Deleted {len(existing)} existing segments")
                
                # Create new segments
                saved_segments = []
                for i, cluster_data in enumerate(clusters_data):
                    # Find matching name from generated names
                    name_data = next((n for n in segment_names if n.get("cluster_id") == cluster_data["cluster_id"]), {})
                    
                    segment_name = name_data.get("name", f"Segment {i+1}")
                    segment_desc = name_data.get("description", "")
                    
                    logger.debug(f"Creating segment: {segment_name}")
                    
                    segment = CustomerSegment(
                        name=segment_name,
                        description=segment_desc,
                        size=cluster_data["size"],
                        channel_distribution=json.dumps(cluster_data["channel_distribution"]),
                        criteria=json.dumps(cluster_data["characteristics"]),
                        cluster_centroid=json.dumps(cluster_data["centroid"])
                    )
                    
                    session.add(segment)
                    saved_segments.append(segment)
                
                session.commit()
                logger.info(f"Committed {len(saved_segments)} segments to database")
                
                # Refresh to get IDs
                for segment in saved_segments:
                    session.refresh(segment)
                    logger.debug(f"Saved segment: {segment.name} (ID: {segment.id})")
                
                logger.info(f"=== Successfully saved {len(saved_segments)} segments ===")
                return saved_segments
                
        except Exception as e:
            logger.error(f"Error saving clusters: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []