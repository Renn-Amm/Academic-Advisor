"""
API Client for Frontend-Backend Communication
Handles all HTTP requests to the FastAPI backend
"""
import requests
import streamlit as st
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url
        self.token = None
        
    def set_token(self, token: str):
        """Set authentication token"""
        self.token = token
        
    def _get_headers(self) -> Dict:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_response(self, response):
        """Handle API response"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    # Authentication Endpoints
    
    def register(self, email: str, password: str, full_name: str, 
                major: str, program: str) -> Optional[Dict]:
        """Register new user"""
        data = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "major": major,
            "program": program
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=data
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return None
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Login user and get token"""
        data = {"username": email, "password": password}
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/token",
                data=data
            )
            result = self._handle_response(response)
            if result and "access_token" in result:
                self.set_token(result["access_token"])
            return result
        except Exception as e:
            logger.error(f"Login error: {e}")
            return None
    
    # User Endpoints
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user profile"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/me",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    def update_user_profile(self, user_data: Dict) -> Optional[Dict]:
        """Update user profile"""
        try:
            response = requests.put(
                f"{self.base_url}/api/users/me",
                json=user_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            return None
    
    def get_user_enrollments(self) -> Optional[List]:
        """Get user's course enrollments"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/me/enrollments",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get enrollments error: {e}")
            return None
    
    def get_user_stats(self) -> Optional[Dict]:
        """Get user statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/me/stats",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return None
    
    # Course Endpoints
    
    def get_all_courses(self, skip: int = 0, limit: int = 100) -> Optional[List]:
        """Get all courses"""
        try:
            response = requests.get(
                f"{self.base_url}/api/courses/",
                params={"skip": skip, "limit": limit},
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get courses error: {e}")
            return None
    
    def get_course(self, course_id: str) -> Optional[Dict]:
        """Get specific course"""
        try:
            response = requests.get(
                f"{self.base_url}/api/courses/{course_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get course error: {e}")
            return None
    
    def enroll_in_course(self, course_id: str, mode: str = "enroll") -> Optional[Dict]:
        """Enroll in a course"""
        data = {"course_id": course_id, "mode": mode}
        try:
            response = requests.post(
                f"{self.base_url}/api/courses/enroll",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Enrollment error: {e}")
            return None
    
    def drop_course(self, enrollment_id: int) -> Optional[Dict]:
        """Drop a course"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/courses/enroll/{enrollment_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Drop course error: {e}")
            return None
    
    def get_courses_by_category(self, category: str) -> Optional[List]:
        """Get courses by category"""
        try:
            response = requests.get(
                f"{self.base_url}/api/courses/category/{category}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get category courses error: {e}")
            return None
    
    # Recommendation Endpoints
    
    def get_recommendations(self, user_query: str, major: str, 
                          career_goal: str = "", experience_level: str = "Beginner") -> Optional[List]:
        """Get course recommendations"""
        data = {
            "query": user_query,
            "major": major,
            "career_goal": career_goal,
            "experience_level": experience_level
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/recommendations/",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get recommendations error: {e}")
            return None
    
    def generate_schedule(self, major: str, program: str) -> Optional[Dict]:
        """Generate personalized schedule"""
        params = {"major": major, "program": program}
        try:
            response = requests.get(
                f"{self.base_url}/api/recommendations/schedule",
                params=params,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Generate schedule error: {e}")
            return None
    
    # Chat Endpoints
    
    def send_chat_message(self, message: str) -> Optional[Dict]:
        """Send chat message to AI"""
        data = {"message": message}
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return None
    
    def get_chat_history(self) -> Optional[List]:
        """Get user's chat history"""
        try:
            response = requests.get(
                f"{self.base_url}/api/chat/history",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get history error: {e}")
            return None
    
    # Feedback Endpoints
    
    def submit_feedback(self, course_id: str, rating: int, comment: str) -> Optional[Dict]:
        """Submit course feedback"""
        data = {
            "course_id": course_id,
            "rating": rating,
            "comment": comment
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/feedback/",
                json=data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Submit feedback error: {e}")
            return None
    
    def get_my_feedback(self) -> Optional[List]:
        """Get user's feedback"""
        try:
            response = requests.get(
                f"{self.base_url}/api/feedback/my-feedback",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get feedback error: {e}")
            return None
    
    def get_course_feedback(self, course_id: str) -> Optional[List]:
        """Get feedback for a course"""
        try:
            response = requests.get(
                f"{self.base_url}/api/feedback/course/{course_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Get course feedback error: {e}")
            return None
    
    # Health Check
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# Global API client instance
def get_api_client() -> APIClient:
    """Get or create API client instance"""
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    return st.session_state.api_client
