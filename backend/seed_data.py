"""
Database seeding script to populate initial course data
"""
import sys
import os
import pandas as pd
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine, Base
from backend.models import Course, User
from backend.auth import get_password_hash


def seed_courses(db: Session):
    """Seed courses from CSV file"""
    csv_path = "data/processed/harbour_space_courses.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Course data file not found: {csv_path}")
        print("Creating sample courses...")
        create_sample_courses(db)
        return
    
    try:
        # Read courses from CSV
        courses_df = pd.read_csv(csv_path)
        print(f"📚 Loading {len(courses_df)} courses from CSV...")
        
        courses_added = 0
        
        for _, row in courses_df.iterrows():
            # Check if course already exists
            existing_course = db.query(Course).filter(
                Course.course_id == row.get('course_id', f"CS{courses_added}")
            ).first()
            
            if existing_course:
                continue
            
            # Parse skills
            skills_str = row.get('skills_covered_str', '')
            skills = []
            if isinstance(skills_str, str) and skills_str:
                skills = [s.strip() for s in skills_str.split(',')]
            
            # Create course
            course = Course(
                course_id=row.get('course_id', f"CS{courses_added}"),
                course_name=row.get('course_name', 'Unknown Course'),
                course_description=row.get('course_description', ''),
                category=row.get('category', 'Computer Science'),
                course_type=row.get('course_type', 'secondary'),
                credits=int(row.get('credits', 4)),
                duration_weeks=int(row.get('duration_weeks', 3)),
                professor=row.get('professor', 'TBD'),
                skills_covered=skills,
                estimated_difficulty=row.get('estimated_difficulty', 'Intermediate'),
                prerequisites=[],
                max_students=30
            )
            
            db.add(course)
            courses_added += 1
        
        db.commit()
        print(f" Added {courses_added} courses to database")
        
    except Exception as e:
        print(f" Error loading courses from CSV: {e}")
        db.rollback()
        print("Creating sample courses instead...")
        create_sample_courses(db)


