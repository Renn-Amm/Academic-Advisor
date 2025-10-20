from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User
from backend.schemas import UserResponse, UserUpdate
from backend.auth import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/me/enrollments")
async def get_user_enrollments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's enrolled courses"""
    enrollments = current_user.enrolled_courses
    
    result = []
    for enrollment in enrollments:
        result.append({
            "enrollment_id": enrollment.id,
            "course": {
                "id": enrollment.course.id,
                "course_id": enrollment.course.course_id,
                "course_name": enrollment.course.course_name,
                "course_type": enrollment.course.course_type,
                "credits": enrollment.course.credits,
                "professor": enrollment.course.professor
            },
            "status": enrollment.status,
            "enrollment_date": enrollment.enrollment_date,
            "grade": enrollment.grade,
            "completion_date": enrollment.completion_date
        })
    
    return {
        "total": len(result),
        "enrollments": result
    }


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    enrollments = current_user.enrolled_courses
    
    total_enrolled = len([e for e in enrollments if e.status == "enrolled"])
    total_completed = len([e for e in enrollments if e.status == "completed"])
    total_credits = sum([e.course.credits for e in enrollments if e.status == "completed"])
    
    # Calculate GPA
    graded_courses = [e for e in enrollments if e.grade is not None]
    avg_grade = sum([e.grade for e in graded_courses]) / len(graded_courses) if graded_courses else 0.0
    
    return {
        "student_id": current_user.student_id,
        "major": current_user.major,
        "program": current_user.program,
        "total_enrolled": total_enrolled,
        "total_completed": total_completed,
        "completed_credits": total_credits,
        "current_gpa": round(avg_grade, 2),
        "career_goal": current_user.career_goal,
        "experience_level": current_user.experience_level
    }
