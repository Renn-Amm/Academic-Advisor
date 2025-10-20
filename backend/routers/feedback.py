from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, Course, CourseFeedback, Enrollment
from backend.schemas import FeedbackCreate, FeedbackResponse
from backend.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_course_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for a course"""
    # Get course
    course = db.query(Course).filter(Course.course_id == feedback_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {feedback_data.course_id} not found"
        )
    
    # Check if user completed the course
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id,
        Enrollment.status == "completed"
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must complete the course before submitting feedback"
        )
    
    # Check if feedback already exists
    existing_feedback = db.query(CourseFeedback).filter(
        CourseFeedback.user_id == current_user.id,
        CourseFeedback.course_id == course.id
    ).first()
    
    if existing_feedback:
        # Update existing feedback
        existing_feedback.rating = feedback_data.rating
        existing_feedback.difficulty = feedback_data.difficulty
        existing_feedback.comment = feedback_data.comment
        existing_feedback.would_recommend = feedback_data.would_recommend
        existing_feedback.skills_gained = feedback_data.skills_gained
        
        db.commit()
        db.refresh(existing_feedback)
        
        return existing_feedback
    
    # Create new feedback
    new_feedback = CourseFeedback(
        user_id=current_user.id,
        course_id=course.id,
        rating=feedback_data.rating,
        difficulty=feedback_data.difficulty,
        comment=feedback_data.comment,
        would_recommend=feedback_data.would_recommend,
        skills_gained=feedback_data.skills_gained
    )
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return new_feedback


@router.get("/my-feedback")
async def get_my_feedback(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all feedback submitted by current user"""
    feedback_list = db.query(CourseFeedback).filter(
        CourseFeedback.user_id == current_user.id
    ).all()
    
    result = []
    for feedback in feedback_list:
        result.append({
            "id": feedback.id,
            "course": {
                "course_id": feedback.course.course_id,
                "course_name": feedback.course.course_name
            },
            "rating": feedback.rating,
            "difficulty": feedback.difficulty,
            "comment": feedback.comment,
            "would_recommend": feedback.would_recommend,
            "skills_gained": feedback.skills_gained,
            "timestamp": feedback.timestamp
        })
    
    return {
        "total": len(result),
        "feedback": result
    }


@router.get("/course/{course_id}")
async def get_course_feedback(
    course_id: str,
    db: Session = Depends(get_db)
):
    """Get all feedback for a specific course"""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )
    
    feedback_list = db.query(CourseFeedback).filter(
        CourseFeedback.course_id == course.id
    ).all()
    
    if not feedback_list:
        return {
            "course_id": course_id,
            "course_name": course.course_name,
            "total_feedback": 0,
            "average_rating": 0.0,
            "feedback": []
        }
    
    # Calculate statistics
    ratings = [f.rating for f in feedback_list]
    avg_rating = sum(ratings) / len(ratings)
    
    difficulty_counts = {}
    for f in feedback_list:
        difficulty_counts[f.difficulty] = difficulty_counts.get(f.difficulty, 0) + 1
    
    recommend_count = sum(1 for f in feedback_list if f.would_recommend)
    
    return {
        "course_id": course_id,
        "course_name": course.course_name,
        "total_feedback": len(feedback_list),
        "average_rating": round(avg_rating, 2),
        "recommend_percentage": round((recommend_count / len(feedback_list)) * 100, 1),
        "difficulty_distribution": difficulty_counts,
        "feedback": [
            {
                "rating": f.rating,
                "difficulty": f.difficulty,
                "comment": f.comment,
                "would_recommend": f.would_recommend,
                "skills_gained": f.skills_gained,
                "timestamp": f.timestamp
            }
            for f in feedback_list
        ]
    }
