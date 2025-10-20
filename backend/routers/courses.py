from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
from backend.models import User, Course, Enrollment
from backend.schemas import (
    CourseResponse, 
    CourseListResponse, 
    CourseCreate,
    EnrollmentCreate,
    EnrollmentResponse
)
from backend.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=CourseListResponse)
async def get_all_courses(
    category: Optional[str] = None,
    course_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all courses with optional filters"""
    query = db.query(Course)
    
    if category:
        query = query.filter(Course.category.ilike(f"%{category}%"))
    
    if course_type:
        query = query.filter(Course.course_type == course_type)
    
    total = query.count()
    courses = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "courses": courses
    }


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific course by ID"""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )
    
    return course


@router.post("/enroll", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll current user in a course"""
    # Get course
    course = db.query(Course).filter(Course.course_id == enrollment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {enrollment_data.course_id} not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course.id,
        Enrollment.status == "enrolled"
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Check max students
    current_enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course.id,
        Enrollment.status == "enrolled"
    ).count()
    
    if current_enrollments >= course.max_students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is full"
        )
    
    # Create enrollment
    new_enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course.id,
        status="enrolled"
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    
    return new_enrollment


@router.delete("/enroll/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def drop_course(
    enrollment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Drop a course enrollment"""
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.user_id == current_user.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    enrollment.status = "dropped"
    db.commit()
    
    return None


@router.get("/category/{category}", response_model=CourseListResponse)
async def get_courses_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    """Get all courses in a specific category"""
    courses = db.query(Course).filter(
        Course.category.ilike(f"%{category}%")
    ).all()
    
    return {
        "total": len(courses),
        "courses": courses
    }


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new course (admin only in production)"""
    # Check if course already exists
    existing_course = db.query(Course).filter(
        Course.course_id == course_data.course_id
    ).first()
    
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course {course_data.course_id} already exists"
        )
    
    # Create course
    new_course = Course(**course_data.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course
