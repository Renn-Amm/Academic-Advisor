from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta

from backend.models import User, Course, Enrollment, CourseFeedback


class RecommendationService:
    """Service for generating course recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def get_personalized_recommendations(
        self, 
        user: User, 
        query: str = None, 
        limit: int = 6
    ) -> Tuple[List[Course], Dict[str, List[str]], str]:
        """Get personalized course recommendations for a user"""
        
        # Get all available courses
        enrolled_course_ids = [e.course_id for e in user.enrolled_courses 
                               if e.status in ["enrolled", "completed"]]
        
        available_courses = self.db.query(Course).filter(
            Course.id.notin_(enrolled_course_ids)
        ).all()
        
        if not available_courses:
            return [], {}, "No courses available for recommendation."
        
        # Filter by major
        major_courses = [c for c in available_courses 
                        if user.major.lower() in c.category.lower()]
        
        if not major_courses:
            major_courses = available_courses
        
        # Apply feedback-based filtering
        scored_courses = self._score_courses(major_courses, user, query)
        
        # Get top recommendations
        top_courses = scored_courses[:limit]
        
        # Generate explanations
        explanations = self._generate_explanations(top_courses, user, query)
        
        # Generate AI response
        ai_response = self._generate_ai_response(top_courses, explanations, user, query)
        
        return top_courses, explanations, ai_response
    
    def _score_courses(
        self, 
        courses: List[Course], 
        user: User, 
        query: str = None
    ) -> List[Course]:
        """Score and sort courses by relevance"""
        scored_courses = []
        
        for course in courses:
            score = 0
            
            # Course type priority
            if course.course_type == "mandatory":
                score += 5
            elif course.course_type == "secondary":
                score += 3
            else:
                score += 1
            
            # Query matching
            if query:
                query_lower = query.lower()
                course_text = f"{course.course_name} {course.course_description}".lower()
                if query_lower in course_text:
                    score += 4
            
            # Major relevance
            if user.major.lower() in course.category.lower():
                score += 3
            
            # Career goal alignment
            if user.career_goal and course.skills_covered:
                career_keywords = self._get_career_keywords(user.career_goal)
                skills_str = " ".join(course.skills_covered).lower()
                for keyword in career_keywords:
                    if keyword in skills_str:
                        score += 2
            
            # Global feedback score
            avg_rating = self._get_course_average_rating(course.id)
            if avg_rating:
                score += avg_rating
            
            scored_courses.append((course, score))
        
        # Sort by score
        scored_courses.sort(key=lambda x: x[1], reverse=True)
        
        return [course for course, score in scored_courses]
    
    def _get_career_keywords(self, career_goal: str) -> List[str]:
        """Get relevant keywords for career goals"""
        career_map = {
            "software engineer": ["programming", "software", "development", "code", "web", "api"],
            "data scientist": ["data", "analytics", "machine learning", "statistics", "python", "ai"],
            "cybersecurity analyst": ["security", "network", "encryption", "hacking", "cyber"],
            "product manager": ["product", "management", "strategy", "business", "agile"],
            "ux designer": ["design", "user", "interface", "experience", "visual", "ui"]
        }
        
        for key, keywords in career_map.items():
            if key in career_goal.lower():
                return keywords
        
        return ["technology", "development"]
    
    def _get_course_average_rating(self, course_id: int) -> float:
        """Get average rating for a course"""
        ratings = self.db.query(CourseFeedback.rating).filter(
            CourseFeedback.course_id == course_id
        ).all()
        
        if not ratings:
            return 0.0
        
        avg = sum([r[0] for r in ratings]) / len(ratings)
        return avg * 0.5  # Scale down to not dominate other factors
    
    def _generate_explanations(
        self, 
        courses: List[Course], 
        user: User, 
        query: str = None
    ) -> Dict[str, List[str]]:
        """Generate explanations for recommended courses"""
        explanations = {}
        
        for course in courses:
            explanation = []
            
            # Course type explanation
            if course.course_type == "mandatory":
                explanation.append(f"**Mandatory for {user.major} major** - Core requirement")
            elif course.course_type == "secondary":
                explanation.append("**Secondary course** - Graded elective for your major")
            else:
                explanation.append("**Audit option** - Explore without grading pressure")
            
            # Credits and duration
            explanation.append(f"**Credits:** {course.credits} | **Duration:** {course.duration_weeks} weeks")
            
            # Career alignment
            if user.career_goal and course.skills_covered:
                career_keywords = self._get_career_keywords(user.career_goal)
                matching_skills = [s for s in course.skills_covered 
                                  if any(k in s.lower() for k in career_keywords)]
                if matching_skills:
                    explanation.append(f"**Aligns with your goal:** {user.career_goal}")
            
            # Query relevance
            if query:
                if query.lower() in course.course_name.lower() or \
                   query.lower() in course.course_description.lower():
                    explanation.append(f"**Matches your search:** '{query}'")
            
            # Skills
            if course.skills_covered:
                top_skills = course.skills_covered[:3]
                explanation.append(f"**Key skills:** {', '.join(top_skills)}")
            
            # Difficulty
            if course.estimated_difficulty:
                explanation.append(f"**Difficulty:** {course.estimated_difficulty}")
            
            explanations[course.course_id] = explanation
        
        return explanations
    
    def _generate_ai_response(
        self, 
        courses: List[Course], 
        explanations: Dict[str, List[str]], 
        user: User, 
        query: str = None
    ) -> str:
        """Generate natural language AI response"""
        if not courses:
            return (
                "I couldn't find specific courses matching your criteria. "
                "Try searching for topics like 'machine learning', 'web development', "
                "or ask me about required courses for your major."
            )
        
        intro = f"Based on your {user.major} major"
        if query:
            intro += f" and your interest in '{query}'"
        intro += ", here are my top recommendations:\n\n"
        
        response = intro
        
        for course in courses:
            course_explanations = explanations.get(course.course_id, [])
            
            response += f"**{course.course_name}** ({course.course_id})\n"
            response += f"*Professor: {course.professor}*\n"
            
            for exp in course_explanations:
                response += f"• {exp}\n"
            
            response += "\n"
        
        response += "\n**Next steps:**\n"
        response += "• Enroll in courses that interest you\n"
        response += "• View your personalized schedule\n"
        response += "• Ask me specific questions about any course\n"
        
        return response
    
    def generate_schedule(self, user: User) -> List[Dict]:
        """Generate a modular schedule for the user"""
        # Get recommended courses
        courses, _, _ = self.get_personalized_recommendations(user, limit=9)
        
        if not courses:
            return []
        
        # Separate by course type
        mandatory = [c for c in courses if c.course_type == "mandatory"]
        secondary = [c for c in courses if c.course_type == "secondary"]
        audit = [c for c in courses if c.course_type == "audit"]
        
        modules = []
        start_date = datetime.now()
        
        # Module 1: Focus on mandatory
        if mandatory:
            module1_courses = mandatory[:2] + secondary[:1]
            if module1_courses:
                modules.append({
                    "module_name": "Module 1",
                    "start_date": start_date,
                    "end_date": start_date + timedelta(weeks=3),
                    "courses": module1_courses,
                    "total_credits": sum(c.credits for c in module1_courses),
                    "description": f"Foundation courses for {user.major}"
                })
        
        # Module 2: Mix of mandatory and secondary
        if len(mandatory) > 2 or len(secondary) > 1:
            module2_courses = mandatory[2:4] + secondary[1:2]
            if module2_courses:
                modules.append({
                    "module_name": "Module 2",
                    "start_date": start_date + timedelta(weeks=3),
                    "end_date": start_date + timedelta(weeks=6),
                    "courses": module2_courses,
                    "total_credits": sum(c.credits for c in module2_courses),
                    "description": f"Advanced {user.major} concepts"
                })
        
        # Module 3: Specialization
        if audit or len(secondary) > 2:
            module3_courses = audit[:1] + secondary[2:3]
            if module3_courses:
                modules.append({
                    "module_name": "Module 3",
                    "start_date": start_date + timedelta(weeks=6),
                    "end_date": start_date + timedelta(weeks=9),
                    "courses": module3_courses,
                    "total_credits": sum(c.credits for c in module3_courses),
                    "description": f"{user.major} specialization and electives"
                })
        
        return modules
