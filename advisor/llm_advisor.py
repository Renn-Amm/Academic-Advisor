"""
LLM-Powered AI Academic Advisor
Uses OpenAI GPT to generate dynamic, conversational responses
"""
import os
import json
import hashlib
import time
import logging
from typing import Dict, List, Tuple, Optional
from collections import deque
from datetime import datetime, timedelta
import pandas as pd
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAdvisor:
    """AI Advisor powered by Large Language Model for dynamic conversations"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo",
                 enable_caching: bool = True, enable_rate_limiting: bool = True):
        """
        Initialize LLM Advisor
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env variable)
            model: Model to use (gpt-3.5-turbo or gpt-4)
            enable_caching: Enable response caching to reduce API calls
            enable_rate_limiting: Enable rate limiting to prevent API overuse
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = model
        self.courses_df = None
        self.lecturers_df = None
        self.programs_df = None
        self.conversation_history = []
        self.knowledge_base = self._load_knowledge_base()
        
        # Caching
        self.enable_caching = enable_caching
        self.cache = {} if enable_caching else None
        self.cache_ttl = 3600  # 1 hour TTL
        
        # Rate limiting
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limit_window = 60  # 1 minute window
        self.max_requests_per_window = 20  # Max 20 requests per minute
        self.request_timestamps = deque(maxlen=self.max_requests_per_window)
        
        # Usage tracking
        self.api_calls_count = 0
        self.cache_hits = 0
        self.total_tokens_used = 0
        
    def _load_knowledge_base(self) -> Dict:
        """Load AI knowledge base for handling general queries"""
        try:
            kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai_knowledge_base.json')
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Could not load knowledge base: {e}")
            return {}
    
    def load_data(self, courses_df: pd.DataFrame, lecturers_df: pd.DataFrame, programs_df: pd.DataFrame = None):
        """Load academic data for context"""
        self.courses_df = courses_df
        self.lecturers_df = lecturers_df
        self.programs_df = programs_df
        
    def _build_system_context(self, student_profile: Dict) -> str:
        """Build comprehensive system context for the LLM"""
        
        major = student_profile.get('major', 'Computer Science')
        career_goal = student_profile.get('career_goal', '')
        experience_level = student_profile.get('experience_level', 'Beginner')
        program = student_profile.get('program', 'Bachelor')
        
        context = f"""You are an AI Academic Advisor at Harbour.Space University, a leading tech university.

STUDENT PROFILE:
- Major: {major}
- Career Goal: {career_goal}
- Experience Level: {experience_level}
- Program: {program}

YOUR ROLE:
You are a helpful, knowledgeable academic advisor who:
- Provides personalized course recommendations
- Explains programs, courses, and academic policies
- Answers questions about lecturers and faculty
- Helps with schedule planning and timetable conflicts
- Gives career guidance and preparation advice
- Supports students with academic issues
- Explains tech concepts and new technologies
- Provides daily conversation support and general help

IMPORTANT ACADEMIC POLICIES:
1. ATTENDANCE POLICY (CRITICAL):
   - 3 or more absences = AUTOMATIC FAIL (no exceptions)
   - Being 10 minutes late = Counts as 1 absence
   - This applies to ALL mandatory and secondary courses
   - Audit courses have flexible attendance

2. COURSE TYPES:
   - Mandatory: Required for degree, graded, strict attendance
   - Secondary: Elective, graded, strict attendance  
   - Audit: Optional, not graded, flexible attendance, for learning only

3. TIMETABLE CONFLICTS:
   - Classes are in 3 time slots: 9:00-12:20, 13:00-16:20, 17:00-20:20
   - Students CANNOT enroll in courses with the same time slot
   - Always warn about schedule conflicts

4. PROGRAM DURATION:
   - Bachelor's: 3 years (full-time)
   - Master's: 1 year (intensive)
   - Module-based: 3 weeks per module, ~12 modules/year

COMMUNICATION STYLE:
- Be conversational and friendly, but professional
- Generate your own words - don't use templates
- Admit when you don't know something
- Be concise but informative
- Use bullet points for clarity
- Always provide actionable advice

AVAILABLE DATA:
"""
        
        # Add knowledge base context for tech topics
        if self.knowledge_base:
            context += "\nTECH KNOWLEDGE BASE AVAILABLE:\n"
            if 'tech_topics' in self.knowledge_base:
                topics = list(self.knowledge_base['tech_topics'].keys())
                context += f"Can explain: {', '.join(topics[:8])}\n"
            if 'university_info' in self.knowledge_base:
                context += "Have detailed university policies and program information\n"
            if 'career_guidance' in self.knowledge_base:
                context += "Can provide career guidance for various roles\n"
        
        # Add course information
        if self.courses_df is not None and not self.courses_df.empty:
            context += f"\nCOURSES AVAILABLE: {len(self.courses_df)} courses\n"
            
            # Sample some courses for context
            sample_courses = self.courses_df.head(5)
            context += "Sample courses:\n"
            for _, course in sample_courses.iterrows():
                context += f"- {course['course_name']} ({course['course_id']}): {course.get('category', 'N/A')}, "
                context += f"{course.get('estimated_difficulty', 'Intermediate')}, {course.get('class_time', 'TBD')}\n"
        
        # Add lecturer information
        if self.lecturers_df is not None and not self.lecturers_df.empty:
            context += f"\nLECTURERS AVAILABLE: {len(self.lecturers_df)} faculty members\n"
            
            # Sample some lecturers
            sample_lecturers = self.lecturers_df.head(3)
            context += "Sample lecturers:\n"
            for _, lect in sample_lecturers.iterrows():
                context += f"- {lect['name']}: {lect.get('job_title', 'Instructor')}, "
                context += f"Expertise: {lect.get('expertise_areas', 'Technology')}\n"
        
        context += """
When answering questions:
1. Search the available courses/lecturers data when relevant
2. Use knowledge base for tech topics and general information
3. Generate natural, conversational responses
4. Be specific with course names, IDs, and details
5. Always check and warn about timetable conflicts
6. Provide actionable next steps
7. Be honest if you need more information
8. For greetings and general queries, be friendly and helpful
"""
        
        return context
    
    def _search_relevant_courses(self, query: str, student_profile: Dict, limit: int = 8) -> pd.DataFrame:
        """Search for courses relevant to the query"""
        if self.courses_df is None or self.courses_df.empty:
            return pd.DataFrame()
        
        query_lower = query.lower()
        major = student_profile.get('major', '')
        
        # Search in multiple fields
        relevant_courses = self.courses_df[
            self.courses_df['course_name'].str.contains(query_lower, case=False, na=False) |
            self.courses_df['course_description'].str.contains(query_lower, case=False, na=False) |
            self.courses_df['skills_covered_str'].str.contains(query_lower, case=False, na=False) |
            self.courses_df['category'].str.contains(query_lower, case=False, na=False)
        ]
        
        # If no results, try major-specific courses
        if relevant_courses.empty and major:
            relevant_courses = self.courses_df[
                self.courses_df['category'].str.contains(major, case=False, na=False)
            ]
        
        return relevant_courses.head(limit)
    
    def _search_relevant_lecturers(self, query: str, limit: int = 5) -> pd.DataFrame:
        """Search for lecturers relevant to the query"""
        if self.lecturers_df is None or self.lecturers_df.empty:
            return pd.DataFrame()
        
        query_lower = query.lower()
        
        # Search in name, expertise, job title, program
        relevant_lecturers = self.lecturers_df[
            self.lecturers_df['name'].str.contains(query_lower, case=False, na=False) |
            self.lecturers_df['expertise_areas'].str.contains(query_lower, case=False, na=False) |
            self.lecturers_df['job_title'].str.contains(query_lower, case=False, na=False) |
            self.lecturers_df['program'].str.contains(query_lower, case=False, na=False)
        ]
        
        return relevant_lecturers.head(limit)
    
    def _detect_timetable_conflict(self, enrolled_courses: List[Dict], new_course: Dict) -> bool:
        """
        Detect if there's a timetable conflict between enrolled courses and a new course
        
        Args:
            enrolled_courses: List of courses student is already enrolled in
            new_course: Course to check for conflicts
            
        Returns:
            True if there's a conflict, False otherwise
        """
        if not enrolled_courses:
            return False
        
        new_time = new_course.get('class_time', '')
        if not new_time:
            return False
        
        for course in enrolled_courses:
            existing_time = course.get('class_time', '')
            if existing_time and existing_time == new_time:
                return True
        
        return False
    
    def get_timetable_conflicts(self, course_list: List[Dict]) -> List[Tuple[str, str]]:
        """
        Find all timetable conflicts in a list of courses
        
        Args:
            course_list: List of courses with class_time
            
        Returns:
            List of tuples with conflicting course names
        """
        conflicts = []
        
        for i, course1 in enumerate(course_list):
            for course2 in course_list[i+1:]:
                time1 = course1.get('class_time', '')
                time2 = course2.get('class_time', '')
                
                if time1 and time2 and time1 == time2:
                    conflicts.append((course1.get('course_name', 'Unknown'), 
                                    course2.get('course_name', 'Unknown')))
        
        return conflicts
    
    def generate_response(self, query: str, student_profile: Dict, 
                         enrolled_courses: Optional[List[Dict]] = None) -> Tuple[str, pd.DataFrame]:
        """
        Generate AI response to student query using LLM
        
        Args:
            query: Student's question
            student_profile: Student information (major, career_goal, etc.)
            enrolled_courses: Currently enrolled courses (for conflict detection)
            
        Returns:
            Tuple of (response_text, relevant_courses_df)
        """
        if not self.client:
            return self._generate_fallback_response(query, student_profile)
        
        # Search for relevant data
        relevant_courses = self._search_relevant_courses(query, student_profile)
        relevant_lecturers = self._search_relevant_lecturers(query)
        
        # Build context
        system_context = self._build_system_context(student_profile)
        
        # Check knowledge base for relevant info
        kb_context = self._get_knowledge_base_context(query)
        
        # Add search results to context
        user_context = f"Student query: {query}\n\n"
        
        # Add knowledge base context if relevant
        if kb_context:
            user_context += f"KNOWLEDGE BASE INFO:\n{kb_context}\n\n"
        
        if not relevant_courses.empty:
            user_context += "RELEVANT COURSES FOUND:\n"
            for idx, course in relevant_courses.iterrows():
                user_context += f"- {course['course_name']} ({course['course_id']})\n"
                user_context += f"  Category: {course.get('category', 'N/A')}\n"
                user_context += f"  Difficulty: {course.get('estimated_difficulty', 'Intermediate')}\n"
                user_context += f"  Time: {course.get('class_time', 'TBD')}\n"
                user_context += f"  Type: {course.get('course_type', 'secondary')}\n"
                user_context += f"  Description: {course.get('course_description', 'N/A')[:150]}...\n"
                
                # Check for timetable conflicts
                if enrolled_courses:
                    course_dict = course.to_dict()
                    if self._detect_timetable_conflict(enrolled_courses, course_dict):
                        user_context += f"  ⚠️ TIMETABLE CONFLICT: This course conflicts with your enrolled courses!\n"
                user_context += "\n"
        
        if not relevant_lecturers.empty:
            user_context += "RELEVANT LECTURERS FOUND:\n"
            for idx, lect in relevant_lecturers.iterrows():
                user_context += f"- {lect['name']}: {lect.get('job_title', 'Instructor')}\n"
                user_context += f"  Program: {lect.get('program', 'N/A')}\n"
                user_context += f"  Expertise: {lect.get('expertise_areas', 'N/A')}\n"
                user_context += f"  Email: {lect.get('email', 'N/A')}\n\n"
        
        # Generate response using GPT
        try:
            messages = [
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_context}
            ]
            
            # Add conversation history if available (increased context)
            for msg in self.conversation_history[-10:]:  # Last 5 exchanges
                messages.append(msg)
            
            # Check cache first
            cache_key = self._generate_cache_key(query, student_profile)
            if self.enable_caching and cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    self.cache_hits += 1
                    logger.info(f"Cache hit for query: {query[:50]}...")
                    return cache_entry['response'], cache_entry['courses']
            
            # Rate limiting check
            if self.enable_rate_limiting and not self._check_rate_limit():
                logger.warning("Rate limit exceeded. Please wait.")
                return "I'm receiving too many requests right now. Please wait a moment and try again.", pd.DataFrame()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1200  # Increased for more detailed responses
            )
            
            ai_response = response.choices[0].message.content
            
            # Track usage
            self.api_calls_count += 1
            self.total_tokens_used += response.usage.total_tokens
            logger.info(f"API call #{self.api_calls_count}, Tokens: {response.usage.total_tokens}, Model: {self.model}")
            
            # Cache the response
            if self.enable_caching:
                self.cache[cache_key] = {
                    'response': ai_response,
                    'courses': relevant_courses,
                    'timestamp': time.time()
                }
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep only last 20 messages (10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return ai_response, relevant_courses
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._generate_fallback_response(query, student_profile)
    
    def _generate_fallback_response(self, query: str, student_profile: Dict) -> Tuple[str, pd.DataFrame]:
        """Fallback response when LLM is unavailable"""
        relevant_courses = self._search_relevant_courses(query, student_profile)
        
        response = f"I'm here to help with your {student_profile.get('major', 'academic')} journey!\n\n"
        
        if not relevant_courses.empty:
            response += f"I found {len(relevant_courses)} courses related to your query:\n\n"
            for idx, course in relevant_courses.iterrows():
                response += f"• {course['course_name']} - {course.get('estimated_difficulty', 'Intermediate')}\n"
                response += f"  Time: {course.get('class_time', 'TBD')}\n\n"
        else:
            response += "I couldn't find specific courses matching your query. Could you provide more details?\n\n"
        
        response += "💡 Tip: For the best experience, set up OpenAI API key to enable advanced AI responses."
        
        return response, relevant_courses
    
    def _get_knowledge_base_context(self, query: str) -> str:
        """Get relevant context from knowledge base"""
        if not self.knowledge_base:
            return ""
        
        query_lower = query.lower()
        context = ""
        
        # Check for tech topics
        if 'tech_topics' in self.knowledge_base:
            for topic, info in self.knowledge_base['tech_topics'].items():
                if topic.replace('_', ' ') in query_lower:
                    context += f"\n{topic.replace('_', ' ').title()}:\n"
                    if 'description' in info:
                        context += f"Description: {info['description']}\n"
                    if 'key_areas' in info:
                        context += f"Key Areas: {', '.join(info['key_areas'][:3])}\n"
                    if 'skills_to_learn' in info:
                        context += f"Skills: {', '.join(info['skills_to_learn'][:3])}\n"
                    break
        
        # Check for greetings
        if 'daily_conversations' in self.knowledge_base:
            for conv in self.knowledge_base['daily_conversations']:
                if any(pattern in query_lower for pattern in conv.get('patterns', [])):
                    if conv.get('category') == 'greetings':
                        context += "This is a greeting - be friendly and welcoming\n"
                    break
        
        # Check for career guidance
        if 'career_guidance' in self.knowledge_base and any(word in query_lower for word in ['career', 'job', 'become']):
            context += "\nCareer guidance available for various tech roles\n"
        
        return context
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def _generate_cache_key(self, query: str, student_profile: Dict) -> str:
        """Generate cache key from query and profile"""
        profile_str = f"{student_profile.get('major', '')}{student_profile.get('career_goal', '')}"
        cache_input = f"{query.lower()}{profile_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limit"""
        current_time = time.time()
        
        # Remove timestamps outside the window
        while self.request_timestamps and current_time - self.request_timestamps[0] > self.rate_limit_window:
            self.request_timestamps.popleft()
        
        # Check if we're at the limit
        if len(self.request_timestamps) >= self.max_requests_per_window:
            return False
        
        # Add current timestamp
        self.request_timestamps.append(current_time)
        return True
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        cache_hit_rate = (self.cache_hits / max(self.api_calls_count + self.cache_hits, 1)) * 100
        
        return {
            'api_calls': self.api_calls_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'total_tokens': self.total_tokens_used,
            'model': self.model,
            'cached_responses': len(self.cache) if self.cache else 0
        }
    
    def clear_cache(self):
        """Clear response cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def switch_model(self, model: str):
        """Switch between GPT models"""
        if model in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]:
            self.model = model
            logger.info(f"Switched to model: {model}")
        else:
            logger.warning(f"Unknown model: {model}")