def create_sample_courses(db: Session):
    """Create sample courses if CSV is not available"""
    sample_courses = [
        {
            "course_id": "CS101",
            "course_name": "Introduction to Programming",
            "course_description": "Learn the fundamentals of programming using Python",
            "category": "Computer Science",
            "course_type": "mandatory",
            "credits": 6,
            "duration_weeks": 3,
            "professor": "Dr. Elena Rodriguez",
            "skills_covered": ["Python", "Programming", "Algorithms", "Data Structures"],
            "estimated_difficulty": "Beginner"
        },
        {
            "course_id": "CS201",
            "course_name": "Data Structures and Algorithms",
            "course_description": "Advanced data structures and algorithm design",
            "category": "Computer Science",
            "course_type": "mandatory",
            "credits": 6,
            "duration_weeks": 3,
            "professor": "Prof. Marcus Chen",
            "skills_covered": ["Algorithms", "Data Structures", "Problem Solving", "Optimization"],
            "estimated_difficulty": "Intermediate"
        },
        {
            "course_id": "CS301",
            "course_name": "Web Development",
            "course_description": "Full-stack web development with modern frameworks",
            "category": "Computer Science",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Dr. Sarah Johnson",
            "skills_covered": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
            "estimated_difficulty": "Intermediate"
        },
        {
            "course_id": "DS101",
            "course_name": "Machine Learning Fundamentals",
            "course_description": "Introduction to machine learning algorithms and applications",
            "category": "Data Science",
            "course_type": "mandatory",
            "credits": 6,
            "duration_weeks": 3,
            "professor": "Prof. James Wilson",
            "skills_covered": ["Machine Learning", "Python", "Statistics", "Neural Networks"],
            "estimated_difficulty": "Advanced"
        },
        {
            "course_id": "DS201",
            "course_name": "Data Analysis with Python",
            "course_description": "Statistical analysis and data visualization",
            "category": "Data Science",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Dr. Maria Garcia",
            "skills_covered": ["Python", "Pandas", "NumPy", "Visualization", "Statistics"],
            "estimated_difficulty": "Intermediate"
        },
        {
            "course_id": "CY101",
            "course_name": "Cybersecurity Fundamentals",
            "course_description": "Essential concepts in cybersecurity and network security",
            "category": "Cybersecurity",
            "course_type": "mandatory",
            "credits": 6,
            "duration_weeks": 3,
            "professor": "Prof. David Kim",
            "skills_covered": ["Security", "Networking", "Encryption", "Ethical Hacking"],
            "estimated_difficulty": "Intermediate"
        },
        {
            "course_id": "CY201",
            "course_name": "Network Security",
            "course_description": "Advanced network security protocols and practices",
            "category": "Cybersecurity",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Dr. Lisa Thompson",
            "skills_covered": ["Network Security", "Firewalls", "VPN", "Intrusion Detection"],
            "estimated_difficulty": "Advanced"
        },
        {
            "course_id": "BU101",
            "course_name": "Business Strategy",
            "course_description": "Strategic planning and business management",
            "category": "Business",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Prof. Alex Morgan",
            "skills_covered": ["Strategy", "Management", "Leadership", "Business Analysis"],
            "estimated_difficulty": "Intermediate"
        },
        {
            "course_id": "DE101",
            "course_name": "User Experience Design",
            "course_description": "Principles of user-centered design and UX research",
            "category": "Design",
            "course_type": "audit",
            "credits": 0,
            "duration_weeks": 3,
            "professor": "Dr. Rachel Green",
            "skills_covered": ["UX Design", "User Research", "Prototyping", "Figma"],
            "estimated_difficulty": "Beginner"
        },
        {
            "course_id": "CS401",
            "course_name": "Cloud Computing",
            "course_description": "Cloud infrastructure, services, and deployment",
            "category": "Computer Science",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Dr. Elena Rodriguez",
            "skills_covered": ["AWS", "Azure", "Docker", "Kubernetes", "DevOps"],
            "estimated_difficulty": "Advanced"
        },
        {
            "course_id": "DS301",
            "course_name": "Deep Learning",
            "course_description": "Neural networks and deep learning architectures",
            "category": "Data Science",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Prof. James Wilson",
            "skills_covered": ["Deep Learning", "TensorFlow", "PyTorch", "CNN", "RNN"],
            "estimated_difficulty": "Advanced"
        },
        {
            "course_id": "CS501",
            "course_name": "Mobile App Development",
            "course_description": "iOS and Android application development",
            "category": "Computer Science",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Dr. Sarah Johnson",
            "skills_covered": ["React Native", "iOS", "Android", "Mobile UI", "App Store"],
            "estimated_difficulty": "Intermediate"
        },
        {
            "course_id": "BU201",
            "course_name": "Digital Marketing",
            "course_description": "Digital marketing strategies and analytics",
            "category": "Business",
            "course_type": "audit",
            "credits": 0,
            "duration_weeks": 3,
            "professor": "Prof. Alex Morgan",
            "skills_covered": ["Marketing", "SEO", "Social Media", "Analytics", "Content Strategy"],
            "estimated_difficulty": "Beginner"
        },
        {
            "course_id": "CY301",
            "course_name": "Ethical Hacking",
            "course_description": "Penetration testing and security assessment",
            "category": "Cybersecurity",
            "course_type": "secondary",
            "credits": 4,
            "duration_weeks": 3,
            "professor": "Prof. David Kim",
            "skills_covered": ["Ethical Hacking", "Penetration Testing", "Security Tools", "Kali Linux"],
            "estimated_difficulty": "Advanced"
        },
        {
            "course_id": "DE201",
            "course_name": "Visual Design Principles",
            "course_description": "Graphic design fundamentals and visual communication",
            "category": "Design",
            "course_type": "audit",
            "credits": 0,
            "duration_weeks": 3,
            "professor": "Dr. Rachel Green",
            "skills_covered": ["Graphic Design", "Typography", "Color Theory", "Adobe Creative Suite"],
            "estimated_difficulty": "Beginner"
        }
    ]
    
    courses_added = 0
    for course_data in sample_courses:
        existing_course = db.query(Course).filter(
            Course.course_id == course_data["course_id"]
        ).first()
        
        if not existing_course:
            course = Course(**course_data)
            db.add(course)
            courses_added += 1
    
    db.commit()
    print(f" Added {courses_added} sample courses to database")


def create_test_user(db: Session):
    """Create a test user for development"""
    existing_user = db.query(User).filter(User.email == "test@harbour.space").first()
    
    if not existing_user:
        test_user = User(
            student_id="HS12345",
            email="test@harbour.space",
            hashed_password=get_password_hash("password123"),
            first_name="Test",
            last_name="User",
            major="Computer Science",
            program="Bachelor's Degree",
            career_goal="Software Engineer",
            experience_level="Intermediate"
        )
        
        db.add(test_user)
        db.commit()
        print(" Created test user: test@harbour.space / password123")
    else:
        print("ℹ  Test user already exists")


def main():
    """Main seeding function"""
    print(" Starting database seeding...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print(" Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_courses(db)
        create_test_user(db)
        
        # Show statistics
        course_count = db.query(Course).count()
        user_count = db.query(User).count()
        
        print("\nDatabase Statistics:")
        print(f"   Courses: {course_count}")
        print(f"   Users: {user_count}")
        print("\n Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
