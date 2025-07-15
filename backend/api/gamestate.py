# backend/api/gamestate.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from data.database import get_session
from data.models import GameState, Metric, Campaign

router = APIRouter()

class GameStateUpdate(BaseModel):
    current_date: Optional[datetime] = None
    game_speed: Optional[str] = None
    is_running: Optional[bool] = None

class GameStateResponse(BaseModel):
    id: str
    current_date: datetime
    game_speed: str
    is_running: bool
    total_reach_optimal: float
    total_reach_non_optimal: float
    created_at: datetime
    updated_at: datetime

class OptimizationDataPoint(BaseModel):
    date: str
    optimal: float
    nonOptimal: float

@router.get("/current", response_model=Optional[GameStateResponse])
async def get_game_state(session: Session = Depends(get_session)):
    """Get current game state"""
    game_state = session.exec(
        select(GameState).order_by(GameState.created_at.desc())
    ).first()
    
    if not game_state:
        # Create initial game state
        game_state = GameState(
            current_date=datetime.utcnow(),
            game_speed="medium",
            is_running=False,
            total_reach_optimal=0.0,
            total_reach_non_optimal=0.0
        )
        session.add(game_state)
        session.commit()
        session.refresh(game_state)
    
    return game_state

@router.put("/current", response_model=GameStateResponse)
async def update_game_state(
    update_data: GameStateUpdate,
    session: Session = Depends(get_session)
):
    """Update game state"""
    game_state = session.exec(
        select(GameState).order_by(GameState.created_at.desc())
    ).first()
    
    if not game_state:
        raise HTTPException(status_code=404, detail="Game state not found")
    
    # Update fields
    if update_data.current_date:
        game_state.current_date = update_data.current_date
    if update_data.game_speed:
        game_state.game_speed = update_data.game_speed
    if update_data.is_running is not None:
        game_state.is_running = update_data.is_running
    
    game_state.updated_at = datetime.utcnow()
    session.add(game_state)
    session.commit()
    session.refresh(game_state)
    
    return game_state

@router.post("/reset")
async def reset_game_state(session: Session = Depends(get_session)):
    """Reset game state metrics"""
    game_state = session.exec(
        select(GameState).order_by(GameState.created_at.desc())
    ).first()
    
    if game_state:
        game_state.total_reach_optimal = 0.0
        game_state.total_reach_non_optimal = 0.0
        game_state.current_date = datetime.utcnow()
        game_state.updated_at = datetime.utcnow()
        session.add(game_state)
        session.commit()
    
    return {"message": "Game state reset successfully"}

@router.get("/optimization-data", response_model=List[OptimizationDataPoint])
async def get_optimization_data(
    days: int = 30,
    session: Session = Depends(get_session)
):
    """Get optimization performance data for the specified number of days"""
    # Get metrics for the last N days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query metrics grouped by date
    metrics_query = select(Metric).where(
        Metric.timestamp >= start_date,
        Metric.timestamp <= end_date
    ).order_by(Metric.timestamp)
    
    metrics = session.exec(metrics_query).all()
    
    # Get active campaigns to determine if they're optimized
    active_campaigns = session.exec(
        select(Campaign).where(Campaign.status == "active")
    ).all()
    
    # Group metrics by date and calculate reach
    daily_data = {}
    for metric in metrics:
        date_key = metric.timestamp.date() if metric.timestamp else datetime.utcnow().date()
        
        if date_key not in daily_data:
            daily_data[date_key] = {
                "optimal": 0.0,
                "nonOptimal": 0.0
            }
        
        # Calculate reach (impressions * engagement_rate)
        reach = (metric.impressions or 0) * (metric.engagement_rate or 0.01)
        
        # Determine if this campaign is optimized based on performance
        # (You can adjust this logic based on your optimization criteria)
        is_optimized = (metric.engagement_rate or 0) > 0.03 and (metric.conversion_rate or 0) > 0.01
        
        if is_optimized:
            daily_data[date_key]["optimal"] += reach
        else:
            daily_data[date_key]["nonOptimal"] += reach
    
    # If no real data, provide a baseline
    if not daily_data:
        # Provide baseline data showing system is ready for optimization
        for i in range(min(days, 7)):
            date = end_date - timedelta(days=i)
            daily_data[date.date()] = {
                "optimal": 0.0,
                "nonOptimal": 0.0
            }
    
    # Convert to response format
    result = []
    for date, values in sorted(daily_data.items()):
        result.append(OptimizationDataPoint(
            date=date.isoformat(),
            optimal=values["optimal"],
            nonOptimal=values["nonOptimal"]
        ))
    
    return result