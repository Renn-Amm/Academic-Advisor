from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    major = Column(String, default="Computer Science")
    program = Column(String)
    career_goal = Column(String)
    experience_level = Column(String, default="Beginner")
    current_gpa = Column(Float, default=0.0)
    completed_credits = Column(Integer, default=0)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    enrolled_courses = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    course_feedback = relationship("CourseFeedback", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    """Course model"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, unique=True, index=True, nullable=False)
    course_name = Column(String, nullable=False)
    course_description = Column(Text)
    category = Column(String, index=True)
    course_type = Column(String, index=True)  # mandatory, secondary, audit
    credits = Column(Integer, default=0)
    duration_weeks = Column(Integer, default=3)
    professor = Column(String)
    skills_covered = Column(JSON)  # Store as JSON array
    estimated_difficulty = Column(String)
    prerequisites = Column(JSON)  # Store as JSON array
    max_students = Column(Integer, default=30)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    feedback = relationship("CourseFeedback", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    """Course enrollment model"""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="enrolled")  # enrolled, completed, dropped
    grade = Column(Float)
    completion_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="enrolled_courses")
    course = relationship("Course", back_populates="enrollments")


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query_type = Column(String)  # recommendation, schedule, general
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")


class CourseFeedback(Base):
    """Course feedback model"""
    __tablename__ = "course_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating = Column(Integer)  # 1-5
    difficulty = Column(String)  # too_easy, just_right, too_hard
    comment = Column(Text)
    would_recommend = Column(Boolean)
    skills_gained = Column(JSON)  # Store as JSON array
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="course_feedback")
    course = relationship("Course", back_populates="feedback")


class Schedule(Base):
    """Student schedule model"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    courses = Column(JSON)  # Store course IDs as JSON array
    total_credits = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
