# backend/api/gamestate.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from data.database import get_session
from data.models import GameState

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