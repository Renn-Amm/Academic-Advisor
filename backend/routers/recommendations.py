from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User
from backend.schemas import RecommendationQuery, RecommendationResponse, ScheduleResponse, ModuleSchedule
from backend.auth import get_current_active_user
from backend.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    query_data: RecommendationQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized course recommendations"""
    service = RecommendationService(db)
    
    courses, explanations, ai_response = service.get_personalized_recommendations(
        user=current_user,
        query=query_data.query,
        limit=query_data.limit
    )
    
    return {
        "courses": courses,
        "explanations": explanations,
        "ai_response": ai_response
    }


@router.get("/schedule", response_model=ScheduleResponse)
async def get_personalized_schedule(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized modular schedule"""
    service = RecommendationService(db)
    modules = service.generate_schedule(current_user)
    
    # Convert to proper response format
    module_list = []
    for module in modules:
        module_list.append(ModuleSchedule(
            module_name=module["module_name"],
            start_date=module["start_date"],
            end_date=module["end_date"],
            courses=module["courses"],
            total_credits=module["total_credits"],
            description=module["description"]
        ))
    
    return {
        "modules": module_list
    }


@router.get("/major/{major}")
async def get_major_recommendations(
    major: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recommended courses for a specific major"""
    service = RecommendationService(db)
    
    # Temporarily update user major for recommendation
    original_major = current_user.major
    current_user.major = major
    
    courses, explanations, ai_response = service.get_personalized_recommendations(
        user=current_user,
        limit=10
    )
    
    # Restore original major
    current_user.major = original_major
    
    return {
        "major": major,
        "courses": courses,
        "explanations": explanations,
        "ai_response": ai_response
    }
