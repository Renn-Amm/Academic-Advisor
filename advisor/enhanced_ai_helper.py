"""
Additional helper methods for enhanced AI advisor
These methods handle different types of queries more intelligently
"""

import pandas as pd
from datetime import datetime

def analyze_query_intent(query):
    """Analyze what the user is really asking for"""
    if not query:
        return 'course_recommendation'
        
    query_lower = query.lower().strip()
    
    # Handle very short queries (1-2 words)
    words = query_lower.split()
    if len(words) <= 2:
        # Expand common abbreviations
        expansions = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ds': 'data science',
            'cs': 'computer science',
            'cyber': 'cybersecurity',
            'webdev': 'web development',
            'db': 'database'
        }
        for abbr, full in expansions.items():
            if abbr in query_lower:
                query_lower = query_lower.replace(abbr, full)
                
        return 'general_info'
    
    # Check for lecturer-related queries
    lecturer_keywords = ['lecturer', 'professor', 'instructor', 'teacher', 'who teaches', 'taught by']
    if any(kw in query_lower for kw in lecturer_keywords):
        return 'lecturer_info'
        
    # Check for schedule-related queries
    schedule_keywords = ['time', 'timing', 'schedule', 'when', 'morning', 'afternoon', 'evening']
    if any(kw in query_lower for kw in schedule_keywords):
        return 'schedule_info'
        
    # Check for career guidance
    career_keywords = ['career', 'job', 'future', 'work', 'industry', 'professional']
    if any(kw in query_lower for kw in career_keywords):
        return 'career_guidance'
        
    return 'course_recommendation'

def handle_general_info_query(self, query, major, career_goal, experience_level, program):
    """Handle general information queries about topics"""
    query_lower = query.lower().strip()
    
    # Find relevant courses
    relevant_courses = self.courses_df[
        self.courses_df['course_name'].str.contains(query_lower, case=False, na=False) |
        self.courses_df['course_description'].str.contains(query_lower, case=False, na=False) |
        self.courses_df['skills_covered_str'].str.contains(query_lower, case=False, na=False)
    ].head(4)
    
    if relevant_courses.empty:
        response = f"I understand you're interested in **{query}**. While I don't have courses with that exact name, let me help you find related options.\n\n"
        response += f"Could you tell me more about what aspect you're interested in? For example:\n"
        response += f"- Are you looking to learn the basics or advanced concepts?\n"
        response += f"- Is this for a specific project or career goal?\n"
        response += f"- Would you like to explore this as a main course or audit option?\n\n"
        response += f"I can then recommend the perfect courses for your needs!"
        return pd.DataFrame(), {}, response
    
    # Generate conversational response
    response = f"Great question about **{query}**! Here's what I can offer you:\n\n"
    
    # Add overview
    response += f"**Available {query.title()} Courses:**\n\n"
    
    explanations = {}
    for idx, (_, course) in enumerate(relevant_courses.iterrows(), 1):
        course_id = course['course_id']
        response += f"**{idx}. {course['course_name']}**\n"
        
        # Lecturer info
        if course_id in self.course_lecturer_map:
            lecturer = self.course_lecturer_map[course_id]
            response += f"   👨‍🏫 Taught by *{lecturer['name']}* ({lecturer['job_title']})"
            response += f" from {lecturer['company']}\n"
        
        # Key info
        response += f"   📊 Level: {course.get('estimated_difficulty', 'Intermediate')} | "
        response += f"⏱️ {course.get('class_time', 'TBD')}\n"
        response += f"   🎯 Focus: {course.get('course_description', '')[:100]}...\n\n"
        
        # Add to explanations
        explanations[course_id] = [
            f"Perfect for {major} students interested in {query}",
            f"Taught by industry expert",
            f"Practical, hands-on approach"
        ]
    
    response += f"\n💡 **My Recommendation:**\n"
    response += f"Since you're a {experience_level} {major} student, I'd suggest starting with **{relevant_courses.iloc[0]['course_name']}**. "
    response += f"It provides a solid foundation and you can build from there.\n\n"
    response += f"Want to know more about any specific course, prerequisites, or schedule?"
    
    return relevant_courses, explanations, response

