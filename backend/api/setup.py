from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
import json

from data.database import get_session
from data.models import SetupConfiguration, Company, Product
from core.scheduler import schedule_budget_rebalancing
from agents.segmentation_agent import generate_customer_segments

router = APIRouter()

class SetupRequest(BaseModel):
    product_id: UUID
    company_id: UUID
    market_details: dict
    strategic_goals: str
    monthly_budget: float
    guardrails: str
    rebalancing_frequency: str = "weekly"
    campaign_count: int = 5

class SetupResponse(BaseModel):
    id: UUID
    product_id: Optional[UUID]
    company_id: Optional[UUID]
    market_details: Optional[str]
    strategic_goals: Optional[str]
    monthly_budget: float
    guardrails: Optional[str]
    rebalancing_frequency: str
    campaign_count: int
    is_active: bool

class CompanyOption(BaseModel):
    id: UUID
    name: str
    industry: Optional[str]

class ProductOption(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    company_id: Optional[UUID]

@router.get("/companies", response_model=List[CompanyOption])
async def get_companies(session: Session = Depends(get_session)):
    """Get all available companies for selection"""
    companies = session.exec(select(Company)).all()
    return [
        CompanyOption(
            id=company.id,
            name=company.company_name or "Unknown",
            industry=company.industry
        )
        for company in companies
    ]

@router.get("/products", response_model=List[ProductOption])
async def get_products(
    company_id: Optional[UUID] = None,
    session: Session = Depends(get_session)
):
    """Get all available products for selection"""
    query = select(Product)
    if company_id:
        query = query.where(Product.company_id == company_id)
    
    products = session.exec(query).all()
    return [
        ProductOption(
            id=product.id,
            name=product.product_name or "Unknown",
            description=product.description,
            company_id=product.company_id
        )
        for product in products
    ]

@router.post("/initialize", response_model=SetupResponse)
async def initialize_setup(
    setup_data: SetupRequest,
    session: Session = Depends(get_session)
):
    """Initialize the application with setup configuration"""
    # Check if there's already an active setup
    existing_setup = session.exec(
        select(SetupConfiguration).where(SetupConfiguration.is_active == True)
    ).first()
    
    if existing_setup:
        existing_setup.is_active = False
        session.add(existing_setup)
    
    # Verify product and company exist
    product = session.get(Product, setup_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    company = session.get(Company, setup_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Create new setup configuration
    setup_config = SetupConfiguration(
        product_id=setup_data.product_id,
        company_id=setup_data.company_id,
        market_details=json.dumps(setup_data.market_details),
        strategic_goals=setup_data.strategic_goals,
        monthly_budget=setup_data.monthly_budget,
        guardrails=setup_data.guardrails,
        rebalancing_frequency=setup_data.rebalancing_frequency,
        campaign_count=setup_data.campaign_count,
        is_active=True
    )
    
    session.add(setup_config)
    session.commit()
    session.refresh(setup_config)
    
    # Schedule budget rebalancing
    schedule_budget_rebalancing(setup_data.rebalancing_frequency)
    
    # Generate customer segments asynchronously
    # This would typically be done in a background task
    try:
        segments = await generate_customer_segments(
            product_id=str(setup_data.product_id),
            market_details=setup_data.market_details,
            strategic_goals=setup_data.strategic_goals
        )
    except Exception as e:
        print(f"Error generating segments: {str(e)}")
    
    return setup_config

@router.get("/current", response_model=Optional[SetupResponse])
async def get_current_setup(session: Session = Depends(get_session)):
    """Get the current active setup configuration"""
    setup = session.exec(
        select(SetupConfiguration).where(SetupConfiguration.is_active == True)
    ).first()
    
    if not setup:
        return None
    
    return setup

@router.put("/current", response_model=SetupResponse)
async def update_setup(
    setup_data: SetupRequest,
    session: Session = Depends(get_session)
):
    """Update the current setup configuration"""
    setup = session.exec(
        select(SetupConfiguration).where(SetupConfiguration.is_active == True)
    ).first()
    
    if not setup:
        raise HTTPException(status_code=404, detail="No active setup found")
    
    # Update fields
    setup.product_id = setup_data.product_id
    setup.company_id = setup_data.company_id
    setup.market_details = json.dumps(setup_data.market_details)
    setup.strategic_goals = setup_data.strategic_goals
    setup.monthly_budget = setup_data.monthly_budget
    setup.guardrails = setup_data.guardrails
    setup.rebalancing_frequency = setup_data.rebalancing_frequency
    setup.campaign_count = setup_data.campaign_count
    
    session.add(setup)
    session.commit()
    session.refresh(setup)
    
    # Reschedule budget rebalancing if frequency changed
    schedule_budget_rebalancing(setup_data.rebalancing_frequency)
    
    return setup