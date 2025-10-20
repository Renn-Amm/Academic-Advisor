from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    major: Optional[str] = "Computer Science"
    program: Optional[str] = None
    career_goal: Optional[str] = None
    experience_level: Optional[str] = "Beginner"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    student_id: str
    current_gpa: float
    completed_credits: int
    registration_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    major: Optional[str] = None
    career_goal: Optional[str] = None
    experience_level: Optional[str] = None


# Course Schemas
class CourseBase(BaseModel):
    course_id: str
    course_name: str
    course_description: Optional[str] = None
    category: str
    course_type: str
    credits: int
    duration_weeks: int = 3
    professor: Optional[str] = None
    skills_covered: Optional[List[str]] = []
    estimated_difficulty: Optional[str] = None
    prerequisites: Optional[List[str]] = []
    max_students: int = 30


class CourseCreate(CourseBase):
    pass


class CourseResponse(CourseBase):
    id: int
    
    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    total: int
    courses: List[CourseResponse]


# Enrollment Schemas
class EnrollmentCreate(BaseModel):
    course_id: str


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrollment_date: datetime
    status: str
    grade: Optional[float] = None
    completion_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatQuery(BaseModel):
    message: str
    query_type: Optional[str] = "general"


class ChatResponse(BaseModel):
    message: str
    response: str
    timestamp: datetime
    recommended_courses: Optional[List[CourseResponse]] = []
    
    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackCreate(BaseModel):
    course_id: str
    rating: int = Field(..., ge=1, le=5)
    difficulty: str
    comment: Optional[str] = None
    would_recommend: bool
    skills_gained: Optional[List[str]] = []


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    rating: int
    difficulty: str
    comment: Optional[str] = None
    would_recommend: bool
    skills_gained: Optional[List[str]] = []
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Schedule Schemas
class ModuleSchedule(BaseModel):
    module_name: str
    start_date: datetime
    end_date: datetime
    courses: List[CourseResponse]
    total_credits: int
    description: str


class ScheduleResponse(BaseModel):
    modules: List[ModuleSchedule]


# Recommendation Schemas
class RecommendationQuery(BaseModel):
    query: Optional[str] = None
    limit: int = 6


class RecommendationResponse(BaseModel):
    courses: List[CourseResponse]
    explanations: Dict[str, List[str]]
    ai_response: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
