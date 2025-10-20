import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

import sys
import os
import hashlib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import networkx as nx

# Import enhanced AI advisor
from advisor.enhanced_ai_advisor import EnhancedAIAdvisor

# Import calendar and realtime components
from calendar_view import render_full_calendar
from realtime_hub import render_realtime_hub

# Page configuration
st.set_page_config(
    page_title="Harbour Space Academic Advisor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hub-Style Clean CSS Design
st.markdown("""
            
<style>

    /* Black Background - Hub Style */
    .stApp {
        background: #000000;
    }
    
    [data-testid="stAppViewContainer"] {
        background: #000000;
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Main Container - Dark Hub Design */
    .main .block-container {
        padding: 2rem;
        max-width: 1400px;
        background: #0a0a0a;
        border-radius: 12px;
        margin: 2rem auto;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.05);
        border: 1px solid #1a1a1a;
    }
    
    /* Header - Simple Solid Color */
    .main-header {
        font-size: 2.8rem;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        color: #ffffff;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2a2a2a;
    }
    
    /* Tab Navigation - Clean Hub Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #1a1a1a;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #2a2a2a;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background: transparent;
        border-radius: 6px;
        font-weight: 500;
        color: #888888;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: #2563eb;
        color: white;
    }
    
    /* Metric Cards - Simple Dark Design */
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-card h3 {
        color: #2563eb;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Course Cards - Dark Theme */
    .course-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #2a2a2a;
        transition: all 0.2s;
        margin-bottom: 1rem;
    }
    
    .course-card:hover {
        border-color: #2563eb;
        background: #222222;
    }
    
    /* Login Container - Dark */
    .login-container {
        max-width: 450px;
        margin: 3rem auto;
        padding: 2.5rem;
        background: #1a1a1a;
        border-radius: 12px;
        border: 1px solid #2a2a2a;
    }
    
    /* Chat Messages - Dark Theme */
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        max-width: 85%;
    }
    
    .chat-message.user {
        background: #1e3a8a;
        border: 1px solid #2563eb;
        margin-left: auto;
        color: #ffffff;
    }
    
    .chat-message.assistant {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        color: #ffffff;
    }
    
    /* Buttons - Solid Blue */
    .stButton>button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }
    
    /* Form Submit Buttons - FORCE BLUE - Aggressive Override */
    .stButton>button[kind="primary"],
    button[kind="primary"],
    button[type="submit"],
    .stForm button,
    .stForm button[kind="primary"],
    form button,
    form button[type="submit"],
    div[data-testid="stForm"] button,
    [data-testid="baseButton-primary"],
    .stButton button[data-testid="baseButton-primary"] {
        background-color: #2563eb !important;
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
    }
    
    .stButton>button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    button[type="submit"]:hover,
    .stForm button:hover,
    form button:hover,
    div[data-testid="stForm"] button:hover,
    [data-testid="baseButton-primary"]:hover,
    .stButton button[data-testid="baseButton-primary"]:hover {
        background-color: #1d4ed8 !important;
        background: #1d4ed8 !important;
    }
    
    /* Smart Planner Action Buttons - Enhanced */
    div[data-testid="column"] .stButton>button {
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }
    
    div[data-testid="column"] .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.5);
    }
    
    /* Input Fields - Dark Theme */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 6px;
        border: 1px solid #2a2a2a;
        padding: 0.625rem;
        background: #1a1a1a;
        color: #ffffff;
    }
    
    /* Password Input - MASSIVE PADDING to push text away */
    .stTextInput>div>div>input[type="password"] {
        padding-right: 5rem !important;
    }
    
    /* Make input container wider to accommodate */
    .stTextInput>div {
        width: 100% !important;
    }
    
    /* Remove eye icon background color */
    .stTextInput button[kind="icon"],
    .stTextInput button[aria-label*="password"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* HIDE HELPER TEXT */
    .stForm [data-baseweb="helper-text"],
    .stForm div[role="alert"],
    .stForm small,
    form small {
        display: none !important;
    }

    
    .stTextInput>div>div>input:focus, 
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #2563eb;
        background: #222222;
    }
    
    /* Timeline - Dark */
    .timeline-module {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #2a2a2a;
    }
    
    /* Sidebar - Dark */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid #2a2a2a;
    }
    
    /* Success/Info/Warning/Error - Dark Theme */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 6px;
        border-width: 1px;
    }
    
    /* General Text Color */
    p, span, div, label {
        color: #e0e0e0;
    }
    
    /* Streamlit Elements Dark Theme */
    .stMarkdown {
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = None
if 'student_skills' not in st.session_state:
    st.session_state.student_skills = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'enrolled_courses' not in st.session_state:
    st.session_state.enrolled_courses = {}
if 'completed_courses' not in st.session_state:
    st.session_state.completed_courses = {}
if 'course_feedback' not in st.session_state:
    st.session_state.course_feedback = {}
if 'course_ratings' not in st.session_state:
    st.session_state.course_ratings = {}
if 'course_difficulty_feedback' not in st.session_state:
    st.session_state.course_difficulty_feedback = {}

# AI Advisor class
class AcademicAIAdvisor:
    def __init__(self):
        self.courses_df = None
        self.programs_df = None
        self.students_df = None
        self.lecturers_df = None
        self.enhanced_advisor = EnhancedAIAdvisor()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def load_data(self, courses_df, programs_df, students_df, lecturers_df=None):
        self.courses_df = courses_df
        self.programs_df = programs_df
        self.students_df = students_df
        self.lecturers_df = lecturers_df
        
        # Load enhanced advisor
        if lecturers_df is not None:
            self.enhanced_advisor.load_data(courses_df, lecturers_df, programs_df)
        
        self._prepare_course_features()
    
    def _prepare_course_features(self):
        """Prepare course features for similarity analysis"""
        if self.courses_df is not None and not self.courses_df.empty:
            course_texts = []
            for _, course in self.courses_df.iterrows():
                text = f"{course['course_name']} {course['course_description']} {course['skills_covered_str']} {course['category']}"
                course_texts.append(text)
            
            self.course_features = self.tfidf_vectorizer.fit_transform(course_texts)
    
    def generate_smart_schedule(self, student_id):
        """Generate optimized schedule based on major and course types"""
        student = self.get_student_profile(student_id)
        major = student.get('major', 'Computer Science')
        
        # Get courses for the student's major
        major_courses = self.courses_df[self.courses_df['category'].str.contains(major, case=False, na=False)].copy()
        
        if major_courses.empty:
            major_courses = self.courses_df.copy()
        
        # Get student's enrolled and completed courses
        enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
        completed_courses = st.session_state.completed_courses.get(student_id, [])
        
        # Filter out already enrolled or completed courses
        available_courses = major_courses[
            ~major_courses['course_id'].isin(enrolled_courses + completed_courses)
        ]
        
        # Apply feedback-based adjustments
        available_courses = self._apply_feedback_adjustments(available_courses, student_id)
        
        # Classify courses
        mandatory_courses = available_courses[available_courses['course_type'] == 'mandatory']
        secondary_courses = available_courses[available_courses['course_type'] == 'secondary']
        audit_courses = available_courses[available_courses['course_type'] == 'audit']
        
        # Create module schedule with actual dates
        modules = self._create_module_schedule(mandatory_courses, secondary_courses, audit_courses, major)
        
        return modules
    
    def _apply_feedback_adjustments(self, courses, student_id):
        """Adjust course recommendations based on student feedback"""
        if courses.empty:
            return courses
            
        # Get student's previous feedback
        student_feedback = st.session_state.course_ratings.get(student_id, {})
        difficulty_feedback = st.session_state.course_difficulty_feedback.get(student_id, {})
        
        # Create a copy to avoid modifying the original
        adjusted_courses = courses.copy()
        
        # Add feedback scores
        feedback_scores = []
        for _, course in adjusted_courses.iterrows():
            score = 0
            
            # Adjust based on course ratings from similar students
            course_id = course['course_id']
            if course_id in student_feedback:
                # Student's own rating
                score += student_feedback[course_id] * 2
            
            # Adjust based on difficulty feedback
            if course_id in difficulty_feedback:
                student_level = self.get_student_profile(student_id).get('experience_level', 'Beginner')
                if difficulty_feedback[course_id] == 'too_easy' and student_level == 'Advanced':
                    score += 1
                elif difficulty_feedback[course_id] == 'too_hard' and student_level == 'Beginner':
                    score -= 1
            
            # Consider course popularity from feedback
            global_ratings = self._get_global_course_ratings()
            if course_id in global_ratings:
                score += global_ratings[course_id] * 0.5
            
            feedback_scores.append(score)
        
        adjusted_courses['feedback_score'] = feedback_scores
        adjusted_courses = adjusted_courses.sort_values('feedback_score', ascending=False)
        
        return adjusted_courses
    
    def _get_global_course_ratings(self):
        """Get aggregated course ratings from all students"""
        global_ratings = {}
        for student_id, ratings in st.session_state.course_ratings.items():
            for course_id, rating in ratings.items():
                if course_id not in global_ratings:
                    global_ratings[course_id] = []
                global_ratings[course_id].append(rating)
        
        # Calculate average ratings
        avg_ratings = {}
        for course_id, ratings in global_ratings.items():
            avg_ratings[course_id] = sum(ratings) / len(ratings)
        
        return avg_ratings
    
    def _create_module_schedule(self, mandatory_courses, secondary_courses, audit_courses, major):
        """Create module schedule with actual dates"""
        modules = {}
        start_date = datetime.now()
        
        # Convert DataFrames to lists of courses (handle empty cases)
        mandatory_list = []
        if not mandatory_courses.empty:
            mandatory_list = [mandatory_courses.iloc[i] for i in range(min(3, len(mandatory_courses)))]
        
        secondary_list = []
        if not secondary_courses.empty:
            secondary_list = [secondary_courses.iloc[i] for i in range(min(2, len(secondary_courses)))]
        
        audit_list = []
        if not audit_courses.empty:
            audit_list = [audit_courses.iloc[i] for i in range(min(1, len(audit_courses)))]
        
        # Module 1: Focus on mandatory courses
        if mandatory_list:
            module1_courses = mandatory_list[:2] + secondary_list[:1]
            modules['Module 1'] = {
                'courses': module1_courses,
                'start_date': start_date,
                'end_date': start_date + timedelta(weeks=3),
                'total_credits': sum(c['credits'] for c in module1_courses),
                'description': f'Foundation courses for {major}'
            }
        
        # Module 2: Mix of mandatory and secondary
        if len(mandatory_list) > 2 or secondary_list:
            module2_courses = []
            if len(mandatory_list) > 2:
                module2_courses.extend(mandatory_list[2:4])
            if len(secondary_list) > 1:
                module2_courses.extend(secondary_list[1:2])
                
            if module2_courses:
                modules['Module 2'] = {
                    'courses': module2_courses,
                    'start_date': start_date + timedelta(weeks=3),
                    'end_date': start_date + timedelta(weeks=6),
                    'total_credits': sum(c['credits'] for c in module2_courses),
                    'description': f'Advanced {major} concepts'
                }
        
        # Module 3: Specialization and electives
        if audit_list or len(secondary_list) > 2:
            module3_courses = []
            if audit_list:
                module3_courses.extend(audit_list)
            if len(secondary_list) > 2:
                module3_courses.extend(secondary_list[2:3])
                
            if module3_courses:
                modules['Module 3'] = {
                    'courses': module3_courses,
                    'start_date': start_date + timedelta(weeks=6),
                    'end_date': start_date + timedelta(weeks=9),
                    'total_credits': sum(c['credits'] for c in module3_courses),
                    'description': f'{major} specialization and electives'
                }
        
        return modules
    
    def process_natural_language_query(self, query, student_id):
        """Enhanced AI assistant with better understanding using EnhancedAIAdvisor"""
        student = self.get_student_profile(student_id)
        
        # Use enhanced advisor if available
        if self.lecturers_df is not None:
            courses, explanations, response = self.enhanced_advisor.get_intelligent_recommendations(
                student,
                query=query,
                limit=6
            )
            return {
                'courses': courses,
                'explanations': explanations,
                'response': response
            }
        
        # Fallback to legacy method
        major = student.get('major', 'Computer Science')
        query_lower = self._normalize_query(query)
        relevant_courses = self._find_relevant_courses(query_lower, major)
        explanations = self._generate_course_explanations(relevant_courses, query_lower, major, student)
        response = self._generate_ai_response(relevant_courses, explanations, query_lower, major)
        
        return {
            'courses': relevant_courses,
            'explanations': explanations,
            'response': response
        }
    
    def _normalize_query(self, query):
        """Normalize query for better matching"""
        query = query.lower()
        
        # Common misspellings and shortcuts
        corrections = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ds': 'data science',
            'cs': 'computer science',
            'cyber': 'cybersecurity',
            'web dev': 'web development',
            'ux': 'user experience',
            'ui': 'user interface',
            'db': 'database',
            'algos': 'algorithms',
            'stats': 'statistics',
            'math': 'mathematics',
            'prog': 'programming',
            'soft eng': 'software engineering',
            'data struct': 'data structures',
            'networking': 'network',
            'cloud comp': 'cloud computing'
        }
        
        for wrong, correct in corrections.items():
            query = query.replace(wrong, correct)
        
        return query
    
    def _find_relevant_courses(self, query, major):
        """Find courses relevant to query and major"""
        if self.courses_df is None or self.courses_df.empty:
            return pd.DataFrame()
            
        # Priority 1: Courses matching query in major
        major_courses = self.courses_df[self.courses_df['category'].str.contains(major, case=False, na=False)]
        query_matches = major_courses[
            major_courses['course_name'].str.contains(query, case=False, na=False) |
            major_courses['course_description'].str.contains(query, case=False, na=False) |
            major_courses['skills_covered_str'].str.contains(query, case=False, na=False)
        ]
        
        # Priority 2: Mandatory courses in major
        mandatory_courses = major_courses[major_courses['course_type'] == 'mandatory']
        
        # Priority 3: Courses with high relevance to major
        relevant_keywords = self._get_major_keywords(major)
        relevant_courses = major_courses[
            major_courses['course_description'].str.contains('|'.join(relevant_keywords), case=False, na=False)
        ]
        
        # Combine and return top courses
        all_relevant = pd.concat([query_matches, mandatory_courses, relevant_courses]).drop_duplicates()
        
        # Score and sort by relevance
        all_relevant = self._score_courses_by_relevance(all_relevant, query, major)
        
        return all_relevant.head(6)
    
    def _get_major_keywords(self, major):
        """Get relevant keywords for each major"""
        keywords = {
            'Computer Science': ['programming', 'algorithm', 'software', 'development', 'code', 'computer'],
            'Data Science': ['data', 'analysis', 'statistics', 'machine learning', 'python', 'analytics'],
            'Cybersecurity': ['security', 'network', 'cyber', 'encryption', 'hacking', 'protection'],
            'Business': ['business', 'management', 'strategy', 'marketing', 'finance', 'leadership'],
            'Design': ['design', 'user', 'interface', 'experience', 'visual', 'creative']
        }
        return keywords.get(major, ['programming', 'technology', 'development'])
    
    def _score_courses_by_relevance(self, courses, query, major):
        """Score courses by relevance to query and major"""
        scores = []
        for _, course in courses.iterrows():
            score = 0
            
            # Course type scoring
            if course['course_type'] == 'mandatory':
                score += 3
            elif course['course_type'] == 'secondary':
                score += 2
            else:
                score += 1
            
            # Query matching
            course_text = f"{course['course_name']} {course['course_description']}".lower()
            if query in course_text:
                score += 2
            
            # Major relevance
            major_keywords = self._get_major_keywords(major)
            for keyword in major_keywords:
                if keyword in course_text:
                    score += 1
            
            scores.append(score)
        
        courses = courses.copy()
        courses['relevance_score'] = scores
        return courses.sort_values('relevance_score', ascending=False)
    
    def _generate_course_explanations(self, courses, query, major, student):
        """Generate explanations for why courses are recommended"""
        explanations = {}
        
        for _, course in courses.iterrows():
            explanation = []
            course_type = course.get('course_type', 'secondary')
            
            # Course type explanation
            if course_type == 'mandatory':
                explanation.append(f"**Mandatory for {major} major** - Core requirement that cannot be skipped")
                explanation.append("Required for degree completion - 6 credits")
            elif course_type == 'secondary':
                explanation.append(f"**Secondary course** - Graded elective that complements your major")
                explanation.append("Counts towards specialization - 4 credits")
            else:
                explanation.append(f"**Audit option** - Learn without grading pressure")
                explanation.append("Perfect for exploring new areas - 0 credits")
            
            # Career relevance
            career_goal = student.get('career_goal', '')
            if career_goal:
                if 'data' in career_goal.lower() and any(word in str(course['skills_covered_str']).lower() for word in ['python', 'statistics', 'machine learning']):
                    explanation.append(f"Essential for your career goal: {career_goal}")
                elif 'software' in career_goal.lower() and any(word in str(course['skills_covered_str']).lower() for word in ['programming', 'development', 'web']):
                    explanation.append(f"Core skills for your career: {career_goal}")
            
            # Query relevance
            if query and any(word in str(course['course_description']).lower() for word in query.split()):
                explanation.append(f"Directly addresses your interest in '{query}'")
            
            # Skill development
            skills = course.get('skills_covered_str', '')
            if skills:
                key_skills = skills.split(',')[:3]
                explanation.append(f"Develops key skills: {', '.join(key_skills)}")
            
            explanations[course['course_id']] = explanation
        
        return explanations
    
    def _generate_ai_response(self, courses, explanations, query, major):
        """Generate natural AI response"""
        if courses.empty:
            return "I couldn't find specific courses matching your query. Could you provide more details about what you're looking for? For example, you could ask about 'machine learning courses', 'web development', or 'required courses for my major'."
        
        response = f"Based on your interest in '{query}', here are my recommendations for your {major} major:\n\n"
        
        for _, course in courses.iterrows():
            course_explanations = explanations.get(course['course_id'], [])
            course_type = course.get('course_type', 'secondary')
            
            response += f"**{course['course_name']}** ({course['course_id']}) - {course_type.title()}\n"
            
            for exp in course_explanations:
                response += f"- {exp}\n"
            
            response += f"Duration: {course['duration_weeks']} weeks | Professor: {course['professor']}\n"
            response += f"Schedule: 3 hours daily | Credits: {course['credits']}\n\n"
        
        response += "**Would you like me to:**\n"
        response += "- Suggest alternative courses\n"
        response += "- Explain why certain courses are mandatory\n"
        response += "- Help you build a full schedule\n"
        response += "- Provide more details about any course"
        
        return response
    
    def get_student_profile(self, student_id):
        """Get student profile"""
        if student_id in st.session_state.user_data:
            return st.session_state.user_data[student_id]
        else:
            return {
                'completed_courses': [],
                'current_gpa': 0.0,
                'major': 'Computer Science',
                'career_goal': 'Software Engineer',
                'experience_level': 'Beginner'
            }
    
    def suggest_alternative_courses(self, current_course, student_id):
        """Suggest alternative courses"""
        student = self.get_student_profile(student_id)
        major = student.get('major', 'Computer Science')
        
        # Get courses of same type but different topic
        same_type_courses = self.courses_df[
            (self.courses_df['course_type'] == current_course['course_type']) &
            (self.courses_df['category'].str.contains(major, case=False, na=False)) &
            (self.courses_df['course_id'] != current_course['course_id'])
        ]
        
        return same_type_courses.head(3)

# Enhanced Login System
def modern_login_system():
    # Check if user info is saved in session
    if 'saved_user' in st.session_state and st.session_state.saved_user:
        saved = st.session_state.saved_user
        st.session_state.authenticated = True
        st.session_state.current_user = saved['student_id']
        if saved['student_id'] not in st.session_state.user_data:
            st.session_state.user_data[saved['student_id']] = saved
        st.rerun()
    
    # Professional centered header
    st.markdown("""
    <div style="text-align: center; margin: 2rem auto 3rem; max-width: 800px;">
        <h1 style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem;">
            HARBOUR.SPACE
        </h1>
        <p style="color: #64748b; font-size: 1.2rem; font-weight: 500; margin: 0.5rem 0;">
            ADVANCED ACADEMIC HUB
        </p>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem;">
            Next-Generation Learning Management & Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centered feature cards
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    feat_col1, feat_col2, feat_col3, feat_col4, feat_col5 = st.columns([1, 2, 2, 2, 1])
    
    with feat_col2:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #1e40af; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;">Smart Planning</div>
            <div style="color: #64748b; font-size: 0.8rem;">AI-Powered Selection</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #6d28d9; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;">AI Assistant</div>
            <div style="color: #64748b; font-size: 0.8rem;">24/7 Guidance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col4:
        st.markdown("""
        <div style="background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="color: #be185d; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;">Analytics</div>
            <div style="color: #64748b; font-size: 0.8rem;">Progress Tracking</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Centered login form
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            st.markdown("<h3 style='text-align: center;'>Welcome Back</h3>", unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="student@harbour.space")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember me")
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                
                if submit:
                    if email and password:
                        student_id = f"HS{np.random.randint(10000, 99999)}"
                        st.session_state.authenticated = True
                        st.session_state.current_user = student_id
                        user_info = {
                            'email': email,
                            'student_id': student_id,
                            'major': 'Computer Science',
                            'program': 'Bachelor',
                            'completed_courses': [],
                            'current_gpa': 0.0,
                            'completed_credits': 0,
                            'career_goal': 'Software Engineer'
                        }
                        st.session_state.user_data[student_id] = user_info
                        
                        # Remember user if checked
                        if remember_me:
                            st.session_state.saved_user = user_info
                        
                        st.rerun()
                    else:
                        st.error("Please enter valid credentials")
    
        with tab2:
            st.markdown("<h3 style='text-align: center;'>Join Harbour Space</h3>", unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
            
            with st.form("signup_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name", placeholder="John")
                    email = st.text_input("Email Address", placeholder="student@harbour.space")
                with col2:
                    last_name = st.text_input("Last Name", placeholder="Doe")
                    password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
                
                col3, col4 = st.columns(2)
                with col3:
                    program = st.selectbox("Program Level", 
                                         ["Bachelor's Degree", "Master's Degree", "Foundation", "Professional Certificate"])
                with col4:
                    major = st.selectbox("Field of Study", 
                                       ["Computer Science", "Data Science", "Cyber Security", "Front-End Development", 
                                        "Digital Marketing", "Interaction Design", "High-Tech Entrepreneurship"])
                
                career_goal = st.selectbox("Career Goal", 
                                         ["Software Engineer", "Data Scientist", "Cybersecurity Analyst", 
                                          "Product Manager", "UX Designer", "Business Analyst", "Marketing Specialist"])
                
                remember_me_signup = st.checkbox("Remember me", key="remember_signup")
                submit_signup = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if submit_signup:
                    if first_name and last_name and email and password:
                        student_id = f"HS{np.random.randint(10000, 99999)}"
                        st.session_state.authenticated = True
                        st.session_state.current_user = student_id
                        user_info = {
                            'name': f"{first_name} {last_name}",
                            'email': email,
                            'student_id': student_id,
                            'program': program,
                            'major': major,
                            'career_goal': career_goal,
                            'completed_courses': [],
                            'current_gpa': 0.0,
                            'completed_credits': 0,
                            'registration_date': datetime.now().strftime("%Y-%m-%d")
                        }
                        st.session_state.user_data[student_id] = user_info
                        
                        # Remember user if checked
                        if remember_me_signup:
                            st.session_state.saved_user = user_info
                        
                        st.success(f"Account created! Your Student ID: {student_id}")
                        st.rerun()
                    else:
                        st.error("Please fill all required fields")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Load and enhance course data using new comprehensive data loader
def load_datasets():
    try:
        from data_loader import data_loader
        
        courses_df, lecturers_df, programs_df = data_loader.load_all_datasets()
        
        # Create sample students data
        students_df = create_sample_students()
        
        st.success(f"Loaded {len(courses_df)} courses, {len(programs_df)} programs, and {len(lecturers_df)} lecturers")
        return courses_df, programs_df, students_df, lecturers_df
        
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
        import traceback
        traceback.print_exc()
        return create_fallback_data()

# Removed old enhance_courses_data and generate_course_id - using new data_loader.py

def create_sample_students():
    """Create sample students data"""
    n_students = 50
    return pd.DataFrame({
        'student_id': [f'HS{10000 + i}' for i in range(n_students)],
        'name': [f'Student {i}' for i in range(n_students)],
        'major': np.random.choice(['Computer Science', 'Data Science', 'Cybersecurity', 'Business'], n_students),
        'career_goal': np.random.choice(['Software Engineer', 'Data Scientist', 'Product Manager', 'UX Designer'], n_students),
        'current_gpa': np.round(np.random.uniform(2.5, 4.0, n_students), 2),
        'completed_credits': np.random.randint(0, 90, n_students)
    })

def create_fallback_data():
    """Create comprehensive fallback data"""
    courses_data = []
    base_courses = [
        ('Machine Learning Fundamentals', 'Data Science', 'mandatory', 'Advanced concepts in machine learning and AI'),
        ('Data Structures and Algorithms', 'Computer Science', 'mandatory', 'Fundamental computer science concepts'),
        ('Web Development', 'Computer Science', 'secondary', 'Full-stack web development'),
        ('Network Security', 'Cybersecurity', 'mandatory', 'Cybersecurity fundamentals and practices'),
        ('Business Strategy', 'Business', 'secondary', 'Strategic business planning and analysis'),
        ('User Experience Design', 'Design', 'audit', 'Principles of user-centered design'),
        ('Database Systems', 'Computer Science', 'mandatory', 'Database design and management'),
        ('Statistical Methods', 'Data Science', 'secondary', 'Statistical analysis for data science'),
        ('Cloud Computing', 'Computer Science', 'secondary', 'Cloud infrastructure and services'),
        ('Digital Marketing', 'Business', 'audit', 'Digital marketing strategies and tools'),
        ('Mobile Development', 'Computer Science', 'secondary', 'iOS and Android app development'),
        ('Ethical Hacking', 'Cybersecurity', 'mandatory', 'Penetration testing and security assessment'),
        ('Product Management', 'Business', 'secondary', 'Product development and management'),
        ('Visual Design', 'Design', 'audit', 'Graphic design principles and tools')
    ]
    
    professors = ["Dr. Elena Rodriguez", "Prof. Marcus Chen", "Dr. Sarah Johnson", "Prof. James Wilson"]
    
    for i, (name, category, course_type, description) in enumerate(base_courses):
        courses_data.append({
            'course_name': name,
            'category': category,
            'course_type': course_type,
            'credits': 6 if course_type == 'mandatory' else 4,
            'duration_weeks': 3,
            'course_description': description,
            'skills_covered_str': 'python, machine learning, data analysis, programming, design, business',
            'professor': professors[i % len(professors)],
            'course_id': generate_course_id({'category': category}),
            'estimated_difficulty': 'Intermediate'
        })
    
    # Create sample lecturers
    lecturers_data = pd.DataFrame({
        'lecturer_id': range(1, 5),
        'name': ['Dr. Elena Rodriguez', 'Prof. Marcus Chen', 'Dr. Sarah Johnson', 'Prof. James Wilson'],
        'job_title': ['CEO', 'CTO', 'Independent Consultant', 'Founder'],
        'company': ['AI Innovations Inc.', 'TechStart Ventures', 'Independent', 'SecureNet Startups'],
        'expertise_areas': ['Machine Learning, AI', 'Software Engineering, Cloud', 'Data Analysis, Statistics', 'Cybersecurity, Network Security'],
        'background': ['PhD in AI from Stanford', 'MS in CS from MIT', 'PhD in Data Science', 'PhD in Cybersecurity'],
        'email': ['elena@harbour.space', 'marcus@harbour.space', 'sarah@harbour.space', 'james@harbour.space']
    })
    
    return pd.DataFrame(courses_data), pd.DataFrame(), create_sample_students(), lecturers_data

# Feedback System Functions
def render_feedback_system():
    """Render the feedback system for AI Assistant and Platform"""
    st.markdown('<div class="section-header">Feedback & Complaints</div>', unsafe_allow_html=True)
    
    student_id = st.session_state.current_user
    
    st.write("Help us improve the AI Academic Advisor and platform. Your feedback matters!")
    
    # Create tabs for different feedback types
    feedback_tabs = st.tabs(["AI Assistant Feedback", "Platform Issues", "Feature Requests"])
    
    with feedback_tabs[0]:
        render_ai_feedback_form(student_id)
    
    with feedback_tabs[1]:
        render_platform_feedback_form(student_id)
    
    with feedback_tabs[2]:
        render_feature_request_form(student_id)

def render_ai_feedback_form(student_id):
    """Render feedback form for AI Assistant - professional design"""
    st.subheader("AI Assistant Feedback")
    st.write("Help us improve the AI's performance and accuracy")
    
    # Star rating with numbers
    st.markdown("**Overall Satisfaction:**")
    rating_cols = st.columns(5)
    ai_rating = 3
    for i in range(1, 6):
        with rating_cols[i-1]:
            if st.button(f"{i} Star{'' if i == 1 else 's'}", key=f"rating_{i}", use_container_width=True):
                ai_rating = i
    
    # Response quality with radio buttons
    response_quality = st.radio(
        "AI Response Quality:",
        ["Excellent", "Good", "Fair", "Poor"],
        horizontal=True,
        key="ai_quality"
    )
    
    # Feedback text areas
    what_worked = st.text_area(
        "What did the AI do well?",
        placeholder="e.g., Found relevant courses, understood my query, provided helpful information...",
        height=100,
        key="ai_worked"
    )
    
    what_improve = st.text_area(
        "What needs improvement?",
        placeholder="e.g., Didn't understand abbreviations, gave irrelevant results, missed key information...",
        height=100,
        key="ai_improve"
    )
    
    # Submit button with validation
    if st.button("Submit AI Feedback", key="submit_ai_feedback", type="primary", use_container_width=True):
        # Validate all fields are filled
        if not what_worked or not what_worked.strip():
            st.error("Please fill in 'What did the AI do well?' field")
        elif not what_improve or not what_improve.strip():
            st.error("Please fill in 'What needs improvement?' field")
        else:
            save_ai_feedback(student_id, ai_rating, response_quality, what_worked, what_improve)
            st.success("Thank you! Your feedback helps us train the AI better!")

def render_platform_feedback_form(student_id):
    """Render feedback form for platform issues"""
    st.subheader("Platform Issues & Complaints")
    st.write("Report bugs, technical issues, or complaints about the system.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Issue type
        issue_type = st.selectbox(
            "Type of Issue:",
            ["Bug/Error", "Performance Issue", "UI/UX Problem", "Data Incorrect", "Other"],
            key="issue_type"
        )
        
        # Severity
        severity = st.selectbox(
            "How severe is this issue?",
            ["Critical - Can't use the system", "Major - Significant problem", "Minor - Small annoyance"],
            key="issue_severity"
        )
    
    with col2:
        # Description
        issue_description = st.text_area(
            "Describe the issue:",
            placeholder="What happened? What were you trying to do?",
            height=150,
            key="issue_description"
        )
    
    # Submit button with validation
    if st.button("Submit Issue Report", key="submit_issue", type="primary"):
        # Validate description is filled
        if not issue_description or not issue_description.strip():
            st.error("Please describe the issue in detail")
        else:
            save_platform_issue(student_id, issue_type, severity, issue_description)
            st.success("Issue reported! Our team will investigate.")

def render_feature_request_form(student_id):
    """Render form for feature requests and mandatory course reasoning"""
    st.subheader("Feature Requests & Course Concerns")
    st.write("Suggest improvements or explain concerns about mandatory courses")
    
    # Tabs for different types of feedback
    concern_tabs = st.tabs(["Feature Suggestion", "Mandatory Course Concerns"])
    
    with concern_tabs[0]:
        # Feature description
        feature_title = st.text_input(
            "Feature Title:",
            placeholder="e.g., Add dark mode, Better search filters...",
            key="feature_title"
        )
        
        feature_description = st.text_area(
            "Describe the feature:",
            placeholder="What should it do? How would it help you?",
            height=120,
            key="feature_description"
        )
        
        # Priority
        priority = st.selectbox(
            "How important is this to you?",
            ["Nice to have", "Would be helpful", "Really need this!"],
            key="feature_priority"
        )
        
        # Submit button with validation
        if st.button("Submit Feature Request", key="submit_feature", type="primary", use_container_width=True):
            # Validate all fields are filled
            if not feature_title or not feature_title.strip():
                st.error("Please enter a feature title")
            elif not feature_description or not feature_description.strip():
                st.error("Please describe the feature in detail")
            else:
                save_feature_request(student_id, feature_title, feature_description, priority)
                st.success("Feature request submitted! We'll consider it for future updates.")
    
    with concern_tabs[1]:
        st.markdown("### Mandatory Course Concerns")
        st.write("If you have concerns about attending a mandatory course, please explain your reasoning. The academic team will review your case.")
        
        # Course selection
        enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
        mandatory_courses = []
        for course_id in enrolled_courses:
            course = get_course_by_id(course_id)
            if course is not None and course.get('course_type') == 'mandatory':
                mandatory_courses.append(f"{course['course_name']} ({course_id})")
        
        if not mandatory_courses:
            st.info("You don't have any mandatory courses enrolled yet.")
        else:
            selected_course = st.selectbox(
                "Which mandatory course are you concerned about?",
                mandatory_courses,
                key="concern_course"
            )
            
            # Reason category
            reason_category = st.selectbox(
                "Primary Reason:",
                [
                    "Schedule Conflict (work/personal)",
                    "Health/Medical Issues",
                    "Already Have Skills (prior experience)",
                    "Course Too Advanced/Difficult",
                    "Financial Constraints",
                    "Family/Personal Emergency",
                    "Other"
                ],
                key="reason_category"
            )
            
            # Detailed explanation
            detailed_reason = st.text_area(
                "Detailed Explanation:",
                placeholder="Please provide a detailed explanation of your situation. The academic team will review and may provide alternatives or accommodations...",
                height=150,
                key="detailed_reason"
            )
            
            # Supporting evidence
            has_evidence = st.checkbox("I can provide supporting documentation", key="has_evidence")
            
            # Alternative preference
            st.markdown("**Would you prefer:**")
            alternative = st.radio(
                "",
                ["Postpone to next module", "Switch to secondary/audit version", "Complete requirements differently", "Other arrangement"],
                key="alternative_pref"
            )
            
            # Submit with validation
            if st.button("Submit Concern to Academic Team", key="submit_concern", type="primary", use_container_width=True):
                # Validate detailed reason is filled
                if not detailed_reason or not detailed_reason.strip():
                    st.error("Please provide a detailed explanation for your concern")
                else:
                    save_mandatory_concern(student_id, selected_course, reason_category, detailed_reason, has_evidence, alternative)
                    st.success("Your concern has been submitted to the academic team. They will review and contact you within 48 hours.")

def save_ai_feedback(student_id, rating, quality, what_worked, what_improve):
    """Save AI feedback to session state"""
    if 'ai_feedback' not in st.session_state:
        st.session_state.ai_feedback = []
    
    st.session_state.ai_feedback.append({
        'student_id': student_id,
        'rating': rating,
        'quality': quality,
        'what_worked': what_worked,
        'what_improve': what_improve,
        'timestamp': pd.Timestamp.now()
    })

def save_platform_issue(student_id, issue_type, severity, description):
    """Save platform issue to session state"""
    if 'platform_issues' not in st.session_state:
        st.session_state.platform_issues = []
    
    st.session_state.platform_issues.append({
        'student_id': student_id,
        'issue_type': issue_type,
        'severity': severity,
        'description': description,
        'timestamp': pd.Timestamp.now()
    })

def save_feature_request(student_id, title, description, priority):
    """Save feature request to session state"""
    if 'feature_requests' not in st.session_state:
        st.session_state.feature_requests = []
    
    st.session_state.feature_requests.append({
        'student_id': student_id,
        'title': title,
        'description': description,
        'priority': priority,
        'timestamp': pd.Timestamp.now()
    })

def save_mandatory_concern(student_id, course, reason_category, detailed_reason, has_evidence, alternative):
    """Save mandatory course concern to session state"""
    if 'mandatory_concerns' not in st.session_state:
        st.session_state.mandatory_concerns = []
    
    st.session_state.mandatory_concerns.append({
        'student_id': student_id,
        'course': course,
        'reason_category': reason_category,
        'detailed_reason': detailed_reason,
        'has_evidence': has_evidence,
        'alternative': alternative,
        'timestamp': pd.Timestamp.now(),
        'status': 'Pending Review'
    })

def save_course_feedback(course_id, student_id, rating, difficulty_feedback, written_feedback):
    """Save course feedback to session state"""
    # Save rating
    if student_id not in st.session_state.course_ratings:
        st.session_state.course_ratings[student_id] = {}
    st.session_state.course_ratings[student_id][course_id] = rating
    
    # Save difficulty feedback
    if student_id not in st.session_state.course_difficulty_feedback:
        st.session_state.course_difficulty_feedback[student_id] = {}
    st.session_state.course_difficulty_feedback[student_id][course_id] = difficulty_feedback
    
    # Save written feedback
    if student_id not in st.session_state.course_feedback:
        st.session_state.course_feedback[student_id] = {}
    st.session_state.course_feedback[student_id][course_id] = written_feedback

def get_course_by_id(course_id):
    """Get course by ID from the dataset"""
    if st.session_state.ai_model and st.session_state.ai_model.courses_df is not None:
        courses_df = st.session_state.ai_model.courses_df
        course = courses_df[courses_df['course_id'] == course_id]
        if not course.empty:
            return course.iloc[0]
    return None

# Main Dashboard Components
def modern_dashboard():
    # Initialize AI Advisor
    if st.session_state.ai_model is None:
        st.session_state.ai_model = AcademicAIAdvisor()
        courses_df, programs_df, students_df, lecturers_df = load_datasets()
        st.session_state.ai_model.load_data(courses_df, programs_df, students_df, lecturers_df)
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown('<h1 class="main-header">AI Academic Advisor</h1>', unsafe_allow_html=True)
    with col2:
        student_data = st.session_state.user_data.get(st.session_state.current_user, {})
        st.metric("Student ID", student_data.get('student_id', st.session_state.current_user))
    with col3:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
    
    # Academic Overview
    st.markdown('<div class="section-header">Academic Overview</div>', unsafe_allow_html=True)
    
    student_data = st.session_state.user_data.get(st.session_state.current_user, {})
    completed_credits = student_data.get('completed_credits', 0)
    current_gpa = student_data.get('current_gpa', 0.0)
    major = student_data.get('major', 'Computer Science')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>0%</h3><p>Degree Progress</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>{current_gpa}/4.0</h3><p>Current GPA</p></div>', unsafe_allow_html=True)
    with col3:
        enrolled_count = len(st.session_state.enrolled_courses.get(st.session_state.current_user, []))
        st.markdown(f'<div class="metric-card"><h3>{enrolled_count}</h3><p>Courses Enrolled</p></div>', unsafe_allow_html=True)
    with col4:
        # Dynamic credit requirements based on program
        student_data = st.session_state.user_data.get(st.session_state.current_user, {})
        major = student_data.get('major', 'Computer Science')
        program = student_data.get('program', 'Bachelor')
        
        # Determine total required credits
        if program == 'Bachelor':
            total_required = 190
        elif major in ['Design', 'Marketing', 'Product Management']:  # Creative degrees
            total_required = 60
        else:
            total_required = 90  # Default for Master/PhD
        
        st.markdown(f'<div class="metric-card"><h3>{completed_credits}/{total_required}</h3><p>Credits Earned</p></div>', unsafe_allow_html=True)
    
    # Add spacing between overview and tabs
    st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    
    # Main Tabs - Fixed order
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Smart Path Planner", 
        "AI Assistant", 
        "Course Catalog", 
        "Progress",
        "Schedule Calendar",
        "Feedback",
        "My Profile"
    ])
    
    with tab1:
        render_smart_planner()
    with tab2:
        render_ai_assistant()
    with tab3:
        render_course_catalog()
    with tab4:
        render_progress_tracker()
    with tab5:
        render_schedule_calendar()
    with tab6:  
        render_feedback_system()
    with tab7:
        render_student_profile()

def render_student_profile():
    """Render student profile page with editable fields"""
    st.markdown('<div class="section-header">My Profile</div>', unsafe_allow_html=True)
    
    student_id = st.session_state.current_user
    student_data = st.session_state.user_data.get(student_id, {})
    
    st.write("Manage your academic profile and preferences.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Academic Information")
        
        # Major
        major = st.selectbox(
            "Major:",
            ["Computer Science", "Data Science", "Cybersecurity", "Business", "Design", "Marketing"],
            index=["Computer Science", "Data Science", "Cybersecurity", "Business", "Design", "Marketing"].index(student_data.get('major', 'Computer Science')),
            key="profile_major"
        )
        
        # Program
        program = st.selectbox(
            "Program Level:",
            ["Bachelor", "Master", "PhD"],
            index=["Bachelor", "Master", "PhD"].index(student_data.get('program', 'Bachelor')),
            key="profile_program"
        )
        
        # Experience Level
        experience = st.selectbox(
            "Experience Level:",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(student_data.get('experience_level', 'Beginner')),
            key="profile_experience"
        )
        
        # Career Goal
        career_goal = st.text_input(
            "Career Goal:",
            value=student_data.get('career_goal', ''),
            placeholder="e.g., Software Engineer, Data Scientist...",
            key="profile_career"
        )
    
    with col2:
        st.subheader("Learning Preferences")
        
        # Preferred time
        preferred_time = st.selectbox(
            "Preferred Class Time:",
            ["Morning", "Afternoon", "Evening", "No Preference"],
            index=["Morning", "Afternoon", "Evening", "No Preference"].index(student_data.get('preferred_time', 'No Preference')),
            key="profile_time"
        )
        
        # Study pace
        study_pace = st.selectbox(
            "Study Pace:",
            ["Fast track (more courses)", "Balanced", "Relaxed (fewer courses)"],
            index=1,
            key="profile_pace"
        )
        
        # Interests
        interests = st.text_area(
            "Areas of Interest:",
            value=student_data.get('interests', ''),
            placeholder="e.g., Machine Learning, Web Development, Cybersecurity...",
            height=100,
            key="profile_interests"
        )
    
    # Save button
    col_save1, col_save2, col_save3 = st.columns([1, 1, 2])
    with col_save1:
        if st.button("Save Profile", type="primary", use_container_width=True):
            # Check if major or program changed
            old_major = student_data.get('major', 'Computer Science')
            old_program = student_data.get('program', 'Bachelor')
            profile_changed = (major != old_major or program != old_program)
            
            # Update student data
            st.session_state.user_data[student_id].update({
                'major': major,
                'program': program,
                'experience_level': experience,
                'career_goal': career_goal,
                'preferred_time': preferred_time,
                'study_pace': study_pace,
                'interests': interests
            })
            
            # If major/program changed, clear enrolled courses to regenerate planner
            if profile_changed:
                if 'profile_change_cleared' not in st.session_state:
                    st.session_state.profile_change_cleared = {}
                st.session_state.profile_change_cleared[student_id] = True
                st.success(f"Profile updated! Your Smart Planner will show courses for {major} ({program}).")
            else:
                st.success("Profile updated successfully!")
            st.rerun()
    
    with col_save2:
        if st.button("Reset to Defaults", use_container_width=True):
            st.session_state.user_data[student_id] = {
                'major': 'Computer Science',
                'program': 'Bachelor',
                'experience_level': 'Beginner',
                'career_goal': '',
                'preferred_time': 'No Preference',
                'study_pace': 'Balanced',
                'interests': ''
            }
            st.rerun()
    
    # Academic Preferences Section (removed enrollment stats as requested)
    st.divider()
    st.markdown("### Academic Goals & Interests")
    
    # Academic targets
    target_col1, target_col2 = st.columns(2)
    with target_col1:
        target_gpa = st.number_input(
            "Target GPA:",
            min_value=0.0,
            max_value=4.0,
            value=student_data.get('target_gpa', 3.5),
            step=0.1,
            key="target_gpa"
        )
    
    with target_col2:
        graduation_year = st.selectbox(
            "Expected Graduation:",
            ["2025", "2026", "2027", "2028", "2029"],
            index=["2025", "2026", "2027", "2028", "2029"].index(student_data.get('graduation_year', '2026')),
            key="graduation_year"
        )
    
    # Academic strengths
    strengths = st.multiselect(
        "Your Academic Strengths:",
        ["Mathematics", "Programming", "Data Analysis", "Design", "Writing", "Presentation", "Research", "Team Work"],
        default=student_data.get('strengths', []),
        key="strengths"
    )
    
    # Learning challenges
    challenges = st.text_area(
        "Areas You Want to Improve:",
        value=student_data.get('challenges', ''),
        placeholder="e.g., Public speaking, Time management, Advanced mathematics...",
        height=80,
        key="challenges"
    )

def render_smart_planner():
    """Render smart planner using enhanced UI components"""
    from ui_components import render_enhanced_smart_planner
    
    student_id = st.session_state.current_user
    student_data = st.session_state.user_data.get(student_id, {})
    
    render_enhanced_smart_planner(st.session_state.ai_model, student_id, student_data)
    return
    
    # Legacy code below (kept as fallback)
    st.markdown('<div class="section-header">Smart Path Planner</div>', unsafe_allow_html=True)
    
    student_data = st.session_state.user_data.get(st.session_state.current_user, {})
    major = student_data.get('major', 'Computer Science')
    
    st.subheader(f"Personalized Academic Plan for {major}")
    st.write("This plan is optimized for your major with proper course sequencing and workload balance.")
    
    # Generate schedule
    schedule = st.session_state.ai_model.generate_smart_schedule(st.session_state.current_user)
    
    if not schedule:
        st.info("No courses available for planning. Please check the course catalog or contact administration.")
        return
    
    # Display timeline
    st.subheader("Academic Timeline")
    
    timeline_data = []
    for module_name, module_data in schedule.items():
        timeline_data.append({
            'Module': module_name,
            'Start': module_data['start_date'],
            'End': module_data['end_date'],
            'Courses': len(module_data['courses']),
            'Credits': module_data['total_credits'],
            'Description': module_data.get('description', '')
        })
    
    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create Gantt chart
        fig = px.timeline(
            timeline_df, 
            x_start="Start", 
            x_end="End", 
            y="Module",
            color="Credits",
            title="Academic Module Timeline",
            hover_data=["Courses", "Description"]
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Display modules in detail
    st.subheader("Module Details")
    
    for module_name, module_data in schedule.items():
        with st.expander(
            f"{module_name} | "
            f"{module_data['start_date'].strftime('%b %d, %Y')} - {module_data['end_date'].strftime('%b %d, %Y')} | "
            f"{module_data['total_credits']} credits | "
            f"{len(module_data['courses'])} courses",
            expanded=True
        ):
            
            st.write(f"**Description:** {module_data.get('description', 'Core academic module')}")
            st.write("**Schedule:** 3 hours daily per class | 3 classes per day | Monday to Friday")
            st.write("**Attendance Policy:** Maximum 3 absences allowed | Late arrival >10 minutes = absence | 3 absences = automatic failure")
            
            st.markdown("### Courses in this Module")
            
            for i, course in enumerate(module_data['courses']):
                # FIXED: Check if course is not None and is a dictionary/Series
                if course is not None and not isinstance(course, pd.Series):
                    # Convert Series to dict if needed
                    if hasattr(course, 'to_dict'):
                        course = course.to_dict()
                    
                    course_type = course.get('course_type', 'secondary')
                    card_class = f"course-card {course_type}"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{course['course_name']}</h4>
                        <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>Course ID:</strong> {course['course_id']} | 
                            <strong>Type:</strong> {course_type.title()} | 
                            <strong>Credits:</strong> {course['credits']}
                        </div>
                        <div style="color: #5a6c7d; font-size: 0.9rem;">
                            <strong>Professor:</strong> {course['professor']} | 
                            <strong>Duration:</strong> {course['duration_weeks']} weeks
                        </div>
                        <div style="color: #5a6c7d; font-size: 0.8rem; margin-top: 0.5rem;">
                            <strong>Skills:</strong> {course['skills_covered_str']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("View Details", key=f"view_{course['course_id']}_{i}", use_container_width=True):
                            show_course_details(course)
                    with col2:
                        if st.button("Enroll", key=f"enroll_{course['course_id']}_{i}", use_container_width=True):
                            enroll_course(course)
                    with col3:
                        if course_type != 'mandatory' and st.button("Swap", key=f"swap_{course['course_id']}_{i}", use_container_width=True):
                            show_alternative_courses(course)
                    
                    st.divider()
                elif isinstance(course, pd.Series):
                    # Handle Series case
                    course_dict = course.to_dict()
                    course_type = course_dict.get('course_type', 'secondary')
                    card_class = f"course-card {course_type}"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{course_dict['course_name']}</h4>
                        <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>Course ID:</strong> {course_dict['course_id']} | 
                            <strong>Type:</strong> {course_type.title()}
                        </div>
                        <div style="color: #5a6c7d; font-size: 0.9rem;">
                            <strong>Professor:</strong> {course_dict['professor']} | 
                            <strong>Duration:</strong> {course_dict['duration_weeks']} weeks
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons for Series
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("View Details", key=f"view_series_{course_dict['course_id']}_{i}", use_container_width=True):
                            show_course_details(course_dict)
                    with col2:
                        if st.button("Enroll", key=f"enroll_series_{course_dict['course_id']}_{i}", use_container_width=True):
                            enroll_course(course_dict)
                    
                    st.divider()

def show_course_details(course):
    """Show detailed course information in sidebar"""
    st.sidebar.markdown("### Course Details")
    st.sidebar.write(f"**{course['course_name']}**")
    st.sidebar.write(f"**Course ID:** {course['course_id']}")
    st.sidebar.write(f"**Type:** {course.get('course_type', 'secondary').title()}")
    st.sidebar.write(f"**Credits:** {course['credits']}")
    st.sidebar.write(f"**Duration:** {course['duration_weeks']} weeks")
    st.sidebar.write(f"**Professor:** {course['professor']}")
    st.sidebar.write(f"**Category:** {course['category']}")
    st.sidebar.write(f"**Difficulty:** {course.get('estimated_difficulty', 'Intermediate')}")
    st.sidebar.write("---")
    st.sidebar.write("**Description:**")
    st.sidebar.write(course['course_description'])
    st.sidebar.write("---")
    st.sidebar.write("**Skills Covered:**")
    st.sidebar.write(course['skills_covered_str'])
    st.sidebar.write("---")
    st.sidebar.write("**Attendance Policy:**")
    st.sidebar.write("- Maximum 3 absences allowed per course")
    st.sidebar.write("- Late arrival >10 minutes = 1 absence")
    st.sidebar.write("- 3 absences = automatic course failure")
    st.sidebar.write("- Mandatory attendance for all scheduled classes")
    st.sidebar.write("- Medical emergencies require official documentation")

def enroll_course(course):
    """Enroll student in a course with collision detection"""
    student_id = st.session_state.current_user
    if student_id not in st.session_state.enrolled_courses:
        st.session_state.enrolled_courses[student_id] = []
    
    # Check if already enrolled
    if course['course_id'] in st.session_state.enrolled_courses[student_id]:
        st.warning(f"You are already enrolled in {course['course_name']}")
        return
    
    # Check for timetable conflicts
    courses_df = st.session_state.ai_model.courses_df
    new_course_time = course.get('class_time', '')
    
    if new_course_time and new_course_time != 'TBD':
        # Get currently enrolled courses
        enrolled_course_ids = st.session_state.enrolled_courses[student_id]
        conflicting_courses = []
        
        for enrolled_id in enrolled_course_ids:
            # Parse course_id:mode format if present
            if ':' in str(enrolled_id):
                enrolled_id, _ = str(enrolled_id).split(':')
            
            enrolled_course_row = courses_df[courses_df['course_id'] == enrolled_id]
            if not enrolled_course_row.empty:
                enrolled_time = enrolled_course_row.iloc[0].get('class_time', '')
                if enrolled_time == new_course_time:
                    conflicting_courses.append({
                        'id': enrolled_id,
                        'name': enrolled_course_row.iloc[0]['course_name'],
                        'time': enrolled_time
                    })
        
        # If conflicts found, show error
        if conflicting_courses:
            st.error(f"**TIMETABLE CONFLICT DETECTED!**")
            st.error(f"**{course['course_name']}** ({new_course_time}) conflicts with:")
            for conflict in conflicting_courses:
                st.error(f"  - **{conflict['name']}** ({conflict['id']}) at {conflict['time']}")
            st.warning("You CANNOT enroll in courses with the same time slot!")
            st.info("Tip: Choose a course in a different time slot (Morning, Afternoon, or Evening)")
            return
    
    # No conflicts - proceed with enrollment
    st.session_state.enrolled_courses[student_id].append(course['course_id'])
    st.success(f"Successfully enrolled in {course['course_name']}!")
    
    if new_course_time and new_course_time != 'TBD':
        st.info(f"Class Time: {new_course_time}")
    
    # Update student data
    student_data = st.session_state.user_data[student_id]
    if 'enrolled_courses' not in student_data:
        student_data['enrolled_courses'] = []
    student_data['enrolled_courses'].append(course['course_id'])

def show_alternative_courses(current_course):
    """Show alternative courses in sidebar"""
    student_id = st.session_state.current_user
    alternatives = st.session_state.ai_model.suggest_alternative_courses(current_course, student_id)
    
    st.sidebar.markdown("### Alternative Courses")
    st.sidebar.write(f"Looking for alternatives to **{current_course['course_name']}**")
    
    if not alternatives.empty:
        for _, alt_course in alternatives.iterrows():
            st.sidebar.write(f"**{alt_course['course_name']}** ({alt_course['course_id']})")
            st.sidebar.write(f"Type: {alt_course['course_type'].title()} | Credits: {alt_course['credits']}")
            if st.sidebar.button(f"Enroll in {alt_course['course_id']}", key=f"alt_{alt_course['course_id']}"):
                enroll_course(alt_course)
            st.sidebar.write("---")
    else:
        st.sidebar.info("No alternative courses found for this selection.")

def render_ai_assistant():
    # Professional academic header
    st.markdown('''
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 600;">AI Academic Advisor</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">Intelligent Course Planning & Academic Guidance System</p>
    </div>
    ''', unsafe_allow_html=True)
    
    student_id = st.session_state.current_user
    student_data = st.session_state.user_data.get(student_id, {})
    major = student_data.get('major', 'Computer Science')
    program = student_data.get('program', 'Bachelor')
    career_goal = student_data.get('career_goal', '')
    
    # Professional context bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'''
        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <strong style="color: #1e40af;">Student Context:</strong> {major} | {program} {'| ' + career_goal if career_goal else ''}
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        if st.button("Clear Chat", use_container_width=True, help="Clear conversation history"):
            if student_id in st.session_state.chat_history:
                # Keep only the intro message
                intro = st.session_state.chat_history[student_id][0] if st.session_state.chat_history[student_id] else None
                st.session_state.chat_history[student_id] = [intro] if intro else []
            st.rerun()
    
    st.write("")
    
    # Initialize chat history with SHORT intro
    if student_id not in st.session_state.chat_history:
        st.session_state.chat_history[student_id] = [
            {
                "role": "assistant", 
                "content": f"""Welcome! I'm your Academic Advisor for **{major}**.

**I can help you with:**
- Course recommendations & discovery
- Faculty information & lecturers  
- Schedule planning & timings
- Academic guidance & preparation tips

Ask me anything!"""
            }
        ]
    
    # Use session state to track button clicks
    if 'process_query' not in st.session_state:
        st.session_state.process_query = None
    
    # Modern Messenger/Instagram-style chat UI - COMPACT
    st.markdown("### AI Chat")
    st.markdown("""
    <style>
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 16px;
        margin-bottom: 0.5rem;
        border: 1px solid #e9ecef;
    }
    
    /* User message bubble - right aligned, blue like iMessage */
    .user-bubble {
        display: flex;
        justify-content: flex-end;
        margin: 0.5rem 0;
    }
    .user-message {
        background: linear-gradient(135deg, #0084ff 0%, #00a3ff 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        box-shadow: 0 2px 4px rgba(0, 132, 255, 0.2);
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* AI message bubble - left aligned, gray like Instagram */
    .ai-bubble {
        display: flex;
        justify-content: flex-start;
        margin: 0.5rem 0;
    }
    .ai-message {
        background: #ffffff;
        color: #000000;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 18px 4px;
        max-width: 75%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* Avatar styling */
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.85rem;
        margin: 0 0.5rem;
    }
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .ai-avatar {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 0.7rem;
        color: #6c757d;
        margin: 0.2rem 0.5rem;
        text-align: center;
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #a0aec0;
    }
    </style>
    <div class="chat-container">
    """, unsafe_allow_html=True)
    
    # Show only last 15 messages with bubble styling
    recent_messages = st.session_state.chat_history[student_id][-15:]
    for message in recent_messages:
        if message["role"] == "user":
            # User bubble - right side, blue
            st.markdown(f'''
            <div class="user-bubble">
                <div class="user-message">{message["content"]}</div>
                <div class="avatar user-avatar">You</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            # AI bubble - left side, white
            st.markdown(f'''
            <div class="ai-bubble">
                <div class="avatar ai-avatar">AI</div>
                <div class="ai-message">{message["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input RIGHT BELOW chat - no scrolling needed!
    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Ask me anything:", 
                placeholder="Type your question: courses, lecturers, schedule, modules...",
                key="chat_input_field",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.form_submit_button("Send", use_container_width=True, type="primary")
        
        if send_button and user_input:
            st.session_state.process_query = user_input
    
    # Quick buttons - compact single row
    st.markdown("**Quick:** ")
    quick_cols = st.columns(6)
    quick_queries = ["ML courses", "Morning classes", "Lecturers", "Schedule", "Career advice", "Duration"]
    for i, q in enumerate(quick_queries):
        with quick_cols[i]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.process_query = q
    
    # Process the query
    if st.session_state.process_query:
        query = st.session_state.process_query
        st.session_state.process_query = None
        
        # Add user message to chat history
        st.session_state.chat_history[student_id].append({"role": "user", "content": query})
        
        # Get AI response
        with st.spinner("Thinking..."):
            try:
                response_data = st.session_state.ai_model.process_natural_language_query(query, student_id)
                
                # Add AI response to chat history
                st.session_state.chat_history[student_id].append({
                    "role": "assistant", 
                    "content": response_data['response']
                })
                
            except Exception as e:
                error_msg = f"I'm having trouble with that question. Please try rephrasing or ask about courses, lecturers, or schedules."
                st.session_state.chat_history[student_id].append({
                    "role": "assistant", 
                    "content": error_msg
                })
        
        # Rerun to update chat display
        st.rerun()

def render_course_catalog():
    """Render course catalog using enhanced UI components"""
    from ui_components import render_enhanced_course_catalog
    
    student_id = st.session_state.current_user
    student_data = st.session_state.user_data.get(student_id, {})
    
    render_enhanced_course_catalog(st.session_state.ai_model, student_data)
    return
    
    # Legacy code below (kept as fallback)
    st.markdown('<div class="section-header">Course Catalog</div>', unsafe_allow_html=True)
    
    student_data = st.session_state.user_data.get(st.session_state.current_user, {})
    major = student_data.get('major', 'Computer Science')
    
    st.write(f"Browse all available courses. Filter by your major ({major}) or explore other areas.")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        major_filter = st.selectbox("Filter by Major", 
                                  ["All", "Computer Science", "Data Science", "Cybersecurity", "Business", "Design"])
    with col2:
        type_filter = st.selectbox("Filter by Type", 
                                 ["All", "Mandatory", "Secondary", "Audit"])
    with col3:
        difficulty_filter = st.selectbox("Filter by Difficulty", 
                                       ["All", "Beginner", "Intermediate", "Advanced"])
    with col4:
        search_query = st.text_input("Search courses...", placeholder="Course name, skills, professor...")
    
    # Get filtered courses
    courses_df = st.session_state.ai_model.courses_df
    if courses_df is None or courses_df.empty:
        st.warning("No courses available in the catalog.")
        return
        
    filtered_courses = courses_df.copy()
    
    if major_filter != "All":
        filtered_courses = filtered_courses[filtered_courses['category'] == major_filter]
    if type_filter != "All":
        filtered_courses = filtered_courses[filtered_courses['course_type'] == type_filter.lower()]
    if difficulty_filter != "All":
        filtered_courses = filtered_courses[filtered_courses['estimated_difficulty'] == difficulty_filter]
    if search_query:
        search_lower = search_query.lower()
        filtered_courses = filtered_courses[
            filtered_courses['course_name'].str.contains(search_lower, case=False, na=False) |
            filtered_courses['course_description'].str.contains(search_lower, case=False, na=False) |
            filtered_courses['skills_covered_str'].str.contains(search_lower, case=False, na=False) |
            filtered_courses['professor'].str.contains(search_lower, case=False, na=False)
        ]
    
    # Display courses in grid
    st.write(f"**Found {len(filtered_courses)} courses**")
    
    if filtered_courses.empty:
        st.info("No courses match your filters. Try adjusting your search criteria.")
        return
    
    # Create grid layout - 3 columns
    cols = st.columns(3)
    
    for idx, course in filtered_courses.iterrows():
        col = cols[idx % 3]
        
        with col:
            course_type = course.get('course_type', 'secondary')
            card_class = f"course-card {course_type}"
            difficulty = course.get('estimated_difficulty', 'Intermediate')
            
            # Color code by difficulty
            difficulty_color = {
                'Beginner': '#2ecc71',
                'Intermediate': '#f39c12', 
                'Advanced': '#e74c3c'
            }.get(difficulty, '#95a5a6')
            
            st.markdown(f"""
            <div class="{card_class}">
                <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50; font-size: 1.1rem;">{course['course_name']}</h4>
                <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    <strong>ID:</strong> {course['course_id']} | 
                    <strong>Type:</strong> {course_type.title()}
                </div>
                <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    <strong>Credits:</strong> {course['credits']} | 
                    <strong>Duration:</strong> {course['duration_weeks']} weeks
                </div>
                <div style="color: #5a6c7d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    <strong>Professor:</strong> {course['professor']}
                </div>
                <div style="color: {difficulty_color}; font-size: 0.8rem; margin-bottom: 0.5rem;">
                    <strong>Level:</strong> {difficulty}
                </div>
                <div style="color: #5a6c7d; font-size: 0.8rem;">
                    <strong>Skills:</strong> {course['skills_covered_str'][:80]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Details", key=f"cat_det_{course['course_id']}_{idx}", use_container_width=True):
                    show_course_details(course)
            with btn_col2:
                if st.button("Enroll", key=f"cat_enr_{course['course_id']}_{idx}", use_container_width=True):
                    enroll_course(course)
            
            st.write("")  

def render_progress_tracker():
    """Completely redesigned - NO duplicate content"""
    st.markdown('<div class="section-header">My Academic Dashboard</div>', unsafe_allow_html=True)
    st.write("Track your courses, grades, and study schedule")
    
    student_id = st.session_state.current_user
    
    # Modern tabbed interface
    prog_tab1, prog_tab2, prog_tab3, prog_tab4 = st.tabs([
        "Course Timeline",
        "Grade Tracker", 
        "Study Schedule",
        "Academic Calendar"
    ])
    
    with prog_tab1:
        render_course_timeline(student_id)
    
    with prog_tab2:
        render_grade_tracker(student_id)
    
    with prog_tab3:
        render_study_schedule(student_id)
    
    with prog_tab4:
        render_academic_calendar(student_id)

def render_course_timeline(student_id):
    """Show detailed course progress timeline"""
    st.subheader("Course Progress Timeline")
    
    enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
    completed_courses = st.session_state.completed_courses.get(student_id, [])
    
    if not enrolled_courses and not completed_courses:
        st.info("No courses in progress. Visit Smart Path Planner to enroll!")
        return
    
    # Active Courses with Progress Tracking
    if enrolled_courses:
        st.markdown("### Currently Enrolled")
        courses_df = st.session_state.ai_model.courses_df
        
        for enroll_data in enrolled_courses:
            if ':' in str(enroll_data):
                course_id, mode = str(enroll_data).split(':')
            else:
                course_id = str(enroll_data)
                mode = 'enroll'
            
            course_row = courses_df[courses_df['course_id'] == course_id]
            if not course_row.empty:
                course = course_row.iloc[0]
                
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #667eea;">
                    <h4 style="margin: 0 0 0.5rem 0;">{course['course_name']}</h4>
                    <p style="color: #64748b; margin: 0;">{course_id} | {course.get('class_time', 'TBD')} | {mode.upper()}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    progress = st.slider("Completion", 0, 100, 0, key=f"prog_{course_id}", label_visibility="collapsed")
                with col2:
                    st.metric("Week", "1/3")
                with col3:
                    st.metric("Attendance", f"{3-0}/3")
    
    # Completed Courses
    if completed_courses:
        st.markdown("### Completed Courses")
        for course_id in completed_courses:
            st.success(f"Completed: {course_id}")

def render_grade_tracker(student_id):
    """Track grades and performance metrics"""
    st.subheader("Grade Tracker & Performance")
    
    enrolled_courses = st.session_state.enrolled_courses.get(student_id, [])
    
    if not enrolled_courses:
        st.info("No active courses to track grades.")
        return
    
    st.markdown("### Current Semester Grades")
    
    courses_df = st.session_state.ai_model.courses_df
    
    # Create grade tracking table
    for enroll_data in enrolled_courses:
        if ':' in str(enroll_data):
            course_id, mode = str(enroll_data).split(':')
        else:
            course_id = str(enroll_data)
            mode = 'enroll'
        
        course_row = courses_df[courses_df['course_id'] == course_id]
        if not course_row.empty:
            course = course_row.iloc[0]
            
            st.markdown(f"#### {course['course_name']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                attendance = st.number_input("Absences", 0, 10, 0, key=f"abs_{course_id}")
                if attendance >= 3:
                    st.error("FAILED - Too many absences")
            with col2:
                midterm = st.number_input("Midterm %", 0, 100, 0, key=f"mid_{course_id}")
            with col3:
                final = st.number_input("Final %", 0, 100, 0, key=f"fin_{course_id}")
            with col4:
                avg = (midterm + final) / 2 if (midterm + final) > 0 else 0
                if avg > 0:
                    grade = "A" if avg >= 90 else "B" if avg >= 80 else "C" if avg >= 70 else "D" if avg >= 60 else "F"
                    color = "#22c55e" if avg >= 80 else "#f59e0b" if avg >= 70 else "#ef4444"
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                        <h2 style="margin: 0;">{grade}</h2>
                        <p style="margin: 0; font-size: 0.9rem;">{avg:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")

def render_study_schedule(student_id):
    """Weekly study schedule planner"""
    st.subheader("Weekly Study Planner")
    
    st.markdown("### This Week's Study Plan")
    st.write("Plan your study hours and tasks for each day.")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    total_hours = 0
    for day in days:
        with st.expander(f"{day}", expanded=False):
            col1, col2 = st.columns([1, 3])
            with col1:
                hours = st.number_input("Study Hours", 0, 12, 0, key=f"hours_{day}")
                total_hours += hours
            with col2:
                st.text_area("Tasks", placeholder="Study materials, assignments, readings...", key=f"tasks_{day}", height=80)
    
    st.metric("Total Study Hours This Week", f"{total_hours} hours")
    
    if st.button("Save Study Plan", use_container_width=True):
        st.success("Study plan saved!")

def render_academic_calendar(student_id):
    """Academic calendar with important dates"""
    st.subheader("Academic Calendar & Deadlines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upcoming Deadlines")
        st.markdown("""
        - **Oct 25, 2025**: Assignment 1 - Machine Learning
        - **Oct 28, 2025**: Midterm Exam - Data Structures
        - **Nov 2, 2025**: Project Proposal - Web Development
        - **Nov 10, 2025**: Final Presentation - Cybersecurity
        """)
    
    with col2:
        st.markdown("### Important Dates")
        st.markdown("""
        - **Oct 23, 2025**: Module 2 Begins
        - **Oct 30, 2025**: Registration Opens
        - **Nov 15, 2025**: Final Exams Begin
        - **Dec 20, 2025**: Winter Break
        """)
    
    st.markdown("---")
    st.markdown("### Add Custom Reminder")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        reminder_text = st.text_input("Reminder", placeholder="e.g., Study for midterm")
    with col2:
        reminder_date = st.date_input("Date")
    with col3:
        st.write("")
        st.write("")
        if st.button("Add", use_container_width=True):
            st.success("Reminder added!")

# All old duplicate content deleted

def render_schedule_calendar():
    """Render schedule calendar tab"""
    student_id = st.session_state.current_user
    courses_df = st.session_state.ai_model.courses_df
    
    if courses_df is None or courses_df.empty:
        st.warning("No course data available. Please contact administration.")
        return
    
    render_full_calendar(student_id, courses_df)


def render_realtime_hub_tab():
    """Render real-time hub tab"""
    student_id = st.session_state.current_user
    courses_df = st.session_state.ai_model.courses_df
    
    if courses_df is None or courses_df.empty:
        st.warning("No course data available. Please contact administration.")
        return
    
    render_realtime_hub(student_id, courses_df)


# Main App Flow
if not st.session_state.authenticated:
    modern_login_system()
else:
    modern_dashboard()