def handle_lecturer_query(self, query, major):
    """Handle lecturer-specific queries"""
    response = f"Let me tell you about our expert lecturers!\n\n"
    
    # Find relevant lecturers
    query_lower = query.lower()
    relevant_lecturers = []
    
    for course_id, lecturer in self.course_lecturer_map.items():
        if (query_lower in lecturer['name'].lower() or
            any(exp.lower() in query_lower for exp in lecturer['expertise'])):
            relevant_lecturers.append((course_id, lecturer))
    
    if not relevant_lecturers:
        # Show all lecturers for the major
        major_courses = self.courses_df[
            self.courses_df['category'].str.contains(major, case=False, na=False)
        ].head(4)
        
        response += f"Here are some of our top instructors for {major}:\n\n"
        
        explanations = {}
        for _, course in major_courses.iterrows():
            course_id = course['course_id']
            if course_id in self.course_lecturer_map:
                lecturer = self.course_lecturer_map[course_id]
                response += f"**{lecturer['name']}** - {lecturer['job_title']}\n"
                response += f"   🏢 Company: {lecturer['company']}\n"
                response += f"   🎓 Teaches: {course['course_name']}\n"
                response += f"   💼 Expertise: {', '.join(lecturer['expertise'][:3])}\n"
                response += f"   📧 Contact: {lecturer['email']}\n\n"
                
                explanations[course_id] = [
                    f"Industry expert with real-world experience",
                    f"Specializes in {', '.join(lecturer['expertise'][:2])}"
                ]
        
        return major_courses.head(4), explanations, response
    
    # Show specific lecturer info
    courses_list = []
    explanations = {}
    
    for course_id, lecturer in relevant_lecturers[:3]:
        course = self.courses_df[self.courses_df['course_id'] == course_id].iloc[0]
        courses_list.append(course)
        
        response += f"**{lecturer['name']}** - {lecturer['job_title']}\n"
        response += f"   🏢 {lecturer['company']}\n"
        response += f"   🎓 Course: {course['course_name']}\n"
        response += f"   💼 Expert in: {', '.join(lecturer['expertise'])}\n"
        response += f"   📧 {lecturer['email']}\n\n"
        
        explanations[course_id] = [
            f"Taught by industry veteran",
            f"Brings real-world insights from {lecturer['company']}"
        ]
    
    response += f"\nWould you like to know more about any instructor's teaching style or course content?"
    
    return pd.DataFrame(courses_list), explanations, response

def handle_schedule_query(self, query, major):
    """Handle schedule and timing queries"""
    major_courses = self.courses_df[
        self.courses_df['category'].str.contains(major, case=False, na=False)
    ].head(6)
    
    response = f"Here's the schedule breakdown for {major} courses:\n\n"
    
    # Group by time slots
    morning = []
    afternoon = []
    evening = []
    
    explanations = {}
    for _, course in major_courses.iterrows():
        time_slot = course.get('class_time', 'Morning (9:00 AM - 12:20 PM)')
        course_id = course['course_id']
        
        course_info = f"**{course['course_name']}** - {time_slot}"
        
        if 'Morning' in time_slot or '9' in time_slot:
            morning.append(course_info)
        elif 'Afternoon' in time_slot or '1' in time_slot:
            afternoon.append(course_info)
        else:
            evening.append(course_info)
            
        explanations[course_id] = [
            f"Scheduled: {time_slot}",
            f"Duration: 3 hours 20 minutes"
        ]
    
    response += "🌅 **Morning Sessions (9:00 AM - 12:20 PM):**\n"
    for course in morning[:3]:
        response += f"   • {course}\n"
    
    response += "\n☀️ **Afternoon Sessions (1:00 PM - 4:20 PM):**\n"
    for course in afternoon[:3]:
        response += f"   • {course}\n"
    
    response += "\n🌙 **Evening Sessions (5:00 PM - 8:20 PM):**\n"
    for course in evening[:3]:
        response += f"   • {course}\n"
    
    response += "\n💡 **Tip:** Choose time slots that match your peak productivity hours!\n"
    response += "Need help building a conflict-free schedule?"
    
    return major_courses, explanations, response

def handle_career_query(self, query, major, career_goal, experience_level):
    """Handle career-related queries"""
    response = f"Let's plan your path to becoming a {career_goal if career_goal else 'professional'}!\n\n"
    
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
    
    response += f"📈 **Career-Aligned Courses for {career_goal if career_goal else 'Your Goal'}:**\n\n"
    
    explanations = {}
    for idx, (_, course) in enumerate(career_courses.iterrows(), 1):
        course_id = course['course_id']
        response += f"**{idx}. {course['course_name']}**\n"
        response += f"   🎯 Why it matters: Directly prepares you for {career_goal if career_goal else 'industry roles'}\n"
        response += f"   💼 Industry value: High demand skill\n"
        
        if course_id in self.course_lecturer_map:
            lecturer = self.course_lecturer_map[course_id]
            response += f"   👨‍🏫 Learn from: {lecturer['name']} at {lecturer['company']}\n"
        
        response += "\n"
        
        explanations[course_id] = [
            f"Essential for {career_goal if career_goal else 'your career'}",
            "Industry-relevant skills",
            "Taught by working professionals"
        ]
    
    response += f"\n🚀 **Career Tip:** Combine technical courses with practical projects. "
    response += f"Consider auditing complementary courses to broaden your skill set!\n\n"
    response += f"Want specific advice on which courses to prioritize?"
    
    return career_courses, explanations, response

def handle_course_recommendation(self, query, major, career_goal, experience_level, program, limit):
    """Handle standard course recommendation requests"""
    # Get available courses for major
    major_courses = self.courses_df[
        self.courses_df['category'].str.contains(major, case=False, na=False)
    ].copy()
    
    if major_courses.empty:
        major_courses = self.courses_df.copy()
        
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
