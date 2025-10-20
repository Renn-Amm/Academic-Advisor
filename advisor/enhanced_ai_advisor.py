"""
Enhanced AI Academic Advisor with Lecturer Integration and Intelligent Recommendations
Now with LLM-powered dynamic response generation and timetable conflict detection
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from difflib import SequenceMatcher
import os

# Import LLM Advisor
try:
    from advisor.llm_advisor import LLMAdvisor
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    # Silently fail - LLM is optional

# Class time slots
CLASS_TIMES = [
    {"slot": 1, "time": "9:00 AM - 12:20 PM", "start_hour": 9},
    {"slot": 2, "time": "1:00 PM - 4:20 PM", "start_hour": 13},
    {"slot": 3, "time": "5:00 PM - 8:20 PM", "start_hour": 17}
]


class EnhancedAIAdvisor:
    """Enhanced AI advisor with comprehensive course intelligence and LLM-powered responses"""
    
    def __init__(self, use_llm=True, openai_api_key=None, model="gpt-3.5-turbo",
                 enable_caching=True, enable_rate_limiting=True):
        """
        Initialize Enhanced AI Advisor
        
        Args:
            use_llm: Whether to use LLM for generating responses (default: True)
            openai_api_key: OpenAI API key (optional, defaults to OPENAI_API_KEY env variable)
            model: LLM model to use (gpt-3.5-turbo or gpt-4)
            enable_caching: Enable response caching
            enable_rate_limiting: Enable rate limiting
        """
        self.courses_df = None
        self.lecturers_df = None
        self.programs_df = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.course_lecturer_map = {}
        
        # Initialize LLM Advisor if available and requested
        self.llm_advisor = None
        self.use_llm = use_llm and LLM_AVAILABLE
        
        if self.use_llm:
            try:
                self.llm_advisor = LLMAdvisor(
                    api_key=openai_api_key,
                    model=model,
                    enable_caching=enable_caching,
                    enable_rate_limiting=enable_rate_limiting
                )
                if self.llm_advisor.client:
                    print(f"LLM-powered AI responses enabled (Model: {model})")
                else:
                    print("LLM running in fallback mode (OpenAI API key not configured)")
            except Exception as e:
                print(f"LLM Advisor in fallback mode: {e}")
                self.use_llm = False
        
    def load_data(self, courses_df, lecturers_df, programs_df=None):
        """Load and prepare all data"""
        self.courses_df = courses_df
        self.lecturers_df = lecturers_df
        self.programs_df = programs_df
        
        # Map courses to lecturers intelligently
        self._map_lecturers_to_courses()
        
        # Prepare features for recommendations
        self._prepare_course_features()
        
        # Load data into LLM advisor if available
        if self.llm_advisor:
            self.llm_advisor.load_data(courses_df, lecturers_df, programs_df)
        
    def _map_lecturers_to_courses(self):
        """Intelligently map lecturers to courses based on expertise"""
        if self.lecturers_df is None or self.courses_df is None:
            return
            
        for idx, course in self.courses_df.iterrows():
            # Find best matching lecturer based on expertise
            course_skills = str(course.get('skills_covered_str', '')).lower()
            course_category = str(course.get('category', '')).lower()
            course_name = str(course.get('course_name', '')).lower()
            
            best_match = None
            best_score = 0
            
            for _, lecturer in self.lecturers_df.iterrows():
                expertise = str(lecturer.get('expertise_areas', '')).lower()
                job_title = str(lecturer.get('job_title', '')).lower()
                
                score = 0
                
                # Match based on expertise areas
                for skill in course_skills.split(','):
                    if skill.strip() and skill.strip() in expertise:
                        score += 3
                        
                # Match based on job title
                if any(word in job_title for word in course_name.split()):
                    score += 2
                    
                # Category matching
                if course_category in expertise or course_category in job_title:
                    score += 2
                    
                if score > best_score:
                    best_score = score
                    best_match = lecturer
                    
            if best_match is not None:
                self.course_lecturer_map[course['course_id']] = {
                    'lecturer_id': best_match['lecturer_id'],
                    'name': best_match['name'],
                    'job_title': best_match['job_title'],
                    'company': best_match.get('company', 'Independent'),
                    'background': best_match.get('background', ''),
                    'expertise_areas': best_match.get('expertise_areas', ''),
                    'email': best_match.get('email', '')
                }
                
    def _prepare_course_features(self):
        """Prepare TF-IDF features for course similarity"""
        if self.courses_df is None or self.courses_df.empty:
            return
            
        course_texts = []
        for _, course in self.courses_df.iterrows():
            text = f"{course['course_name']} {course['course_description']} {course['skills_covered_str']} {course['category']}"
            course_texts.append(text)
            
        self.course_features = self.tfidf_vectorizer.fit_transform(course_texts)
        
    def get_intelligent_recommendations(self, student_profile, query=None, limit=10, enrolled_courses=None):
        """
        Get intelligent course recommendations with detailed explanations
        Uses LLM for dynamic responses when available
        
        Args:
            student_profile: Dict with student info (major, career_goal, etc.)
            query: Student's question
            limit: Maximum number of courses to return
            enrolled_courses: List of currently enrolled courses (for conflict detection)
        
        Returns: (courses_list, explanations_dict, ai_response_text)
        """
        # Try LLM-powered response first if available
        if self.use_llm and self.llm_advisor and query:
            try:
                ai_response, relevant_courses = self.llm_advisor.generate_response(
                    query, student_profile, enrolled_courses
                )
                
                # Generate explanations for courses
                explanations = {}
                for _, course in relevant_courses.iterrows():
                    course_id = course['course_id']
                    explanations[course_id] = [
                        f"Relevant to your query",
                        f"Matches your {student_profile.get('major', 'program')} track"
                    ]
                
                return relevant_courses, explanations, ai_response
            except Exception as e:
                print(f"LLM generation failed: {e}, falling back to rule-based system")
        
        # Fallback to rule-based system
        major = student_profile.get('major', 'Computer Science')
        career_goal = student_profile.get('career_goal', '')
        experience_level = student_profile.get('experience_level', 'Beginner')
        program = student_profile.get('program', 'Bachelor')
        
        # Expand abbreviations in query first
        expanded_query = self._expand_query(query) if query else query
        
        # Analyze query intent (uses expanded query internally)
        query_intent = self._analyze_query_intent(query)
        
        # Handle different query types - use expanded_query for better matching
        if query_intent == 'preparation_advice':
            # For queries about preparing for class
            return self._handle_preparation_advice(expanded_query, major, career_goal, experience_level)
        elif query_intent == 'course_type_explanation':
            # For queries about course types, mandatory, audit, etc.
            return self._handle_course_type_explanation(expanded_query, major)
        elif query_intent == 'program_duration':
            # For queries about program length/duration
            return self._handle_program_duration_query(expanded_query, major, program)
        elif query_intent == 'general_info':
            # For queries like "data science", "machine learning" - provide overview
            return self._handle_general_info_query(expanded_query, major, career_goal, experience_level, program)
        elif query_intent == 'greeting':
            # For greetings
            return self._handle_greeting(major, career_goal)
        elif query_intent == 'lecturer_info':
            # For queries about lecturers
            return self._handle_lecturer_query(expanded_query, major)
        elif query_intent == 'schedule_info':
            # For queries about timings
            return self._handle_schedule_query(expanded_query, major)
        elif query_intent == 'career_guidance':
            # For career-related queries
            return self._handle_career_query(expanded_query, major, career_goal, experience_level)
        elif query_intent == 'module_planning':
            # For module planning queries
            return self._handle_module_planning_query(expanded_query, major, career_goal, experience_level, program)
        elif query_intent == 'attendance_consequences':
            # For queries about what happens if skip/miss classes
            return self._handle_attendance_consequences(expanded_query, major)
        elif query_intent == 'student_issues':
            # For queries about having problems/issues
            return self._handle_student_issues(expanded_query, major)
        elif query_intent == 'specific_class_preparation':
            # For queries about preparing for a specific class
            return self._handle_specific_class_preparation(expanded_query, major)
        elif query_intent == 'program_info':
            # For queries about what's in a specific major/program
            return self._handle_program_info_query(expanded_query, major, career_goal, experience_level, program)
        else:
            # Default: course recommendations
            return self._handle_course_recommendation(expanded_query, major, career_goal, experience_level, program, limit)
        
    def _score_courses(self, courses, major, career_goal, experience_level, program, query=None):
        """Score courses based on multiple factors"""
        scores = []
        
        for _, course in courses.iterrows():
            score = 0
            
            # 1. Major relevance (high priority)
            if major.lower() in str(course['category']).lower():
                score += 10
                
            # 2. Program alignment
            if program.lower() in str(course.get('program_name', '')).lower():
                score += 5
                
            # 3. Career goal alignment
            if career_goal:
                career_keywords = self._get_career_keywords(career_goal)
                skills = str(course.get('skills_covered_str', '')).lower()
                desc = str(course.get('course_description', '')).lower()
                for keyword in career_keywords:
                    if keyword in skills or keyword in desc:
                        score += 3
                        
            # 4. Experience level matching
            difficulty = str(course.get('estimated_difficulty', 'Intermediate'))
            if experience_level == 'Beginner' and difficulty == 'Beginner':
                score += 4
            elif experience_level == 'Intermediate' and difficulty in ['Beginner', 'Intermediate']:
                score += 4
            elif experience_level == 'Advanced':
                score += 2  # Advanced students can take any level
                
            # 5. Query matching (if provided)
            if query:
                query_lower = query.lower()
                course_text = f"{course['course_name']} {course['course_description']} {course.get('skills_covered_str', '')}".lower()
                if query_lower in course_text:
                    score += 8
                # Partial matches
                query_words = query_lower.split()
                for word in query_words:
                    if len(word) > 3 and word in course_text:
                        score += 2
                        
            # 6. Course type priority
            course_type = course.get('course_type', 'secondary')
            if course_type == 'mandatory':
                score += 7
            elif course_type == 'secondary':
                score += 4
            else:  # audit
                score += 2
                
            scores.append(score)
            
        courses = courses.copy()
        courses['relevance_score'] = scores
        return courses.sort_values('relevance_score', ascending=False)
        
    def _get_career_keywords(self, career_goal):
        """Get relevant keywords for career goals"""
        career_map = {
            'software engineer': ['programming', 'software', 'development', 'code', 'algorithms', 'web', 'api', 'backend', 'frontend'],
            'data scientist': ['data', 'analytics', 'machine learning', 'statistics', 'python', 'ai', 'deep learning', 'visualization'],
            'cybersecurity analyst': ['security', 'network', 'encryption', 'hacking', 'cyber', 'forensics', 'threat'],
            'product manager': ['product', 'management', 'strategy', 'business', 'agile', 'leadership'],
            'ux designer': ['design', 'user', 'interface', 'experience', 'visual', 'ui', 'prototyping', 'research'],
            'data engineer': ['data', 'pipeline', 'etl', 'database', 'big data', 'spark', 'hadoop'],
            'web developer': ['web', 'html', 'css', 'javascript', 'react', 'node', 'frontend'],
            'business analyst': ['business', 'analytics', 'strategy', 'analysis', 'intelligence']
        }
        
        for key, keywords in career_map.items():
            if key in career_goal.lower():
                return keywords
        return ['technology', 'programming', 'development']
    
    def _expand_query(self, query):
        """Expand abbreviations and fix typos in query"""
        if not query:
            return query
            
        query_lower = query.lower().strip()
        
        expansions = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ds': 'data science',
            'cs': 'computer science',
            'cyber': 'cybersecurity',
            'webdev': 'web development',
            'db': 'database',
            'dl': 'deep learning',
            'nn': 'neural network',
            # Common typos
            'machne': 'machine',
            'learing': 'learning',
            'lecurer': 'lecturer',
            'instuctor': 'instructor',
            'proffesor': 'professor',
            'scince': 'science',
            'engeneer': 'engineer',
            'devloper': 'developer'
        }
        
        # Apply all expansions
        for abbr, full in expansions.items():
            if abbr in query_lower:
                query_lower = query_lower.replace(abbr, full)
        
        return query_lower
    
    def _fuzzy_match(self, word, keyword_list, threshold=0.75):
        """Check if word matches any keyword with fuzzy matching for typos"""
        word_lower = word.lower()
        for keyword in keyword_list:
            # Direct match
            if keyword in word_lower or word_lower in keyword:
                return True
            # Fuzzy match for typos
            similarity = SequenceMatcher(None, word_lower, keyword).ratio()
            if similarity >= threshold:
                return True
        return False
    
    def _analyze_query_intent(self, query):
        """Analyze what the user is really asking for with typo tolerance"""
        if not query:
            return 'course_recommendation'
            
        query_lower = query.lower().strip()
        
        # Check for greetings FIRST (exact match or starts with)
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'howdy']
        if any(kw == query_lower or query_lower.startswith(kw + ' ') or query_lower.startswith(kw + ',') for kw in greeting_keywords):
            return 'greeting'
        
        # Check for "how are you" type greetings
        how_are_you_keywords = ['how are you', 'how r u', 'how are u', 'hows it going', 'how is it going', 'whats up', "what's up", 'sup']
        if any(kw in query_lower for kw in how_are_you_keywords):
            return 'greeting'
        
        # FIRST: Expand abbreviations and fix typos
        expansions = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ds': 'data science',
            'cs': 'computer science',
            'cyber': 'cybersecurity',
            'webdev': 'web development',
            'db': 'database',
            'dl': 'deep learning',
            'nn': 'neural network',
            # Common typos
            'machne': 'machine',
            'learing': 'learning',
            'lecurer': 'lecturer',
            'instuctor': 'instructor',
            'proffesor': 'professor',
            'scince': 'science',
            'engeneer': 'engineer',
            'devloper': 'developer'
        }
        
        # Apply all expansions
        for abbr, full in expansions.items():
            if abbr in query_lower:
                query_lower = query_lower.replace(abbr, full)
        
        query_words = query_lower.split()
        
        # Check for specific class preparation FIRST (highest priority - before lecturer!)
        specific_prep_keywords = ['what to prepare for', 'what should i prepare for', 'how to prepare for', 'prepare for', 
                                 'get ready for', 'before taking', 'what do i need for', 'prerequisites for', 'ready for']
        if any(kw in query_lower for kw in specific_prep_keywords):
            # This is about preparing for a specific course/topic
            return 'specific_class_preparation'
        
        # Check for program duration queries
        duration_keywords = ['how long', 'duration', 'how many years', 'length', 'year', 'years', 'program duration', 
                           'bachelor duration', 'master duration', 'how much time', 'time to complete', 
                           'how many', 'long is', 'take to complete', 'time required']
        if any(kw in query_lower for kw in duration_keywords):
            return 'program_duration'
        
        # Check for attendance/absence consequences
        attendance_consequence_keywords = ['what if', 'what happen', 'skip class', 'miss class', 'dont attend', 
                                          "don't attend", 'absent', 'too many absence', 'skip mandatory', 
                                          'miss mandatory', 'late to class', 'miss too many', 'fail because']
        if any(kw in query_lower for kw in attendance_consequence_keywords):
            if any(word in query_lower for word in ['class', 'mandatory', 'attendance', 'absent', 'skip', 'miss', 'late']):
                return 'attendance_consequences'
        
        # Check for issues/problems/help
        issues_keywords = ['have issue', 'have problem', 'need help', 'having trouble', 'struggling', 
                          'cant attend', "can't attend", 'emergency', 'conflict', 'sick', 'medical']
        if any(kw in query_lower for kw in issues_keywords):
            return 'student_issues'
        
        # Check for lecturer-related queries (AFTER preparation queries)
        lecturer_keywords = ['lecturer', 'lecturers', 'professor', 'instructor', 'instructors', 'teacher', 'teachers', 'prof', 'faculty', 'tutor', 'who teaches', 'who teach']
        
        # Direct check first
        if any(kw in query_lower for kw in lecturer_keywords):
            return 'lecturer_info'
        
        # Fuzzy match check
        if any(self._fuzzy_match(word, lecturer_keywords) for word in query_words):
            return 'lecturer_info'
        
        # Check for course type explanations
        explanation_keywords = ['mandatory', 'audit', 'secondary', 'course type', 'what is mandatory', 'what is audit', 'explain']
        if any(kw in query_lower for kw in explanation_keywords):
            if not any(word in query_lower for word in ['skip', 'miss', 'dont', "don't", 'happen', 'what if']):
                return 'course_type_explanation'
        
        # Check for general preparation/before class queries (more general, after specific)
        prep_keywords = ['before class', 'preparation', 'study tips', 'prepare well', 'how to study']
        if any(kw in query_lower for kw in prep_keywords):
            # Only general preparation advice, not specific to a course
            return 'preparation_advice'
        
        # Check for course queries ("course for X", "X course", "learn X", etc.)
        course_indicators = ['course', 'class', 'learn', 'study', 'teach', 'training', 'program']
        has_course_indicator = any(ind in query_lower for ind in course_indicators)
        
        # Check for general topic queries (short, 1-3 words about a topic OR contains key topics)
        topic_keywords = ['machine learning', 'ml', 'artificial intelligence', 'ai', 'data science', 'computer science', 
                         'cybersecurity', 'cyber', 'security', 'web development', 'web', 'database', 'db', 'deep learning', 'neural network',
                         'programming', 'software', 'data', 'python', 'java', 'javascript', 'software development',
                         'web dev', 'mobile', 'app development', 'frontend', 'backend', 'fullstack', 'business',
                         'design', 'ux', 'ui', 'marketing', 'entrepreneurship', 'analytics']
        
        # Single word AND two-word major/topic searches - ALWAYS return courses
        single_word_topics = ['ml', 'ai', 'software', 'business', 'design', 'marketing', 'data', 'web', 'mobile', 
                             'python', 'java', 'javascript', 'security', 'cyber', 'database', 'programming']
        
        two_word_topics = ['computer science', 'data science', 'machine learning', 'web development', 
                          'software development', 'deep learning', 'artificial intelligence',
                          'cyber security', 'app development', 'digital marketing']
        
        # If it's a short query (1-3 words) and matches a topic, it's a course search
        word_count = len(query_lower.split())
        if word_count <= 3:
            # Check single word topics
            if any(topic in query_lower for topic in single_word_topics):
                return 'general_info'
            # Check two word topics (exact match or contains)
            if any(topic in query_lower for topic in two_word_topics):
                return 'general_info'
        
        # If asking about courses with these topics, search courses
        if has_course_indicator or any(topic in query_lower for topic in topic_keywords):
            if not any(kw in query_lower for kw in ['schedule', 'career', 'module', 'time', 'timing', 'morning', 'afternoon', 'evening']):
                return 'general_info'
            
        # Check for schedule-related queries
        schedule_keywords = ['time', 'timing', 'schedule', 'when', 'morning', 'afternoon', 'evening']
        if any(kw in query_lower for kw in schedule_keywords):
            return 'schedule_info'
            
        # Check for career guidance
        career_keywords = ['career', 'job', 'future', 'work', 'industry', 'professional']
        if any(kw in query_lower for kw in career_keywords):
            return 'career_guidance'
        
        # Check for module planning
        module_keywords = ['module', 'semester', 'this module', 'next module', 'planning']
        if any(kw in query_lower for kw in module_keywords):
            return 'module_planning'
        
        # Check for major/program information queries
        program_query_patterns = [
            'what is in', 'whats in', 'courses in', 'what courses', 'show me',
            'tell me about', 'information about', 'about the', 'in the',
            'major', 'program', 'degree', 'what can i study', 'what will i learn'
        ]
        
        # List of all programs/majors
        program_names = [
            'computer science', 'data science', 'cyber security', 'cybersecurity',
            'front-end development', 'frontend', 'interaction design', 'design',
            'digital marketing', 'marketing', 'high-tech entrepreneurship', 'entrepreneurship',
            'business', 'digital transformation', 'product management', 'fintech',
            'applied data and computer science'
        ]
        
        # If query mentions a program name AND a program query pattern, it's asking about that program
        has_program_name = any(prog in query_lower for prog in program_names)
        has_program_pattern = any(pattern in query_lower for pattern in program_query_patterns)
        
        if has_program_name and has_program_pattern:
            return 'program_info'
            
        return 'course_recommendation'
    
    def _handle_course_type_explanation(self, query, major):
        """Explain course types, mandatory, audit, secondary, and attendance policies"""
        response = "Let me explain the different course types and requirements:\n\n"
        
        response += "COURSE TYPES:\n\n"
        
        response += "1. Mandatory Courses\n"
        response += "   - Required courses you MUST take for your degree\n"
        response += "   - Count towards your graduation requirements\n"
        response += "   - Graded and recorded on your transcript\n"
        response += "   - Attendance is mandatory (3 or more absences = FAIL)\n\n"
        
        response += "2. Secondary Courses\n"
        response += "   - Recommended elective courses for your major\n"
        response += "   - Count towards your credits\n"
        response += "   - Graded and recorded on transcript\n"
        response += "   - Attendance is mandatory (3 or more absences = FAIL)\n"
        response += "   - You can choose which secondary courses to take\n\n"
        
        response += "3. Audit Courses\n"
        response += "   - Optional courses you can take for learning only\n"
        response += "   - NOT graded, marked as 'Audit' on transcript\n"
        response += "   - Do NOT count towards your degree credits\n"
        response += "   - Attendance is recommended but flexible\n"
        response += "   - Great for exploring interests without GPA impact\n"
        response += "   - You can still access all course materials and lectures\n\n"
        
        response += "ATTENDANCE POLICY:\n"
        response += "- **3 or more absences = AUTOMATIC FAIL** (no exceptions)\n"
        response += "- **Being 10 minutes late = 1 absence** (punctuality is critical)\n"
        response += "- Missing 3+ consecutive classes without notice: Warning issued\n"
        response += "- Audit courses: Flexible attendance (no strict requirements)\n\n"
        
        response += "WARNINGS:\n"
        response += "- 1st Warning: Email notification about low attendance\n"
        response += "- 2nd Warning: Meeting with academic advisor required\n"
        response += "- **3rd Absence: Automatic course failure** (no exceptions)\n"
        response += "- Academic probation may apply for repeated failures\n\n"
        
        # Show example courses for the major
        major_courses = self.courses_df[
            self.courses_df['category'].str.contains(major, case=False, na=False)
        ].head(3)
        
        if not major_courses.empty:
            response += f"\nEXAMPLE from {major}:\n"
            for _, course in major_courses.iterrows():
                course_type = course.get('course_type', 'mandatory')
                response += f"- {course['course_name']} ({course['course_id']}): {course_type.upper()}\n"
        
        response += "\nWould you like to see all mandatory courses for your major, or help planning your semester?"
        
        explanations = {}
        return major_courses if not major_courses.empty else pd.DataFrame(), explanations, response
    
    def _handle_program_duration_query(self, query, major, program):
        """Answer questions about program duration/length"""
        query_lower = query.lower()
        
        # Program duration mapping based on Harbour Space structure
        program_durations = {
            # Bachelor Programs - typically 3 years
            'Computer Science': {'bachelor': 3, 'master': 1},
            'Data Science': {'bachelor': 3, 'master': 1},
            'Cyber Security': {'bachelor': 3, 'master': 1},
            'Front-End Development': {'bachelor': 3, 'master': 1},
            'Front-end Development': {'bachelor': 3, 'master': 1},
            'Interaction Design': {'bachelor': 3, 'master': 1},
            'Digital Marketing': {'bachelor': 3, 'master': 1},
            'High-Tech Entrepreneurship': {'bachelor': 3, 'master': 1},
            
            # Master Programs - typically 1 year
            'Digital Transformation': {'bachelor': 3, 'master': 1},
            'Product Management': {'bachelor': 3, 'master': 1},
            'Fintech': {'bachelor': 3, 'master': 1},
            'Applied Data and Computer Science': {'bachelor': 3, 'master': 1},
            'Computer Science Masters': {'bachelor': 3, 'master': 1}
        }
        
        # Detect if asking about bachelor or master
        level = 'bachelor'
        if any(word in query_lower for word in ['master', 'masters', 'msc', 'graduate']):
            level = 'master'
        elif any(word in query_lower for word in ['bachelor', 'bachelors', 'bsc', 'undergraduate']):
            level = 'bachelor'
        elif program:
            # Use current program level
            if 'master' in program.lower():
                level = 'master'
        
        response = "**Program Duration at Harbour.Space:**\n\n"
        
        # If asking about specific major
        if major and major in program_durations:
            duration = program_durations[major].get(level, 3 if level == 'bachelor' else 1)
            response += f"**{major} ({level.title()}):** {duration} year{'s' if duration > 1 else ''}\n\n"
            
            # Get actual courses from this program to show evidence
            program_courses = self.courses_df[
                (self.courses_df['category'] == major) & 
                (self.courses_df['Level'].str.lower() == level)
            ]
            
            if not program_courses.empty:
                # Analyze year distribution
                years = program_courses['Year'].unique() if 'Year' in program_courses.columns else []
                if len(years) > 0:
                    response += f"**Structure:** This program has courses in {len(years)} years:\n"
                    for year in sorted(years):
                        year_courses = program_courses[program_courses['Year'] == year]
                        response += f"- {year}: {len(year_courses)} courses\n"
                    response += "\n"
        
        # General overview
        response += "**General Program Lengths:**\n\n"
        response += "**Bachelor's Degree:** 3 years (full-time)\n"
        response += "- Year 1: Foundation courses and core fundamentals\n"
        response += "- Year 2: Intermediate courses and specialization begins\n"
        response += "- Year 3: Advanced courses, electives, and capstone project\n\n"
        
        response += "**Master's Degree:** 1 year (intensive)\n"
        response += "- Full-time intensive program\n"
        response += "- Focus on advanced topics and industry applications\n"
        response += "- Includes capstone project or thesis\n\n"
        
        response += "**Note:** All programs follow Harbour.Space's unique module system:\n"
        response += "- Each module = 3 weeks\n"
        response += "- ~12 modules per year\n"
        response += "- Intensive, focused learning\n\n"
        
        # Show programs with different durations if any
        if 'duration' in query_lower or 'all' in query_lower:
            response += "**Available Programs:**\n\n"
            response += "**Bachelor Programs (3 years):**\n"
            bachelor_programs = ['Computer Science', 'Data Science', 'Cyber Security', 'Front-End Development', 
                                'Interaction Design', 'Digital Marketing', 'High-Tech Entrepreneurship']
            for prog in bachelor_programs:
                response += f"• {prog}\n"
            
            response += "\n**Master Programs (1 year):**\n"
            master_programs = ['Digital Transformation', 'Product Management', 'Fintech', 
                              'Applied Data and Computer Science', 'Interaction Design']
            for prog in master_programs:
                response += f"• {prog}\n"
        
        response += "\n**Want to know more?** Ask about:\n"
        response += "• Specific program structure\n"
        response += "• Module breakdown\n"
        response += "• Career outcomes after graduation"
        
        explanations = {}
        return pd.DataFrame(), explanations, response
    
    def _handle_preparation_advice(self, query, major, career_goal, experience_level):
        """Provide preparation advice for classes"""
        # Get varied courses from different categories
        all_courses = self.courses_df.head(20)
        
        response = "Great question! Let me help you prepare for your classes. Here's what you should do:\n\n"
        
        response += "BEFORE YOUR FIRST CLASS:\n"
        response += "1. Review course materials and syllabus\n"
        response += "2. Set up your development environment (IDE, tools)\n"
        response += "3. Join the course communication channel\n"
        response += "4. Prepare questions about topics you're curious about\n\n"
        
        response += "GENERAL PREPARATION TIPS:\n"
        response += "- Read ahead: Review next class topics the night before\n"
        response += "- Practice coding: Try small exercises related to upcoming topics\n"
        response += "- Connect with classmates: Form study groups early\n"
        response += "- Ask questions: Don't hesitate to reach out to instructors\n\n"
        
        response += f"FOR {major.upper()} STUDENTS:\n"
        
        # Get subject-specific courses
        major_courses = self.courses_df[
            self.courses_df['category'].str.contains(major, case=False, na=False)
        ].head(5)
        
        if not major_courses.empty:
            response += "Recommended preparation for your major:\n\n"
            explanations = {}
            
            for idx, (_, course) in enumerate(major_courses.iterrows(), 1):
                course_id = course['course_id']
                response += f"{idx}. For {course['course_name']}:\n"
                prereq_skills = self._get_prerequisite_skills(course)
                if prereq_skills:
                    response += f"   - Brush up on: {', '.join(prereq_skills[:3])}\n"
                else:
                    response += f"   - No prerequisites, perfect for beginners\n"
                
                # Add lecturer tip
                if course_id in self.course_lecturer_map:
                    lecturer = self.course_lecturer_map[course_id]
                    response += f"   - Taught by {lecturer['name']} ({lecturer['company']})\n"
                
                response += "\n"
                
                explanations[course_id] = [
                    f"Preparation recommended",
                    f"Review prerequisite skills"
                ]
            
            response += "\nWould you like specific study resources or tips for any particular subject?"
            return major_courses, explanations, response
        
        return pd.DataFrame(), {}, response
    
    def _handle_general_info_query(self, query, major, career_goal, experience_level, program):
        """Handle general information queries about topics - supports ANY major"""
        query_lower = query.lower().strip()
        
        # Check if query looks like gibberish (no common words)
        common_words = ['course', 'class', 'learn', 'study', 'teach', 'help', 'show', 'find', 'about', 'what', 'how', 'when', 'where', 'who']
        known_topics = ['machine learning', 'data science', 'computer science', 'cybersecurity', 'cyber security', 
                       'programming', 'web', 'development', 'python', 'java', 'javascript', 'database', 'ai', 'artificial',
                       'software', 'business', 'design', 'marketing', 'frontend', 'backend', 'mobile']
        
        has_common_word = any(word in query_lower for word in common_words)
        has_known_topic = any(topic in query_lower for topic in known_topics)
        
        # If query is very short and doesn't match any known pattern, treat as unknown
        # BUT: known topics are OK even without common words!
        if len(query_lower) < 3:
            return self._handle_unknown_query(query, major, career_goal)
        
        # If it's a short query with no common word AND no known topic, treat as unknown
        if not has_common_word and not has_known_topic and len(query.split()) <= 3:
            return self._handle_unknown_query(query, major, career_goal)
        
        # Detect if user is asking about a DIFFERENT major
        major_keywords = {
            'business': ['business', 'entrepreneurship', 'management', 'mba'],
            'data science': ['data science', 'data analytics', 'analytics'],
            'computer science': ['computer science', 'cs', 'computing'],
            'cybersecurity': ['cybersecurity', 'cyber security', 'security', 'infosec'],
            'design': ['design', 'ux', 'ui', 'interaction design'],
            'marketing': ['marketing', 'digital marketing', 'social media'],
            'software development': ['software development', 'software engineering', 'programming'],
            'web development': ['web development', 'web dev', 'frontend', 'backend', 'fullstack'],
            'mobile': ['mobile', 'app development', 'android', 'ios'],
        }
        
        # Check if query mentions a specific major
        target_major = None
        for major_name, keywords in major_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                target_major = major_name
                break
        
        # If no specific major detected, use student's major
        search_query = query_lower
        
        # Find relevant courses - show more results (up to 8)
        try:
            # Search in course name, description, skills, AND category
            relevant_courses = self.courses_df[
                self.courses_df['course_name'].str.contains(search_query, case=False, na=False) |
                self.courses_df['course_description'].str.contains(search_query, case=False, na=False) |
                self.courses_df['skills_covered_str'].str.contains(search_query, case=False, na=False) |
                self.courses_df['category'].str.contains(search_query, case=False, na=False)
            ]
            
            # If target major is detected, prioritize courses from that major
            if target_major and not relevant_courses.empty:
                major_specific = relevant_courses[
                    relevant_courses['category'].str.contains(target_major, case=False, na=False)
                ]
                if not major_specific.empty:
                    relevant_courses = major_specific
            
            relevant_courses = relevant_courses.head(8)
        except:
            return self._handle_unknown_query(query, major, career_goal)
        
        if relevant_courses.empty:
            # Use the unknown query handler instead of generic response
            return self._handle_unknown_query(query, major, career_goal)
        
        # Generate conversational response
        if target_major:
            response = f"**{target_major.title()} Courses:**\n\n"
            response += f"Great choice! Here are the best courses for {target_major}:\n\n"
        else:
            response = f"**Courses for: {query}**\n\n"
        
        explanations = {}
        for idx, (_, course) in enumerate(relevant_courses.iterrows(), 1):
            course_id = course['course_id']
            response += f"{idx}. {course['course_name']}\n"
            
            # Lecturer info
            if course_id in self.course_lecturer_map:
                lecturer = self.course_lecturer_map[course_id]
                response += f"   Instructor: {lecturer['name']} ({lecturer['job_title']}) from {lecturer['company']}\n"
            
            # Key info
            response += f"   Level: {course.get('estimated_difficulty', 'Intermediate')} | Schedule: {course.get('class_time', 'TBD')}\n"
            response += f"   {course.get('course_description', '')[:120]}...\n\n"
            
            # Add to explanations
            explanations[course_id] = [
                f"Perfect for {major} students",
                f"Taught by industry expert",
                f"Practical, hands-on approach"
            ]
        
        response += f"\nFor a {experience_level} student, I'd recommend starting with {relevant_courses.iloc[0]['course_name']}. "
        response += f"It provides a solid foundation. Would you like to know about prerequisites or course combinations?"
        
        return relevant_courses, explanations, response
    
    def _handle_lecturer_query(self, query, major):
        """Handle lecturer-specific queries - field-based and conversational"""
        query_lower = query.lower()
        
        # Get unique lecturers grouped by program
        lecturers_by_program = {}
        all_lecturer_names = []
        
        if self.lecturers_df is not None and not self.lecturers_df.empty:
            for _, lecturer in self.lecturers_df.iterrows():
                program = lecturer.get('program', 'General')
                name = lecturer.get('name', 'Unknown')
                
                if program not in lecturers_by_program:
                    lecturers_by_program[program] = []
                lecturers_by_program[program].append(lecturer)
                all_lecturer_names.append(name.lower())
        
        # Check if asking about specific person
        specific_person = None
        for name in all_lecturer_names:
            if name in query_lower:
                specific_person = name
                break
        
        if specific_person:
            # Provide details about specific lecturer
            lecturer_info = self.lecturers_df[self.lecturers_df['name'].str.lower() == specific_person]
            if not lecturer_info.empty:
                lect = lecturer_info.iloc[0]
                response = f"**{lect['name']}**\n\n"
                response += f"**Position:** {lect['job_title']}\n"
                response += f"**Company:** {lect.get('company', 'Harbour.Space')}\n"
                response += f"**Program:** {lect.get('program', 'N/A')}\n"
                response += f"**Email:** {lect.get('email', 'N/A')}\n"
                response += f"**Profile:** {lect.get('profile_url', 'N/A')}\n\n"
                response += f"**Expertise:** {lect.get('expertise_areas', 'Technology Education')}\n\n"
                response += f"**Background:** {lect.get('background', 'Experienced educator and industry professional.')}"
                
                return pd.DataFrame(), {}, response
        
        # Check if asking about specific field/program
        field_match = None
        for program in lecturers_by_program.keys():
            if program.lower() in query_lower:
                field_match = program
                break
        
        if field_match:
            # Show lecturers from specific field
            lecturers = lecturers_by_program[field_match]
            response = f"**{field_match} Instructors:**\n\n"
            response += f"We have {len(lecturers)} instructors teaching {field_match}:\n\n"
            
            for idx, lect in enumerate(lecturers[:10], 1):
                response += f"{idx}. **{lect['name']}**\n"
                response += f"   {lect['job_title']}\n"
                if idx <= 5:
                    response += f"   Email: {lect.get('email', 'N/A')}\n"
                response += "\n"
            
            if len(lecturers) > 10:
                response += f"\n...and {len(lecturers)-10} more instructors.\n"
            
            response += f"\n**Tip: Ask about a specific instructor by name for more details!**"
            return pd.DataFrame(), {}, response
        
        # General query - ask which field
        response = "I can tell you about our instructors! **Which field are you interested in?**\n\n"
        response += "We have expert faculty in:\n\n"
        
        for idx, program in enumerate(sorted(lecturers_by_program.keys())[:10], 1):
            count = len(lecturers_by_program[program])
            response += f"• **{program}** ({count} instructors)\n"
        
        response += "\n**Examples:**\n"
        response += '• "Computer Science lecturers"\n'
        response += '• "Who teaches Data Science?"\n'
        response += '• "Tell me about [Instructor Name]"'
        
        all_courses = []
        explanations = {}
        
        return pd.DataFrame(all_courses) if all_courses else pd.DataFrame(), explanations, response
    
    def _handle_greeting(self, major, career_goal):
        """Handle greetings conversationally"""
        response = f"Hello! I'm your AI Academic Advisor for **{major}**.\n\n"
        response += "I'm here to help you navigate your academic journey! "
        
        if career_goal:
            response += f"I see you're aiming for **{career_goal}** - that's an exciting goal!\n\n"
        else:
            response += "Let's explore your academic options together.\n\n"
        
        response += "**I can help you with:**\n\n"
        response += "**Course Discovery** - \"Show me ML courses\", \"Software development courses\"\n"
        response += "**Faculty Info** - \"Lecturers for data science\", \"Who teaches Python?\"\n"
        response += "**Schedules** - \"Morning classes\", \"Evening courses\"\n"
        response += "**Planning** - \"Module planning\", \"What should I take?\"\n"
        response += "**Guidance** - \"Career advice\", \"Preparation tips\"\n\n"
        response += "**What would you like to know?** Feel free to ask me anything!"
        
        return pd.DataFrame(), {}, response
    
    def _handle_attendance_consequences(self, query, major):
        """Handle queries about what happens if skip/miss classes"""
        query_lower = query.lower()
        
        response = "I understand you're asking about attendance requirements. Let me explain what happens:\n\n"
        
        # Determine specific scenario
        if 'mandatory' in query_lower or 'required' in query_lower:
            response += "**For MANDATORY Courses:**\n\n"
            response += "Mandatory courses are essential for your degree, and attendance is strictly enforced:\n\n"
            response += "**Critical Rules:**\n"
            response += "- 3 or more absences = AUTOMATIC FAIL (no exceptions)\n"
            response += "- Being 10 minutes late = Counts as 1 absence\n"
            response += "- Failed mandatory course = Must retake it (delays graduation)\n\n"
            response += "**What This Means:**\n"
            response += "If your mandatory course has 15 sessions, you can miss maximum 2 classes. The 3rd absence automatically fails you.\n\n"
        else:
            response += "**General Attendance Policy:**\n\n"
            response += "**For ALL Course Types:**\n"
            response += "- 3 or more absences in any course = FAIL\n"
            response += "- 10 minutes late = 1 absence\n\n"
            response += "**Consequences of Failing:**\n"
            response += "- Mandatory course: Must retake (delays graduation, affects GPA)\n"
            response += "- Secondary course: May need to replace with another course\n"
            response += "- Audit course: Removed from transcript\n\n"
        
        response += "**What If You Have a Valid Reason?**\n\n"
        response += "If you anticipate attendance issues due to:\n"
        response += "- Medical emergencies\n"
        response += "- Family emergencies\n"
        response += "- Schedule conflicts\n"
        response += "- Other serious situations\n\n"
        response += "**You should:**\n"
        response += "1. Contact the academic team IMMEDIATELY\n"
        response += "2. Provide documentation (medical certificate, etc.)\n"
        response += "3. Submit a concern through the Feedback tab\n"
        response += "4. Discuss alternatives (postpone, switch to audit, etc.)\n\n"
        
        response += "**Bottom Line:** Attendance is serious. Missing 3 classes means automatic failure. Plan ahead and communicate early if you foresee issues!\n\n"
        response += "Need help with a specific situation? Ask me \"I have an issue\" and I'll guide you through the process."
        
        return pd.DataFrame(), {}, response
    
    def _handle_student_issues(self, query, major):
        """Handle queries about having problems or issues"""
        query_lower = query.lower()
        
        response = "I'm here to help you navigate any challenges you're facing. Let me guide you through the support process.\n\n"
        
        # Detect type of issue
        if any(word in query_lower for word in ['sick', 'medical', 'health', 'hospital']):
            response += "**Medical/Health Issue:**\n\n"
            response += "I understand health comes first. Here's what you should do:\n\n"
            response += "**Immediate Steps:**\n"
            response += "1. Get medical documentation (doctor's note, hospital certificate)\n"
            response += "2. Email your instructors ASAP about your situation\n"
            response += "3. Submit a concern through the Feedback tab (include 'Medical Issue')\n"
            response += "4. Contact the academic team: They can arrange:\n"
            response += "   - Excused absences (with documentation)\n"
            response += "   - Assignment extensions\n"
            response += "   - Module postponement if needed\n\n"
            
        elif any(word in query_lower for word in ['work', 'job', 'schedule', 'conflict']):
            response += "**Schedule Conflict (Work/Personal):**\n\n"
            response += "Balancing work and studies is challenging. Here are your options:\n\n"
            response += "**Solutions:**\n"
            response += "1. Check for alternative time slots (morning/afternoon/evening)\n"
            response += "2. Consider switching mandatory to audit (less attendance pressure)\n"
            response += "3. Postpone the course to next module\n"
            response += "4. Discuss hybrid/flexible arrangements with academic team\n\n"
            response += "**Try asking me:**\n"
            response += "- \"Evening classes\" to see later options\n"
            response += "- \"What is audit\" to learn about flexible options\n\n"
            
        else:
            response += "**General Support Process:**\n\n"
            response += "Whatever your situation, we're here to help. Here's how:\n\n"
            
        response += "**How to Get Help:**\n\n"
        response += "**1. Use the Feedback Tab (in the app)**\n"
        response += "   - Go to 'Feedback' tab\n"
        response += "   - Choose 'Feature Requests & Course Concerns'\n"
        response += "   - Select 'Mandatory Course Concerns'\n"
        response += "   - Explain your situation in detail\n"
        response += "   - Submit - Academic team reviews within 48 hours\n\n"
        
        response += "**2. Common Situations & Solutions:**\n\n"
        response += "**Issue: Can't attend mandatory class**\n"
        response += "→ Options: Postpone, switch to secondary/audit, find alternative\n\n"
        response += "**Issue: Course too difficult**\n"
        response += "→ Options: Get tutoring, switch to beginner level, extend timeline\n\n"
        response += "**Issue: Financial constraints**\n"
        response += "→ Options: Scholarship info, payment plans, reduced course load\n\n"
        response += "**Issue: Personal/family emergency**\n"
        response += "→ Options: Temporary leave, postpone modules, flexible arrangements\n\n"
        
        response += "**3. What Happens Next:**\n"
        response += "- Academic team reviews your case\n"
        response += "- They contact you within 48 hours\n"
        response += "- You discuss solutions together\n"
        response += "- They provide accommodations when possible\n\n"
        
        response += "**Remember:** The earlier you communicate, the more options we have to help you succeed!\n\n"
        response += "**Need specific help?** Ask me:\n"
        response += "- \"What if I skip mandatory class\" - Understand consequences\n"
        response += "- \"How to prepare for [course name]\" - Get ready for tough courses\n"
        response += "- \"Alternative schedules\" - Find different time options"
        
        return pd.DataFrame(), {}, response
    
    def _handle_specific_class_preparation(self, query, major):
        """Handle queries about preparing for specific classes"""
        query_lower = query.lower()
        
        # Check if asking about general field/topic vs specific course
        general_topics = {
            'data science': ['statistics', 'Python/R programming', 'data visualization', 'machine learning basics', 'SQL'],
            'software': ['programming fundamentals', 'data structures', 'algorithms', 'version control (Git)', 'problem-solving', 'debugging'],
            'software development': ['programming fundamentals', 'data structures', 'algorithms', 'version control (Git)', 'problem-solving', 'debugging'],
            'machine learning': ['Python programming', 'statistics & probability', 'linear algebra', 'calculus', 'data preprocessing'],
            'ml': ['Python programming', 'statistics & probability', 'linear algebra', 'mathematics', 'data handling'],
            'web development': ['HTML/CSS', 'JavaScript', 'responsive design', 'backend basics', 'databases'],
            'web': ['HTML/CSS', 'JavaScript', 'responsive design', 'browser tools', 'basic design'],
            'cybersecurity': ['networking fundamentals', 'operating systems', 'basic programming', 'security concepts', 'ethical mindset'],
            'cyber': ['networking basics', 'system administration', 'security principles', 'ethical hacking concepts'],
            'business': ['communication skills', 'basic accounting', 'market research', 'analytical thinking', 'presentation skills'],
            'design': ['design principles', 'color theory', 'typography', 'design tools (Figma/Adobe)', 'user empathy'],
            'marketing': ['communication', 'psychology basics', 'social media familiarity', 'analytics', 'creativity'],
            'computer science': ['programming fundamentals', 'mathematics', 'logic', 'algorithms', 'problem-solving'],
            'programming': ['logic', 'syntax fundamentals', 'problem decomposition', 'debugging skills', 'practice'],
        }
        
        # Specific preparation guide for each topic
        preparation_guides = {
            'data science': {
                'tools': ['Python (install Anaconda)', 'Jupyter Notebook', 'pandas library', 'NumPy library', 'Matplotlib'],
                'languages': ['Python (primary)', 'SQL for databases', 'R (optional)'],
                'practice': ['Kaggle datasets analysis', 'Clean and visualize CSV files', 'Build simple prediction models', 'Create data dashboards'],
                'research': ['Statistics fundamentals', 'Probability theory', 'Linear regression', 'Data cleaning techniques'],
                'resources': ['Kaggle.com for datasets', 'DataCamp Python courses', 'Coursera "Python for Data Science"', 'Book: "Python Data Science Handbook"']
            },
            'software': {
                'tools': ['VS Code or PyCharm', 'Git and GitHub', 'Terminal/Command Line', 'Docker (basics)'],
                'languages': ['Python', 'JavaScript', 'Java or C++'],
                'practice': ['Build a calculator app', 'Create a to-do list app', 'Contribute to open-source projects', 'Solve LeetCode Easy problems'],
                'research': ['Data structures (arrays, linked lists)', 'Algorithms (sorting, searching)', 'Object-oriented programming', 'Design patterns'],
                'resources': ['freeCodeCamp.org', 'LeetCode.com', 'GitHub for projects', 'Book: "Clean Code" by Robert Martin']
            },
            'software development': {
                'tools': ['VS Code or PyCharm', 'Git and GitHub', 'Terminal/Command Line', 'Docker (basics)'],
                'languages': ['Python', 'JavaScript', 'Java or C++'],
                'practice': ['Build a calculator app', 'Create a to-do list app', 'Contribute to open-source projects', 'Solve LeetCode Easy problems'],
                'research': ['Data structures (arrays, linked lists)', 'Algorithms (sorting, searching)', 'Object-oriented programming', 'Design patterns'],
                'resources': ['freeCodeCamp.org', 'LeetCode.com', 'GitHub for projects', 'Book: "Clean Code" by Robert Martin']
            },
            'machine learning': {
                'tools': ['Python', 'Jupyter Notebook', 'scikit-learn', 'TensorFlow or PyTorch', 'Google Colab'],
                'languages': ['Python (essential)', 'R (optional)'],
                'practice': ['Train a simple classification model', 'Implement linear regression from scratch', 'Build image classifier', 'Kaggle competitions'],
                'research': ['Supervised vs unsupervised learning', 'Neural networks basics', 'Gradient descent', 'Overfitting and regularization'],
                'resources': ['Andrew Ng\'s ML course on Coursera', 'Fast.ai courses', 'Kaggle Learn', 'Book: "Hands-On Machine Learning"']
            },
            'ml': {
                'tools': ['Python', 'Jupyter Notebook', 'scikit-learn', 'TensorFlow or PyTorch', 'Google Colab'],
                'languages': ['Python (essential)', 'R (optional)'],
                'practice': ['Train a simple classification model', 'Implement linear regression from scratch', 'Build image classifier', 'Kaggle competitions'],
                'research': ['Supervised vs unsupervised learning', 'Neural networks basics', 'Gradient descent', 'Overfitting and regularization'],
                'resources': ['Andrew Ng\'s ML course on Coursera', 'Fast.ai courses', 'Kaggle Learn', 'Book: "Hands-On Machine Learning"']
            },
            'web development': {
                'tools': ['VS Code', 'Chrome DevTools', 'Postman', 'npm/yarn', 'Git'],
                'languages': ['HTML', 'CSS', 'JavaScript', 'Node.js'],
                'practice': ['Build personal portfolio site', 'Create landing pages', 'Build REST API', 'Deploy to Netlify/Vercel'],
                'research': ['Responsive design', 'CSS Flexbox and Grid', 'DOM manipulation', 'HTTP methods and APIs'],
                'resources': ['MDN Web Docs', 'freeCodeCamp Web Dev', 'JavaScript30.com', 'Frontend Mentor challenges']
            },
            'web': {
                'tools': ['VS Code', 'Chrome DevTools', 'Postman', 'npm/yarn', 'Git'],
                'languages': ['HTML', 'CSS', 'JavaScript', 'Node.js'],
                'practice': ['Build personal portfolio site', 'Create landing pages', 'Build REST API', 'Deploy to Netlify/Vercel'],
                'research': ['Responsive design', 'CSS Flexbox and Grid', 'DOM manipulation', 'HTTP methods and APIs'],
                'resources': ['MDN Web Docs', 'freeCodeCamp Web Dev', 'JavaScript30.com', 'Frontend Mentor challenges']
            },
            'cybersecurity': {
                'tools': ['VirtualBox or VMware', 'Kali Linux', 'Wireshark', 'Metasploit', 'Burp Suite'],
                'languages': ['Python (for scripts)', 'Bash scripting', 'PowerShell'],
                'practice': ['Set up virtual lab', 'Practice on HackTheBox', 'Complete TryHackMe rooms', 'Capture The Flag challenges'],
                'research': ['Network protocols', 'Common vulnerabilities (OWASP Top 10)', 'Encryption basics', 'Penetration testing methodology'],
                'resources': ['TryHackMe.com', 'HackTheBox.eu', 'OWASP resources', 'Book: "The Web Application Hacker\'s Handbook"']
            },
            'cyber': {
                'tools': ['VirtualBox or VMware', 'Kali Linux', 'Wireshark', 'Metasploit', 'Burp Suite'],
                'languages': ['Python (for scripts)', 'Bash scripting', 'PowerShell'],
                'practice': ['Set up virtual lab', 'Practice on HackTheBox', 'Complete TryHackMe rooms', 'Capture The Flag challenges'],
                'research': ['Network protocols', 'Common vulnerabilities (OWASP Top 10)', 'Encryption basics', 'Penetration testing methodology'],
                'resources': ['TryHackMe.com', 'HackTheBox.eu', 'OWASP resources', 'Book: "The Web Application Hacker\'s Handbook"']
            },
            'business': {
                'tools': ['Excel/Google Sheets', 'PowerPoint/Google Slides', 'Notion or Trello', 'Canva for presentations'],
                'languages': ['None required'],
                'practice': ['Analyze business case studies', 'Create business plan template', 'Build financial model in Excel', 'Present mock pitches'],
                'research': ['Business model canvas', 'SWOT analysis', 'Market research methods', 'Financial statements basics'],
                'resources': ['Harvard Business Review', 'Coursera Business courses', 'Case studies from your field', 'Book: "The Lean Startup"']
            },
            'design': {
                'tools': ['Figma (free)', 'Adobe XD', 'Canva', 'Pen and paper for sketching'],
                'languages': ['None required'],
                'practice': ['Redesign existing apps', 'Create 30-day UI challenge', 'Build design system', 'Copy popular designs'],
                'research': ['Design principles (CRAP)', 'Color theory', 'Typography rules', 'User psychology', 'Accessibility standards'],
                'resources': ['Dribbble for inspiration', 'Behance portfolios', 'Refactoring UI book', 'Daily UI challenges']
            },
            'marketing': {
                'tools': ['Google Analytics', 'Google Ads', 'Mailchimp', 'Canva', 'Hootsuite'],
                'languages': ['None required'],
                'practice': ['Run mock ad campaigns', 'Analyze competitor websites', 'Create content calendar', 'Write marketing copy'],
                'research': ['SEO basics', 'Content marketing', 'Social media algorithms', 'Email marketing best practices', 'Conversion optimization'],
                'resources': ['Google Digital Garage', 'HubSpot Academy', 'Neil Patel blog', 'Book: "Contagious" by Jonah Berger']
            },
            'computer science': {
                'tools': ['VS Code or IntelliJ', 'Git', 'Terminal', 'Python or Java IDE'],
                'languages': ['Python', 'Java', 'C++ (one of these)'],
                'practice': ['Solve algorithmic problems', 'Build data structures from scratch', 'Contribute to open-source', 'Complete coding challenges'],
                'research': ['Algorithms complexity', 'Data structures', 'Computer architecture', 'Operating systems basics'],
                'resources': ['LeetCode', 'HackerRank', 'CS50 by Harvard', 'Book: "Introduction to Algorithms" (CLRS)']
            },
            'programming': {
                'tools': ['VS Code', 'Git and GitHub', 'Terminal/Command Line', 'Python or JavaScript'],
                'languages': ['Python (beginner-friendly)', 'JavaScript (for web)'],
                'practice': ['100 Days of Code challenge', 'Build 10 small projects', 'Solve Codewars katas', 'Read other people\'s code'],
                'research': ['Variables and data types', 'Control flow (if/else, loops)', 'Functions', 'Debugging techniques'],
                'resources': ['Codecademy', 'Python.org tutorial', 'Automate the Boring Stuff book', 'freeCodeCamp']
            }
        }
        
        # Check if asking about general topic
        for topic, skills in general_topics.items():
            if topic in query_lower:
                guide = preparation_guides.get(topic, None)
                
                if guide:
                    # Specific actionable preparation guide
                    response = f"**Preparing for {topic.title()}**\n\n"
                    response += f"Here's your actionable preparation plan:\n\n"
                    
                    response += "**1. Tools to Install & Practice:**\n"
                    for tool in guide['tools']:
                        response += f"- {tool}\n"
                    response += "\n"
                    
                    response += "**2. Programming Languages to Learn:**\n"
                    for lang in guide['languages']:
                        response += f"- {lang}\n"
                    response += "\n"
                    
                    response += "**3. Hands-On Practice Projects:**\n"
                    for project in guide['practice']:
                        response += f"- {project}\n"
                    response += "\n"
                    
                    response += "**4. Topics to Research:**\n"
                    for research_topic in guide['research']:
                        response += f"- {research_topic}\n"
                    response += "\n"
                    
                    response += "**5. Recommended Resources:**\n"
                    for resource in guide['resources']:
                        response += f"- {resource}\n"
                    response += "\n"
                    
                    response += f"**Action Plan:**\n"
                    response += "Week 1-2: Install tools, complete basic tutorials\n"
                    response += "Week 3-4: Start first practice project\n"
                    response += "Week 5-6: Research advanced topics, build portfolio\n"
                    response += "Week 7-8: Apply to our courses, continue practicing\n\n"
                    
                    response += f"**Ready to Enroll:**\n"
                    response += f"Once comfortable with basics, check our {topic.title()} courses in the Smart Path Planner!"
                    
                    return pd.DataFrame(), {}, response
                else:
                    # Fallback for topics without specific guide
                    response = f"**Preparing for {topic.title()}**\n\n"
                    response += f"Essential skills: {', '.join(skills)}\n\n"
                    response += "Practice consistently, build projects, and join relevant communities.\n"
                    response += f"Check our {topic.title()} courses when ready!"
                    return pd.DataFrame(), {}, response
        
        # Try to extract specific course name from query
        course_found = None
        for _, course in self.courses_df.iterrows():
            course_name_lower = course['course_name'].lower()
            # More precise matching - course name should be significantly present in query
            if course_name_lower in query_lower:
                course_found = course
                break
        
        if course_found is not None:
            response = f"**Preparing for {course_found['course_name']}**\n\n"
            response += f"Great question! Here's how to get ready for this course:\n\n"
            
            # Prerequisites
            response += "**Skills You Should Have:**\n"
            skills = course_found.get('skills_covered_str', '')
            if skills and str(skills) != 'nan':
                skills_list = [s.strip() for s in str(skills).split(',')]
                response += "Make sure you're comfortable with:\n"
                for skill in skills_list[:5]:
                    response += f"- {skill}\n"
                response += "\n"
            else:
                response += f"- Basic understanding of {major}\n"
                response += "- Strong problem-solving skills\n\n"
            
            # Difficulty level
            difficulty = course_found.get('estimated_difficulty', 'Intermediate')
            response += f"**Course Difficulty:** {difficulty}\n\n"
            
            if difficulty == 'Advanced':
                response += "**This is an advanced course.** Make sure you:\n"
                response += "- Have completed prerequisite courses\n"
                response += "- Are comfortable with foundational concepts\n"
                response += "- Are ready for challenging projects\n\n"
            elif difficulty == 'Beginner':
                response += "**This is a beginner-friendly course.** You should:\n"
                response += "- Come with an open mind\n"
                response += "- Be ready to learn from scratch\n"
                response += "- Practice consistently\n\n"
            
            # Lecturer info
            course_id = course_found['course_id']
            lecturer = self.get_lecturer_details(course_id)
            if lecturer:
                response += f"**Instructor:** {lecturer['name']}\n"
                response += f"Role: {lecturer['job_title']}\n"
                response += f"Expertise: {lecturer.get('expertise_areas', 'Industry professional')}\n\n"
            
            # General preparation tips
            response += "**Before First Class:**\n"
            response += "1. Review any prerequisites or recommended readings\n"
            response += "2. Set up your development environment (if technical course)\n"
            response += "3. Join the course communication channel\n"
            response += "4. Prepare questions you want answered\n\n"
            
            response += "**During the Course:**\n"
            response += "- Attend ALL classes (remember: 3 absences = fail!)\n"
            response += "- Take detailed notes\n"
            response += "- Ask questions when confused\n"
            response += "- Start assignments early\n"
            response += "- Form study groups with classmates\n\n"
            
            response += f"**Time Commitment:** 3 weeks, {course_found.get('credits', 3)} credits\n"
            response += f"Each week requires significant dedication outside of class time.\n\n"
            
            response += "Ready to enroll? Check the Smart Path Planner to add this course to your schedule!"
            
        else:
            # Generic preparation advice
            response = "**Preparing for Your Classes**\n\n"
            response += "I didn't catch which specific course you're asking about, but here's general preparation advice:\n\n"
            
            response += "**Before Any Course Starts:**\n"
            response += "1. **Research the course:**\n"
            response += "   - Read the course description\n"
            response += "   - Check what skills are covered\n"
            response += "   - See who the instructor is\n\n"
            
            response += "2. **Assess prerequisites:**\n"
            response += "   - Do you have the required background?\n"
            response += "   - Need to review any concepts?\n"
            response += "   - Should you take a prep course first?\n\n"
            
            response += "3. **Plan your time:**\n"
            response += "   - Each module is 3 weeks\n"
            response += "   - Count on 10-15 hours/week per course\n"
            response += "   - Can you commit to the schedule?\n\n"
            
            response += "4. **Prepare mentally:**\n"
            response += "   - Ready to learn actively (not just passively)\n"
            response += "   - Open to challenges and making mistakes\n"
            response += "   - Committed to showing up (3 absences = fail!)\n\n"
            
            response += "**To get specific preparation tips:**\n"
            response += "Ask me: \"How to prepare for [course name]\" with the actual course name\n\n"
            
            response += "**Example:**\n"
            response += '- "How to prepare for Introduction to Machine Learning"\n'
            response += '- "Get ready for Web Development Fundamentals"\n\n'
            
            response += "I'll give you detailed, course-specific preparation guidance!"
        
        return pd.DataFrame(), {}, response
    
    def _handle_schedule_query(self, query, major):
        """Handle schedule and timing queries - improved for morning/afternoon/evening"""
        query_lower = query.lower()
        
        # Determine what time user is asking about
        time_filter = None
        if 'morning' in query_lower:
            time_filter = 'morning'
        elif 'afternoon' in query_lower:
            time_filter = 'afternoon'
        elif 'evening' in query_lower:
            time_filter = 'evening'
        
        major_courses = self.courses_df[
            self.courses_df['category'].str.contains(major, case=False, na=False)
        ].head(15)  # Get more courses to filter by time
        
        # Group by time slots
        morning = []
        afternoon = []
        evening = []
        
        explanations = {}
        for _, course in major_courses.iterrows():
            time_slot = course.get('class_time', 'Morning (9:00 AM - 12:20 PM)')
            course_id = course['course_id']
            
            course_info = {
                'id': course_id,
                'name': course['course_name'],
                'time': time_slot,
                'difficulty': course.get('estimated_difficulty', 'Intermediate')
            }
            
            if 'Morning' in time_slot or '9' in time_slot:
                morning.append(course_info)
            elif 'Afternoon' in time_slot or '1' in time_slot or '2' in time_slot:
                afternoon.append(course_info)
            else:
                evening.append(course_info)
                
            explanations[course_id] = [
                f"Scheduled: {time_slot}",
                f"Duration: 3 weeks, 3 hours 20 min per session"
            ]
        
        # Build response based on what user asked
        if time_filter == 'morning':
            response = f"**Morning Classes for {major}** (9:00 AM - 12:20 PM)\n\n"
            response += "Perfect for early birds! Here are available morning courses:\n\n"
            for idx, course in enumerate(morning[:6], 1):
                response += f"{idx}. **{course['name']}**\n"
                response += f"   Time: {course['time']} | Level: {course['difficulty']}\n\n"
            
            if len(morning) > 6:
                response += f"_+ {len(morning) - 6} more morning courses available_\n\n"
            response += "Would you like details on any specific course?"
            
            courses_to_return = self.courses_df[self.courses_df['course_id'].isin([c['id'] for c in morning[:6]])]
            return courses_to_return, explanations, response
            
        elif time_filter == 'afternoon':
            response = f"**Afternoon Classes for {major}** (1:00 PM - 4:20 PM)\n\n"
            response += "Great for afternoon learners! Here are available afternoon courses:\n\n"
            for idx, course in enumerate(afternoon[:6], 1):
                response += f"{idx}. **{course['name']}**\n"
                response += f"   Time: {course['time']} | Level: {course['difficulty']}\n\n"
            
            if len(afternoon) > 6:
                response += f"_+ {len(afternoon) - 6} more afternoon courses available_\n\n"
            response += "Would you like details on any specific course?"
            
            courses_to_return = self.courses_df[self.courses_df['course_id'].isin([c['id'] for c in afternoon[:6]])]
            return courses_to_return, explanations, response
            
        elif time_filter == 'evening':
            response = f"**Evening Classes for {major}** (5:00 PM - 8:20 PM)\n\n"
            response += "Perfect for night owls! Here are available evening courses:\n\n"
            for idx, course in enumerate(evening[:6], 1):
                response += f"{idx}. **{course['name']}**\n"
                response += f"   Time: {course['time']} | Level: {course['difficulty']}\n\n"
            
            if len(evening) > 6:
                response += f"_+ {len(evening) - 6} more evening courses available_\n\n"
            response += "Would you like details on any specific course?"
            
            courses_to_return = self.courses_df[self.courses_df['course_id'].isin([c['id'] for c in evening[:6]])]
            return courses_to_return, explanations, response
        
        # Default: show all time slots
        response = f"**Schedule Overview for {major} Courses**\n\n"
        
        response += "**Morning Sessions** (9:00 AM - 12:20 PM):\n"
        for course in morning[:3]:
            response += f"  • {course['name']} - {course['difficulty']}\n"
        
        response += "\n**Afternoon Sessions** (1:00 PM - 4:20 PM):\n"
        for course in afternoon[:3]:
            response += f"  • {course['name']} - {course['difficulty']}\n"
        
        response += "\n**Evening Sessions** (5:00 PM - 8:20 PM):\n"
        for course in evening[:3]:
            response += f"  • {course['name']} - {course['difficulty']}\n"
        
        response += "\n**Tip:** Choose time slots that match your productivity hours!\n"
        response += "Try: \"morning classes\" or \"evening courses\" for more details."
        
        return major_courses.head(9), explanations, response
    
    def _handle_career_query(self, query, major, career_goal, experience_level):
        """Handle career-related queries"""
        response = f"Let's plan your path to {career_goal if career_goal else 'success'}!\n\n"
        
        # Get career-aligned courses
        career_keywords = self._get_career_keywords(career_goal if career_goal else query)
        
        career_courses = self.courses_df[
            self.courses_df['skills_covered_str'].str.contains('|'.join(career_keywords), case=False, na=False) |
            self.courses_df['course_description'].str.contains('|'.join(career_keywords), case=False, na=False)
        ].head(4)
        
        if career_courses.empty:
            career_courses = self.courses_df[
                self.courses_df['category'].str.contains(major, case=False, na=False)
            ].head(4)
        
        response += f"Career-Aligned Courses:\n\n"
        
        explanations = {}
        for idx, (_, course) in enumerate(career_courses.iterrows(), 1):
            course_id = course['course_id']
            response += f"{idx}. {course['course_name']}\n"
            response += f"   Why: Prepares you for {career_goal if career_goal else 'industry roles'}\n"
            response += f"   Industry value: High demand skill\n"
            
            if course_id in self.course_lecturer_map:
                lecturer = self.course_lecturer_map[course_id]
                response += f"   Instructor: {lecturer['name']} at {lecturer['company']}\n"
            
            response += "\n"
            
            explanations[course_id] = [
                f"Essential for {career_goal if career_goal else 'your career'}",
                "Industry-relevant skills",
                "Taught by professionals"
            ]
        
        response += f"\nCareer Tip: Combine technical courses with projects. Consider auditing complementary courses to broaden your skill set. Would you like advice on course priority?"
        
        return career_courses, explanations, response
    
    def _handle_module_planning_query(self, query, major, career_goal, experience_level, program):
        """Handle queries about module planning"""
        # Get suitable courses for the major
        major_courses = self.courses_df[
            self.courses_df['category'].str.contains(major, case=False, na=False)
        ].head(6)
        
        if major_courses.empty:
            major_courses = self.courses_df.head(6)
        
        response = f"Here's a suggested module plan for {major}:\n\n"
        response += f"Module 1 (Current - 3 weeks):\n"
        
        # Group courses for module planning
        mandatory = major_courses[major_courses['course_type'] == 'mandatory']
        secondary = major_courses[major_courses['course_type'] == 'secondary']
        
        # Show 2-3 courses for current module
        module_courses = []
        if len(mandatory) >= 2:
            module_courses.extend([mandatory.iloc[0], mandatory.iloc[1]])
        elif len(mandatory) == 1:
            module_courses.append(mandatory.iloc[0])
            if not secondary.empty:
                module_courses.append(secondary.iloc[0])
        else:
            if len(secondary) >= 2:
                module_courses.extend([secondary.iloc[0], secondary.iloc[1]])
        
        explanations = {}
        for idx, course in enumerate(module_courses, 1):
            course_id = course['course_id']
            response += f"  {idx}. {course['course_name']} ({course_id})\n"
            response += f"     Time: {course.get('class_time', 'TBD')} | Credits: {course.get('credits', 6)}\n"
            
            if course_id in self.course_lecturer_map:
                lecturer = self.course_lecturer_map[course_id]
                response += f"     Instructor: {lecturer['name']}\n"
            
            explanations[course_id] = [
                f"Core course for {major}",
                f"Scheduled: {course.get('class_time', 'TBD')}"
            ]
        
        response += f"\nModule 2 (Next - 3 weeks):\n"
        response += f"  Coming soon - will be planned based on your progress\n\n"
        
        response += f"Module 3 (Future):\n"
        response += f"  Coming soon - advanced courses\n\n"
        
        response += "Each module runs for 3 weeks with 3-4 courses. Would you like details on any specific course or help with scheduling?"
        
        return pd.DataFrame(module_courses) if module_courses else major_courses.head(3), explanations, response
    
    def _handle_program_info_query(self, query, major, career_goal, experience_level, program):
        """Handle queries about what courses are in a specific major/program"""
        query_lower = query.lower()
        
        # Detect which program/major the user is asking about
        program_mappings = {
            'Computer Science': ['computer science', 'cs', 'computing'],
            'Data Science': ['data science', 'data analytics', 'analytics'],
            'Cyber Security': ['cyber security', 'cybersecurity', 'infosec', 'security'],
            'Front-End Development': ['front-end development', 'frontend development', 'frontend', 'front-end', 'web development'],
            'Interaction Design': ['interaction design', 'ux design', 'ui design', 'design'],
            'Digital Marketing': ['digital marketing', 'marketing'],
            'High-Tech Entrepreneurship': ['entrepreneurship', 'high-tech entrepreneurship', 'business', 'startup'],
            'Digital Transformation': ['digital transformation', 'transformation'],
            'Product Management': ['product management', 'pm'],
            'Fintech': ['fintech', 'financial technology'],
            'Applied Data and Computer Science': ['applied data', 'applied computer science']
        }
        
        # Find which program is being asked about
        target_program = None
        for program_name, keywords in program_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                target_program = program_name
                break
        
        # If no specific program detected, use the student's current major/program
        if not target_program:
            target_program = program if program else major
        
        # Get all courses for this program (search in category field which contains Program)
        program_courses = self.courses_df[
            self.courses_df['category'].str.contains(target_program, case=False, na=False)
        ].copy()
        
        if program_courses.empty:
            response = f"I couldn't find courses specifically for {target_program}.\n\n"
            response += "Available programs include:\n"
            response += "- Computer Science\n"
            response += "- Data Science\n"
            response += "- Cyber Security\n"
            response += "- Front-End Development\n"
            response += "- Interaction Design\n"
            response += "- Digital Marketing\n"
            response += "- High-Tech Entrepreneurship\n"
            response += "- Fintech\n"
            response += "- Product Management\n"
            response += "- Digital Transformation\n\n"
            response += "Which program would you like to learn about?"
            return pd.DataFrame(), {}, response
        
        # Sort by course type (mandatory first, then secondary, then audit)
        course_type_order = {'mandatory': 1, 'secondary': 2, 'audit': 3}
        program_courses['type_order'] = program_courses['course_type'].map(course_type_order).fillna(4)
        program_courses = program_courses.sort_values('type_order')
        
        # Build response
        response = f"**{target_program} Program**\n\n"
        response += f"Total Courses Available: {len(program_courses)}\n\n"
        
        # Group by course type
        mandatory = program_courses[program_courses['course_type'] == 'mandatory']
        secondary = program_courses[program_courses['course_type'] == 'secondary']
        audit = program_courses[program_courses['course_type'] == 'audit']
        
        explanations = {}
        
        if not mandatory.empty:
            response += f"**MANDATORY COURSES ({len(mandatory)} courses):**\n"
            response += "These are required for graduation:\n\n"
            for idx, (_, course) in enumerate(mandatory.head(10).iterrows(), 1):
                course_id = course['course_id']
                response += f"{idx}. {course['course_name']} ({course_id})\n"
                response += f"   Credits: {course.get('credits', 6)} | Level: {course.get('estimated_difficulty', 'Intermediate')}\n"
                response += f"   Schedule: {course.get('class_time', 'TBD')}\n"
                
                if course_id in self.course_lecturer_map:
                    lecturer = self.course_lecturer_map[course_id]
                    response += f"   Instructor: {lecturer['name']}\n"
                
                response += f"   {course.get('course_description', '')[:100]}...\n\n"
                
                explanations[course_id] = [
                    f"Mandatory course for {target_program}",
                    "Required for graduation",
                    f"Taught by industry expert"
                ]
        
        if not secondary.empty:
            response += f"\n**SECONDARY/ELECTIVE COURSES ({len(secondary)} courses):**\n"
            response += "Recommended courses to enhance your skills:\n\n"
            for idx, (_, course) in enumerate(secondary.head(10).iterrows(), 1):
                course_id = course['course_id']
                response += f"{idx}. {course['course_name']} ({course_id})\n"
                response += f"   Credits: {course.get('credits', 4)} | Level: {course.get('estimated_difficulty', 'Intermediate')}\n"
                response += f"   Schedule: {course.get('class_time', 'TBD')}\n\n"
                
                explanations[course_id] = [
                    f"Elective for {target_program}",
                    "Counts towards credits"
                ]
        
        if not audit.empty:
            response += f"\n**AUDIT COURSES ({len(audit)} courses):**\n"
            response += "Additional learning opportunities (no credits):\n\n"
            for idx, (_, course) in enumerate(audit.head(5).iterrows(), 1):
                course_id = course['course_id']
                response += f"{idx}. {course['course_name']} ({course_id})\n\n"
                
                explanations[course_id] = [
                    "Audit course - no credits",
                    "For learning and exploration"
                ]
        
        response += f"\n**Program Highlights:**\n"
        response += f"- Total courses: {len(program_courses)}\n"
        response += f"- Mandatory courses: {len(mandatory)}\n"
        response += f"- Elective courses: {len(secondary)}\n"
        response += f"- Duration: 3 weeks per course\n"
        response += f"- Schedule: Morning, Afternoon, or Evening slots\n\n"
        
        response += "Would you like details on any specific course or help planning your module schedule?"
        
        # Return up to 15 courses to show variety
        return program_courses.head(15), explanations, response
    
    def _handle_course_recommendation(self, query, major, career_goal, experience_level, program, limit):
        """Handle standard course recommendation requests"""
        try:
            # Get available courses for major
            major_courses = self.courses_df[
                self.courses_df['category'].str.contains(major, case=False, na=False)
            ].copy()
            
            if major_courses.empty:
                major_courses = self.courses_df.copy()
            
            # If still empty, return helpful fallback
            if major_courses.empty:
                return self._handle_unknown_query(query, major, career_goal)
                
            # Score and rank courses
            scored_courses = self._score_courses(
                major_courses, 
                major, 
                career_goal, 
                experience_level,
                program,
                query
            )
            
            # Get top N recommendations
            top_courses = scored_courses.head(limit)
            
            # If no courses match well, provide fallback
            if top_courses.empty or len(top_courses) < 3:
                return self._handle_unknown_query(query, major, career_goal)
            
            # Generate detailed explanations
            explanations = self._generate_detailed_explanations(
                top_courses, 
                major, 
                career_goal, 
                experience_level,
                program,
                query
            )
            
            # Generate conversational AI response
            ai_response = self._generate_conversational_response(
                top_courses, 
                explanations, 
                major, 
                career_goal,
                query
            )
            
            return top_courses, explanations, ai_response
            
        except Exception as e:
            # Handle any errors gracefully
            return self._handle_unknown_query(query, major, career_goal, error=str(e))
        
    def _generate_detailed_explanations(self, courses, major, career_goal, experience_level, program, query):
        """Generate detailed explanations for each recommendation"""
        explanations = {}
        
        for idx, course in courses.iterrows():
            explanation_parts = []
            course_id = course['course_id']
            
            # Best for major/program
            explanation_parts.append(f"**Best for:** {major} students in {program} program")
            
            # Course level and type
            course_type = course.get('course_type', 'secondary')
            difficulty = course.get('estimated_difficulty', 'Intermediate')
            
            if course_type == 'mandatory':
                explanation_parts.append(f"**Course Type:** Required core course for {major} - 6 credits")
            elif course_type == 'secondary':
                explanation_parts.append(f"**Course Type:** Graded elective - 4 credits (counts toward degree)")
            else:
                explanation_parts.append(f"**Course Type:** Audit option - 0 credits (explore without grades)")
                
            explanation_parts.append(f"**Difficulty Level:** {difficulty} - Suitable for {experience_level} students")
            
            # Lecturer information
            if course_id in self.course_lecturer_map:
                lecturer = self.course_lecturer_map[course_id]
                explanation_parts.append(
                    f"**Instructor:** {lecturer['name']}, {lecturer['job_title']} at {lecturer['company']}"
                )
                explanation_parts.append(f"**Expertise:** {lecturer['expertise_areas']}")
                
            # Skills preparation
            prereq_skills = self._get_prerequisite_skills(course)
            if prereq_skills:
                explanation_parts.append(f"**Skills to Prepare:** {', '.join(prereq_skills)}")
                
            # Career alignment
            if career_goal:
                career_keywords = self._get_career_keywords(career_goal)
                course_skills = str(course.get('skills_covered_str', '')).lower().split(',')
                matching_skills = [s.strip() for s in course_skills if any(k in s for k in career_keywords)]
                if matching_skills:
                    explanation_parts.append(f"**Career Relevance:** Directly applicable to {career_goal} role")
                    
            # Course combination suggestions
            audit_suggestion = self._get_audit_combination_suggestion(course, courses)
            if audit_suggestion:
                explanation_parts.append(f"**Recommended Audit Combination:** Pair with {audit_suggestion}")
                
            # Time and schedule
            explanation_parts.append(f"**Duration:** 3 weeks intensive | **Credits:** {course.get('credits', 3)}")
            
            explanations[course_id] = explanation_parts
            
        return explanations
        
    def _get_prerequisite_skills(self, course):
        """Determine prerequisite skills for a course"""
        course_name = str(course.get('course_name', '')).lower()
        difficulty = str(course.get('estimated_difficulty', 'Intermediate'))
        category = str(course.get('category', '')).lower()
        
        prerequisites = []
        
        # Advanced courses need more prep
        if difficulty == 'Advanced':
            prerequisites.append(f"Intermediate {category} knowledge")
            
        # Specific course prerequisites
        if 'machine learning' in course_name or 'deep learning' in course_name:
            prerequisites.extend(['Python programming', 'Basic statistics', 'Linear algebra'])
        elif 'data' in course_name:
            prerequisites.extend(['Python basics', 'SQL fundamentals'])
        elif 'web' in course_name or 'frontend' in course_name:
            prerequisites.extend(['HTML/CSS basics', 'JavaScript fundamentals'])
        elif 'security' in course_name or 'cyber' in course_name:
            prerequisites.extend(['Networking basics', 'Operating systems knowledge'])
        elif 'database' in course_name:
            prerequisites.extend(['SQL basics', 'Data modeling concepts'])
            
        return prerequisites[:3]  # Limit to top 3
        
    def _get_audit_combination_suggestion(self, main_course, all_courses):
        """Suggest audit course that complements the main course"""
        # Find complementary audit courses
        main_skills = set(str(main_course.get('skills_covered_str', '')).lower().split(','))
        main_category = str(main_course.get('category', '')).lower()
        
        audit_courses = all_courses[all_courses['course_type'] == 'audit']
        
        for _, audit in audit_courses.iterrows():
            if audit['course_id'] == main_course['course_id']:
                continue
                
            audit_skills = set(str(audit.get('skills_covered_str', '')).lower().split(','))
            audit_category = str(audit.get('category', '')).lower()
            
            # Check for complementary skills (not too similar, not too different)
            overlap = len(main_skills & audit_skills)
            if overlap > 0 and overlap < 3:
                return f"{audit['course_name']} ({audit['course_id']})"
                
        return None
        
    def _generate_conversational_response(self, courses, explanations, major, career_goal, query):
        """Generate natural, conversational AI response - like ChatGPT"""
        if courses.empty:
            return (
                f"I couldn't find specific courses matching that query. "
                f"As a {major} student, I can help you with course recommendations, "
                f"lecturer information, schedules, or module planning. What would you like to know?"
            )
        
        # Natural, conversational introduction
        if query and len(query.split()) <= 2:
            response = f"Here are the {query} courses available:\n\n"
        elif career_goal:
            response = f"For {career_goal}, I recommend these courses:\n\n"
        else:
            response = f"Based on your {major} major, here are relevant courses:\n\n"
        
        # Show courses in clean format without emojis
        for idx, (_, course) in enumerate(courses.iterrows(), 1):
            course_id = course['course_id']
            
            # Course header
            response += f"{idx}. {course['course_name']} ({course_id})\n"
            response += f"   Level: {course.get('estimated_difficulty', 'Intermediate')} | Credits: {course.get('credits', 6)}\n"
            
            # Lecturer info (removed company name)
            if course_id in self.course_lecturer_map:
                lecturer = self.course_lecturer_map[course_id]
                response += f"   Instructor: {lecturer['name']}, {lecturer['job_title']}\n"
            
            # Time slot
            response += f"   Schedule: {course.get('class_time', 'TBD')}\n"
            
            # Key reason
            if course_id in explanations and explanations[course_id]:
                response += f"   Why: {explanations[course_id][0]}\n"
                
            response += "\n"
        
        # Conversational closing
        if len(courses) == 1:
            response += "Would you like to know more about prerequisites, similar courses, or module planning?"
        elif len(courses) <= 3:
            response += "Would you like details on any specific course, or help choosing between them?"
        else:
            response += "I can provide more details on any course. What would you like to know?"
        
        return response
        
    def generate_smart_schedule(self, student_profile, enrolled_courses=None, completed_courses=None, limit_modules=4):
        """
        Generate intelligent module schedule with time slots
        Respects bachelor/master level, filters capstones, mixes majors
        """
        major = student_profile.get('major', 'Computer Science')
        program = student_profile.get('program', "Bachelor's Degree")
        
        # Determine level
        level = 'bachelor' if 'bachelor' in program.lower() else 'master'
        
        # Safety check: ensure courses_df exists and has data
        if self.courses_df is None or self.courses_df.empty:
            return []
        
        # Get courses for this level (with safety check for Level column)
        if 'Level' in self.courses_df.columns:
            level_courses = self.courses_df[
                self.courses_df['Level'].str.lower() == level
            ].copy()
        else:
            level_courses = self.courses_df.copy()
        
        if level_courses.empty:
            level_courses = self.courses_df.copy()
        
        # Filter out capstone/seminar courses from early modules (they're for year 3+)
        capstone_keywords = ['capstone', 'seminar', 'thesis', 'final project', 'graduation project']
        if 'Course' in level_courses.columns:
            early_module_courses = level_courses[
                ~level_courses['Course'].str.lower().str.contains('|'.join(capstone_keywords), na=False)
            ].copy()
        elif 'course_name' in level_courses.columns:
            early_module_courses = level_courses[
                ~level_courses['course_name'].str.lower().str.contains('|'.join(capstone_keywords), na=False)
            ].copy()
        else:
            early_module_courses = level_courses.copy()
        
        # Get PRIMARY major courses (will be mandatory)
        if 'category' in early_module_courses.columns:
            major_courses = early_module_courses[
                early_module_courses['category'].str.contains(major, case=False, na=False)
            ].copy()
            
            # Get COMPLEMENTARY courses from other majors (will be secondary/audit)
            other_courses = early_module_courses[
                ~early_module_courses['category'].str.contains(major, case=False, na=False)
            ].copy()
        else:
            # If no category column, use all courses as major courses
            major_courses = early_module_courses.copy()
            other_courses = pd.DataFrame()
        
        if major_courses.empty:
            major_courses = early_module_courses.copy()
            
        # DON'T filter out enrolled courses - keep them visible but mark as enrolled
        # Only filter completed courses
        if completed_courses:
            major_courses = major_courses[~major_courses['course_id'].isin(completed_courses)]
            other_courses = other_courses[~other_courses['course_id'].isin(completed_courses)]
        
        # Shuffle to get variety but keep seed for consistency per session
        major_courses = major_courses.sample(frac=1, random_state=hash(major) % 100).reset_index(drop=True)
        other_courses = other_courses.sample(frac=1, random_state=hash(major) % 100 + 1).reset_index(drop=True)
        
        # Set course types based on major match
        # PRIMARY major courses = mandatory
        major_courses['course_type'] = 'mandatory'
        
        # OTHER major courses = secondary/audit (mix)
        if not other_courses.empty:
            total_other = len(other_courses)
            other_courses['course_type'] = 'secondary'
            # Make some audit (30%)
            audit_count = int(total_other * 0.3)
            if audit_count > 0:
                other_courses.iloc[-audit_count:, other_courses.columns.get_loc('course_type')] = 'audit'
        
        # Combine for distribution
        all_courses = pd.concat([major_courses.head(10), other_courses.head(10)], ignore_index=True)
        
        # Separate by type
        mandatory = all_courses[all_courses['course_type'] == 'mandatory'].head(10)
        secondary = all_courses[all_courses['course_type'] == 'secondary'].head(10)
        audit = all_courses[all_courses['course_type'] == 'audit'].head(6)
        
        # If no course types are set, distribute them - SMART distribution (fewer mandatory)
        if mandatory.empty and secondary.empty and audit.empty:
            total = len(major_courses)
            # NEW: Only 1-2 mandatory per module, rest are flexible
            major_courses = major_courses.copy()
            major_courses['course_type'] = 'secondary'
            if total > 0:
                # Only 20% mandatory (about 1 per module), 50% secondary, 30% audit
                mandatory_count = max(3, min(4, int(total * 0.20)))  # 3-4 total mandatory
                secondary_count = int(total * 0.50)
                major_courses.iloc[:mandatory_count, major_courses.columns.get_loc('course_type')] = 'mandatory'
                major_courses.iloc[mandatory_count:mandatory_count+secondary_count, major_courses.columns.get_loc('course_type')] = 'secondary'
                if total > mandatory_count + secondary_count:
                    major_courses.iloc[mandatory_count+secondary_count:, major_courses.columns.get_loc('course_type')] = 'audit'
            
            mandatory = major_courses[major_courses['course_type'] == 'mandatory']
            secondary = major_courses[major_courses['course_type'] == 'secondary']
            audit = major_courses[major_courses['course_type'] == 'audit']
        
        modules = []
        start_date = datetime.now()
        
        # Module 1 - 5-6 courses: 1 mandatory + 3-4 secondary + 1 audit
        if not all_courses.empty:
            m1_courses = []
            # Add only 1 mandatory course from student's major
            if len(mandatory) >= 1:
                m1_courses.append(mandatory.iloc[0])
            
            # Add 3-4 secondary courses (from other majors)
            if len(secondary) >= 4:
                m1_courses.extend([secondary.iloc[0], secondary.iloc[1], secondary.iloc[2], secondary.iloc[3]])
            elif len(secondary) >= 3:
                m1_courses.extend([secondary.iloc[0], secondary.iloc[1], secondary.iloc[2]])
            elif len(secondary) >= 2:
                m1_courses.extend([secondary.iloc[0], secondary.iloc[1]])
            elif len(secondary) == 1:
                m1_courses.append(secondary.iloc[0])
            
            # Add 1 audit option
            if not audit.empty:
                m1_courses.append(audit.iloc[0])
                
            if m1_courses:
                modules.append(self._create_module(
                    "Module 1",
                    m1_courses,
                    start_date,
                    f"Foundation courses for {major}",
                    1
                ))
                
        # Module 2 - 5-6 courses: 1 mandatory + 3-4 secondary + 1 audit
        if len(mandatory) > 1 or len(secondary) > 4:
            m2_courses = []
            # Add only 1 mandatory
            if len(mandatory) >= 2:
                m2_courses.append(mandatory.iloc[1])
            
            # Add 3-4 secondary
            if len(secondary) >= 8:
                m2_courses.extend([secondary.iloc[4], secondary.iloc[5], secondary.iloc[6], secondary.iloc[7]])
            elif len(secondary) >= 6:
                m2_courses.extend([secondary.iloc[4], secondary.iloc[5], secondary.iloc[6]])
            elif len(secondary) >= 5:
                m2_courses.extend([secondary.iloc[4], secondary.iloc[5]])
            elif len(secondary) == 5:
                m2_courses.append(secondary.iloc[4])
            
            # Add 1 audit
            if len(audit) > 1:
                m2_courses.append(audit.iloc[1])
                
            if m2_courses:
                modules.append(self._create_module(
                    "Module 2",
                    m2_courses,
                    start_date + timedelta(weeks=3),
                    f"Core {major} development",
                    2
                ))
                
        # Module 3 - 5-6 courses: 1 mandatory + 3-4 secondary + 1 audit
        if len(mandatory) > 2 or len(secondary) > 8:
            m3_courses = []
            # Add only 1 mandatory
            if len(mandatory) >= 3:
                m3_courses.append(mandatory.iloc[2])
            
            # Add 3-4 secondary (FIX: proper bounds checking)
            if len(secondary) >= 12:
                m3_courses.extend([secondary.iloc[8], secondary.iloc[9], secondary.iloc[10], secondary.iloc[11]])
            elif len(secondary) >= 11:
                m3_courses.extend([secondary.iloc[8], secondary.iloc[9], secondary.iloc[10]])
            elif len(secondary) >= 10:
                m3_courses.extend([secondary.iloc[8], secondary.iloc[9]])
            elif len(secondary) >= 9:
                m3_courses.append(secondary.iloc[8])
            
            # Add 1 audit
            if len(audit) > 2:
                m3_courses.append(audit.iloc[2])
                
            if m3_courses:
                modules.append(self._create_module(
                    "Module 3",
                    m3_courses,
                    start_date + timedelta(weeks=6),
                    f"{major} specialization and exploration",
                    3
                ))
                
        # YEAR 2 - Modules 4, 5, 6 (Second Year)
        # Module 4 - Start of Year 2
        if len(mandatory) > 3 or len(secondary) > 12:
            m4_courses = []
            if len(mandatory) >= 4:
                m4_courses.append(mandatory.iloc[3])
            if len(secondary) >= 15:
                m4_courses.extend([secondary.iloc[12], secondary.iloc[13], secondary.iloc[14]])
            elif len(secondary) >= 14:
                m4_courses.extend([secondary.iloc[12], secondary.iloc[13]])
            elif len(secondary) >= 13:
                m4_courses.append(secondary.iloc[12])
            if len(audit) > 3:
                m4_courses.append(audit.iloc[3])
                
            if m4_courses:
                modules.append(self._create_module(
                    "Module 4 (Year 2)",
                    m4_courses,
                    start_date + timedelta(weeks=52),  # Year 2 starts
                    f"Year 2: Advanced {major} concepts",
                    4
                ))
        
        # Module 5 - Mid Year 2
        if len(secondary) > 15:
            m5_courses = []
            if len(secondary) >= 18:
                m5_courses.extend([secondary.iloc[15], secondary.iloc[16], secondary.iloc[17]])
            elif len(secondary) >= 17:
                m5_courses.extend([secondary.iloc[15], secondary.iloc[16]])
            elif len(secondary) >= 16:
                m5_courses.append(secondary.iloc[15])
            if len(audit) > 4:
                m5_courses.append(audit.iloc[4])
                
            if m5_courses:
                modules.append(self._create_module(
                    "Module 5 (Year 2)",
                    m5_courses,
                    start_date + timedelta(weeks=55),
                    f"Year 2: {major} specialization",
                    5
                ))
        
        # Module 6 - End of Year 2
        if len(secondary) > 18:
            m6_courses = []
            if len(secondary) >= 21:
                m6_courses.extend([secondary.iloc[18], secondary.iloc[19], secondary.iloc[20]])
            elif len(secondary) >= 20:
                m6_courses.extend([secondary.iloc[18], secondary.iloc[19]])
            elif len(secondary) >= 19:
                m6_courses.append(secondary.iloc[18])
            if len(audit) > 5:
                m6_courses.append(audit.iloc[5])
                
            if m6_courses:
                modules.append(self._create_module(
                    "Module 6 (Year 2)",
                    m6_courses,
                    start_date + timedelta(weeks=58),
                    f"Year 2: Capstone preparation",
                    6
                ))
        
        # YEAR 3 - Modules 7, 8, 9 (if needed for 3-year program)
        # Module 7 - Start of Year 3
        if len(secondary) > 21:
            m7_courses = []
            if len(secondary) >= 24:
                m7_courses.extend([secondary.iloc[21], secondary.iloc[22], secondary.iloc[23]])
            elif len(secondary) >= 23:
                m7_courses.extend([secondary.iloc[21], secondary.iloc[22]])
            elif len(secondary) >= 22:
                m7_courses.append(secondary.iloc[21])
                
            if m7_courses:
                modules.append(self._create_module(
                    "Module 7 (Year 3)",
                    m7_courses,
                    start_date + timedelta(weeks=104),  # Year 3 starts
                    f"Year 3: Advanced specialization",
                    7
                ))
                
        # Limit to specified number of modules
        return modules[:limit_modules]
        
    def _create_module(self, name, courses, start_date, description, module_number):
        """Create a module with time slots assigned to courses"""
        # Assign time slots to courses (3 courses per day)
        courses_with_times = []
        for idx, course in enumerate(courses):
            time_slot = CLASS_TIMES[idx % 3]
            course_dict = course.to_dict() if hasattr(course, 'to_dict') else course
            course_dict['time_slot'] = time_slot['time']
            course_dict['slot_number'] = time_slot['slot']
            courses_with_times.append(course_dict)
            
        return {
            'module_name': name,
            'module_number': module_number,
            'courses': courses_with_times,
            'start_date': start_date,
            'end_date': start_date + timedelta(weeks=3),
            'total_credits': sum(c.get('credits', 3) for c in courses_with_times),
            'description': description
        }
        
    def _handle_unknown_query(self, query, major, career_goal, error=None):
        """Handle queries that the AI doesn't understand or can't find courses for - conversational style"""
        
        import random
        
        # Conversational opening - vary the response
        openings = [
            f"Thanks for asking about **\"{query}\"**! ",
            f"Interesting question about **\"{query}\"**! ",
            f"I appreciate you asking about **\"{query}\"**. ",
            f"Good question! You asked about **\"{query}\"**. "
        ]
        
        response = random.choice(openings)
        
        # Honest explanation - vary these too
        limitations = [
            "I'm still learning and my knowledge is somewhat limited right now. ",
            "My vocabulary is growing every day, but I don't have an answer for this specific question yet. ",
            "I'm an AI that's continuously improving, and while I can't fully answer this right now, ",
            "I don't quite understand this question at the moment, but I'm learning more each day! "
        ]
        
        response += random.choice(limitations)
        response += "Let me guide you to what I can help with.\n\n"
        
        # Provide helpful alternatives in conversational tone
        response += f"**I'm really good at helping with:**\n\n"
        
        response += f"**Finding Courses ({major}):**\n"
        response += "Ask me things like:\n"
        response += '- "software" or "business" or "data science"\n'
        response += '- "ML courses"\n'
        response += '- "What courses should I take?"\n'
        response += '- "Show me programming classes"\n\n'
        
        response += "**Class Schedules & Times:**\n"
        response += '- "Morning classes"\n'
        response += '- "Evening courses"\n'
        response += '- "When is [course name]?"\n\n'
        
        response += "**Instructors & Faculty:**\n"
        response += '- "Lecturers"\n'
        response += '- "Who teaches machine learning?"\n'
        response += '- "Tell me about the professors"\n\n'
        
        response += "**Student Support & Guidance:**\n"
        response += '- "What if I skip mandatory class?"\n'
        response += '- "I have an issue" or "I need help"\n'
        response += '- "How to prepare for [course name]"\n'
        response += '- "What happens if I miss too many classes?"\n\n'
        
        response += "**Academic Information:**\n"
        response += '- "How long is bachelor?" or "program duration"\n'
        response += '- "What is mandatory vs audit?"\n'
        response += '- "Attendance policy"\n'
        response += '- "Career advice"\n\n'
        
        if career_goal:
            response += f"**Your Career Goal ({career_goal}):**\n"
            response += f'- "Courses for {career_goal}"\n'
            response += f'- "Skills needed for {career_goal}"\n'
            response += f'- "Best path to become {career_goal}"\n\n'
        
        # Encouraging closing
        closings = [
            "Try asking one of these, and I'll give you a detailed answer! My knowledge is growing, and I'm here to support your academic journey.",
            "Feel free to rephrase your question using the examples above. I'm getting smarter every day and want to help you succeed!",
            "Don't hesitate to ask in different words - I might understand better! I'm continuously learning to serve you better.",
            "Use the quick buttons below or try one of these questions. I'm improving constantly and committed to helping you!"
        ]
        
        response += random.choice(closings)
        
        # Return empty dataframe and explanations with the helpful response
        return pd.DataFrame(), {}, response
    
    def get_lecturer_details(self, course_id):
        """Get detailed lecturer information for a course"""
        if course_id in self.course_lecturer_map:
            return self.course_lecturer_map[course_id]
        return None
        
    def get_all_lecturer_courses(self, lecturer_name):
        """Get all courses taught by a specific lecturer"""
        lecturer_courses = []
        for course_id, lecturer_info in self.course_lecturer_map.items():
            if lecturer_info['name'] == lecturer_name:
                course = self.courses_df[self.courses_df['course_id'] == course_id]
                if not course.empty:
                    lecturer_courses.append(course.iloc[0])
        return lecturer_courses
    
    def check_timetable_conflict(self, enrolled_courses, new_course):
        """
        Check if a new course conflicts with already enrolled courses
        
        Args:
            enrolled_courses: List of course dicts with 'class_time' field
            new_course: Course dict to check for conflicts
            
        Returns:
            Tuple of (has_conflict: bool, conflicting_courses: list)
        """
        if not enrolled_courses:
            return False, []
        
        new_time = new_course.get('class_time', '')
        if not new_time:
            return False, []
        
        conflicting = []
        for course in enrolled_courses:
            existing_time = course.get('class_time', '')
            if existing_time and existing_time == new_time:
                conflicting.append(course.get('course_name', 'Unknown Course'))
        
        return len(conflicting) > 0, conflicting
    
    def get_all_timetable_conflicts(self, course_list):
        """
        Find all timetable conflicts within a list of courses
        
        Args:
            course_list: List of course dicts with 'class_time' field
            
        Returns:
            List of conflict tuples: [(course1_name, course2_name, time), ...]
        """
        conflicts = []
        time_groups = {}
        
        # Group courses by time slot
        for course in course_list:
            time = course.get('class_time', '')
            if time:
                if time not in time_groups:
                    time_groups[time] = []
                time_groups[time].append(course.get('course_name', 'Unknown'))
        
        # Find groups with more than one course
        for time, courses in time_groups.items():
            if len(courses) > 1:
                # Add all pairs in this time slot
                for i in range(len(courses)):
                    for j in range(i + 1, len(courses)):
                        conflicts.append((courses[i], courses[j], time))
        
        return conflicts
    
    def suggest_alternative_time(self, course_name, excluded_times=None):
        """
        Suggest alternative time slots for a course
        
        Args:
            course_name: Name of the course
            excluded_times: List of time slots to exclude
            
        Returns:
            List of alternative course offerings with different times
        """
        if excluded_times is None:
            excluded_times = []
        
        # In a real system, this would query a database for alternative sections
        # For now, we'll return available time slots
        all_times = ["9:00 AM - 12:20 PM", "1:00 PM - 4:20 PM", "5:00 PM - 8:20 PM"]
        available_times = [t for t in all_times if t not in excluded_times]
        
        return available_times
    
    def generate_conflict_warning(self, conflicting_courses, new_course_name):
        """
        Generate a user-friendly warning message about timetable conflicts
        
        Args:
            conflicting_courses: List of course names that conflict
            new_course_name: Name of the course being added
            
        Returns:
            Warning message string
        """
        if not conflicting_courses:
            return ""
        
        warning = f"⚠️ **TIMETABLE CONFLICT WARNING** ⚠️\n\n"
        warning += f"You cannot enroll in **{new_course_name}** because it conflicts with:\n\n"
        
        for course in conflicting_courses:
            warning += f"• {course}\n"
        
        warning += "\n**Important:** Students cannot attend two courses scheduled at the same time.\n"
        warning += "**Solution:** Choose courses with different time slots (Morning/Afternoon/Evening).\n"
        
        return warning
