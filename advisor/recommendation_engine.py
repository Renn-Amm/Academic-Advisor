import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pickle
import os

class CourseRecommender:
    def __init__(self, data_path="data/processed/"):
        self.data_path = data_path
        self.courses_df = None
        self.programs_df = None
        self.students_df = None
        self.grades_df = None
        self.tfidf_vectorizer = None
        self.course_features = None
        self.scaler = StandardScaler()
        
        self.load_data()
        self.prepare_recommendation_engine()
    
    def load_data(self):
        """Load all processed datasets"""
        try:
            self.courses_df = pd.read_csv(f"{self.data_path}harbour_space_courses.csv")
            self.programs_df = pd.read_csv(f"{self.data_path}harbour_space_programs.csv")
            self.students_df = pd.read_csv(f"{self.data_path}sample_students.csv")
            self.grades_df = pd.read_csv(f"{self.data_path}sample_grades.csv")
            
            # Enhance courses data with professor names and proper structure
            self.courses_df = self.enhance_courses_data(self.courses_df)
            
            print("Data loaded successfully")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def enhance_courses_data(self, courses_df):
        """Enhance courses data with additional fields"""
        # Add professor names if missing
        if 'professor' not in courses_df.columns:
            professors = [
                "Dr. Elena Rodriguez", "Prof. Marcus Chen", "Dr. Sarah Johnson", 
                "Prof. James Wilson", "Dr. Maria Garcia", "Prof. David Kim",
                "Dr. Lisa Thompson", "Prof. Alex Morgan", "Dr. Rachel Green"
            ]
            courses_df['professor'] = np.random.choice(professors, len(courses_df))
        
        # Ensure course IDs are properly formatted
        if 'course_id' not in courses_df.columns:
            courses_df['course_id'] = courses_df.apply(self.generate_course_id, axis=1)
        
        # Set duration to 3 weeks and proper credits
        courses_df['duration_weeks'] = 3
        courses_df['credits'] = courses_df.apply(
            lambda row: 6 if any(keyword in str(row.get('course_name', '')).lower() 
            for keyword in ['core', 'fundamental', 'advanced', 'machine learning', 'data structure']) else 4, 
            axis=1
        )
        
        return courses_df
    
    def generate_course_id(self, row):
        """Generate proper course IDs"""
        category_map = {
            'Computer Science': 'CS',
            'Data Science': 'DS', 
            'Cybersecurity': 'CY',
            'Web Development': 'WD',
            'Business': 'BU',
            'Design': 'DE',
            'Marketing': 'MK',
            'Technology': 'CS',
            'Creative': 'CR'
        }
        
        prefix = category_map.get(row.get('category', 'CS'), 'CS')
        level = '1' if 'Introduction' in str(row.get('course_name', '')) else '2'
        number = f"{hash(row.get('course_name', '')) % 100:02d}"
        
        return f"{prefix}{level}{number}"
    
    def prepare_recommendation_engine(self):
        """Prepare the AI recommendation engine with enhanced features"""
        # Combine text features for course similarity
        self.courses_df['combined_features'] = (
            self.courses_df['course_name'] + " " + 
            self.courses_df['course_description'] + " " + 
            self.courses_df['skills_covered_str'] + " " +
            self.courses_df['category'] + " " +
            self.courses_df['professor']
        ).fillna('')
        
        # TF-IDF for content-based filtering
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1500)
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.courses_df['combined_features'])
        
        # Calculate course similarities
        self.course_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Prepare enhanced numerical features for ranking
        numerical_features = self.courses_df[['credits', 'duration_weeks']].copy()
        numerical_features['difficulty_score'] = self.courses_df['estimated_difficulty'].map({
            'Beginner': 1, 'Intermediate': 2, 'Advanced': 3
        })
        numerical_features['skills_count'] = self.courses_df['skills_count']
        
        # Add career relevance scores
        numerical_features['career_relevance'] = self.calculate_career_relevance_scores()
        
        self.course_features = self.scaler.fit_transform(numerical_features)
        
        print("Enhanced recommendation engine prepared")
    
    def calculate_career_relevance_scores(self):
        """Calculate career relevance scores for courses"""
        career_keywords = {
            'Data Scientist': ['machine learning', 'data science', 'statistics', 'python', 'data analysis'],
            'Software Engineer': ['software engineering', 'algorithms', 'web development', 'java', 'system design'],
            'Cybersecurity Analyst': ['cybersecurity', 'security', 'cryptography', 'ethical hacking', 'network security'],
            'Product Manager': ['product management', 'business', 'strategy', 'leadership', 'user research'],
            'UX Designer': ['design', 'user experience', 'prototyping', 'ui', 'user research']
        }
        
        relevance_scores = []
        for _, course in self.courses_df.iterrows():
            course_text = f"{course['course_name']} {course['course_description']}".lower()
            max_score = 0
            for career, keywords in career_keywords.items():
                score = sum(1 for keyword in keywords if keyword in course_text)
                max_score = max(max_score, score)
            relevance_scores.append(max_score)
        
        return relevance_scores
    
    def get_student_profile(self, student_id):
        """Get enhanced student profile and academic history"""
        student = self.students_df[self.students_df['student_id'] == student_id].iloc[0]
        student_grades = self.grades_df[self.grades_df['student_id'] == student_id]
        
        # Calculate student's performance in different categories
        category_performance = {}
        for category in self.courses_df['category'].unique():
            category_courses = student_grades[student_grades['course_name'].isin(
                self.courses_df[self.courses_df['category'] == category]['course_name']
            )]
            if not category_courses.empty:
                grade_scores = category_courses['grade'].map({
                    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                    'C+': 2.3, 'C': 2.0, 'D': 1.0, 'F': 0.0
                })
                category_performance[category] = grade_scores.mean()
        
        return {
            'student_info': student,
            'completed_courses': student_grades,
            'category_performance': category_performance,
            'preferred_learning_style': student.get('preferred_learning_style', 'Visual'),
            'interests': student.get('interests', '').split(', '),
            'career_goals': student.get('career_goals', 'Software Engineer'),
            'major': student.get('major', 'Computer Science'),
            'current_gpa': student.get('current_gpa', 3.0)
        }
    
    def recommend_courses(self, student_id, top_n=10, strategy='hybrid', career_goal=None):
        """Generate enhanced course recommendations for a student"""
        student_profile = self.get_student_profile(student_id)
        
        if career_goal:
            student_profile['career_goals'] = career_goal
        
        if strategy == 'content_based':
            return self._content_based_recommendations(student_profile, top_n)
        elif strategy == 'collaborative':
            return self._collaborative_recommendations(student_profile, top_n)
        elif strategy == 'career_focused':
            return self._career_focused_recommendations(student_profile, top_n)
        else:  # hybrid
            return self._hybrid_recommendations(student_profile, top_n)
    
    def _content_based_recommendations(self, student_profile, top_n):
        """Enhanced content-based recommendations using course features"""
        # Get student interests and career goals
        interests_text = ' '.join(student_profile['interests']) + ' ' + student_profile['career_goals']
        
        # Vectorize student interests
        student_vector = self.tfidf_vectorizer.transform([interests_text])
        
        # Calculate similarity with all courses
        course_vectors = self.tfidf_vectorizer.transform(self.courses_df['combined_features'])
        similarities = cosine_similarity(student_vector, course_vectors).flatten()
        
        # Get top similar courses
        similar_indices = similarities.argsort()[-top_n*2:][::-1]
        recommendations = self.courses_df.iloc[similar_indices].copy()
        recommendations['similarity_score'] = similarities[similar_indices]
        
        # Filter out already completed courses
        completed_courses = student_profile['completed_courses']['course_name'].tolist()
        recommendations = recommendations[~recommendations['course_name'].isin(completed_courses)]
        
        return recommendations.head(top_n)
    
    def _collaborative_recommendations(self, student_profile, top_n):
        """Enhanced collaborative filtering based on similar students"""
        # Find similar students based on completed courses and performance
        student_grades = student_profile['completed_courses']
        
        if student_grades.empty:
            return self._content_based_recommendations(student_profile, top_n)
        
        # Enhanced similar student finding
        similar_students = self._find_similar_students_enhanced(student_profile)
        
        # Get courses taken by similar students with good grades
        similar_courses = self.grades_df[
            (self.grades_df['student_id'].isin(similar_students)) & 
            (self.grades_df['grade'].isin(['A', 'A-', 'B+']))
        ]
        
        # Remove courses already taken by the student
        taken_courses = student_grades['course_name'].tolist()
        recommended_courses = similar_courses[~similar_courses['course_name'].isin(taken_courses)]
        
        # Get top courses by frequency and grade with enhanced scoring
        course_recommendations = recommended_courses.groupby('course_name').agg({
            'grade': lambda x: (x.isin(['A', 'A-', 'B+'])).mean(),
            'student_id': 'count'
        }).rename(columns={'student_id': 'popularity', 'grade': 'success_rate'})
        
        # Enhanced scoring formula
        course_recommendations['score'] = (
            course_recommendations['popularity'] * 0.4 + 
            course_recommendations['success_rate'] * 0.6
        )
        
        top_courses = course_recommendations.nlargest(top_n, 'score')
        recommendations = self.courses_df[
            self.courses_df['course_name'].isin(top_courses.index)
        ].copy()
        
        return recommendations
    
    def _career_focused_recommendations(self, student_profile, top_n):
        """Career-focused recommendations based on skill gaps"""
        career_goal = student_profile['career_goals']
        
        # Analyze skill gaps
        skill_gaps = self.analyze_skill_gaps(student_profile, career_goal)
        
        # Get courses that address skill gaps
        gap_courses = []
        for skill in skill_gaps['missing_skills']:
            skill_courses = self.courses_df[
                self.courses_df['skills_covered_str'].str.contains(skill, case=False, na=False)
            ]
            gap_courses.extend(skill_courses.to_dict('records'))
        
        # Remove duplicates and already taken courses
        unique_courses = []
        seen_courses = set()
        completed_courses = student_profile['completed_courses']['course_name'].tolist()
        
        for course in gap_courses:
            course_name = course['course_name']
            if course_name not in seen_courses and course_name not in completed_courses:
                unique_courses.append(course)
                seen_courses.add(course_name)
        
        return pd.DataFrame(unique_courses).head(top_n)
    
    def _hybrid_recommendations(self, student_profile, top_n):
        """Enhanced hybrid approach combining multiple strategies"""
        content_recs = self._content_based_recommendations(student_profile, top_n * 2)
        collaborative_recs = self._collaborative_recommendations(student_profile, top_n * 2)
        career_recs = self._career_focused_recommendations(student_profile, top_n * 2)
        
        # Combine and rank recommendations
        all_recs = pd.concat([content_recs, collaborative_recs, career_recs]).drop_duplicates('course_name')
        
        # Calculate final score based on multiple enhanced factors
        all_recs['final_score'] = self._calculate_enhanced_final_score(all_recs, student_profile)
        
        return all_recs.nlargest(top_n, 'final_score')
    
    def _find_similar_students_enhanced(self, student_profile, n_similar=15):
        """Enhanced similar student finding considering multiple factors"""
        student_major = student_profile['student_info']['major']
        student_career_goal = student_profile['career_goals']
        student_gpa = student_profile['student_info']['current_gpa']
        
        # Find students with same major and similar career goals
        similar_students = self.students_df[
            (self.students_df['major'] == student_major) |
            (self.students_df['career_goals'] == student_career_goal)
        ]
        
        # Further filter by GPA range
        similar_students = similar_students[
            abs(similar_students['current_gpa'] - student_gpa) < 0.7
        ]
        
        return similar_students['student_id'].head(n_similar).tolist()
    
    def analyze_skill_gaps(self, student_profile, target_job):
        """Analyze skill gaps for career-focused recommendations"""
        completed_courses = student_profile['completed_courses']['course_name'].tolist()
        
        # Get current skills from completed courses
        current_skills = set()
        for course_name in completed_courses:
            course = self.courses_df[self.courses_df['course_name'] == course_name]
            if not course.empty:
                skills = str(course.iloc[0]['skills_covered_str']).split(', ')
                current_skills.update([s.strip().lower() for s in skills if s.strip()])
        
        # Define target job skills
        job_skills = {
            'Data Scientist': {'python', 'machine learning', 'statistics', 'sql', 'data visualization', 
                             'deep learning', 'data analysis', 'algorithms'},
            'Software Engineer': {'python', 'java', 'algorithms', 'system design', 'databases', 
                                'web development', 'software engineering', 'testing'},
            'Cybersecurity Analyst': {'network security', 'cryptography', 'ethical hacking', 
                                    'risk assessment', 'security protocols', 'penetration testing'},
            'Product Manager': {'product strategy', 'user research', 'agile', 'project management',
                              'business analysis', 'market research'},
            'UX Designer': {'user research', 'wireframing', 'prototyping', 'usability testing',
                          'interaction design', 'visual design'}
        }
        
        target_skills = job_skills.get(target_job, set())
        missing_skills = target_skills - current_skills
        
        return {
            'current_skills': list(current_skills),
            'required_skills': list(target_skills),
            'missing_skills': list(missing_skills),
            'coverage_percentage': len(current_skills.intersection(target_skills)) / len(target_skills) * 100
        }
    
    def _calculate_enhanced_final_score(self, recommendations, student_profile):
        """Calculate enhanced final recommendation score"""
        scores = []
        
        for _, course in recommendations.iterrows():
            score = 0
            
            # Career goal alignment (enhanced)
            career_goal = student_profile['career_goals'].lower()
            course_text = course['combined_features'].lower()
            if career_goal in course_text:
                score += 0.3
            
            # Interest alignment (enhanced)
            interests = [interest.lower() for interest in student_profile['interests']]
            interest_match = sum(1 for interest in interests if interest in course_text)
            score += min(interest_match * 0.2, 0.4)  # Cap at 0.4
            
            # Major alignment
            if course['category'].lower() == student_profile['major'].lower():
                score += 0.2
            
            # Difficulty appropriateness (enhanced)
            student_gpa = student_profile['current_gpa']
            course_difficulty = course['estimated_difficulty']
            
            if course_difficulty == 'Beginner' and student_gpa < 3.0:
                score += 0.15
            elif course_difficulty == 'Intermediate' and 3.0 <= student_gpa < 3.5:
                score += 0.15
            elif course_difficulty == 'Advanced' and student_gpa >= 3.5:
                score += 0.15
            
            # Skills development (prefer courses with more skills)
            score += min(course['skills_count'] * 0.08, 0.24)  # Cap at 0.24
            
            # Career relevance bonus
            career_keywords = ['machine learning', 'data science', 'web development', 'cybersecurity']
            if any(keyword in course_text for keyword in career_keywords):
                score += 0.1
            
            scores.append(score)
        
        return scores
    
    def generate_smart_schedule(self, student_id, max_courses_per_term=4, available_hours=20):
        """Generate optimized multi-term schedule"""
        student_profile = self.get_student_profile(student_id)
        completed_courses = student_profile['completed_courses']['course_name'].tolist()
        
        # Get available courses (not completed)
        available_courses = self.courses_df[~self.courses_df['course_name'].isin(completed_courses)].copy()
        
        # Calculate priority scores for each course
        available_courses['priority_score'] = available_courses.apply(
            lambda row: self._calculate_course_priority(row, student_profile), axis=1
        )
        
        # Sort by priority
        available_courses = available_courses.sort_values('priority_score', ascending=False)
        
        # Distribute across terms considering workload
        schedule = {}
        term = 1
        current_term_courses = []
        current_workload = 0
        
        for _, course in available_courses.iterrows():
            course_workload = course['credits'] * 3  
            
            if (len(current_term_courses) < max_courses_per_term and 
                current_workload + course_workload <= available_hours):
                
                current_term_courses.append(course)
                current_workload += course_workload
            
            if (len(current_term_courses) >= max_courses_per_term or 
                current_workload + course_workload > available_hours):
                
                schedule[f'Term {term}'] = {
                    'courses': current_term_courses.copy(),
                    'total_workload': current_workload,
                    'total_credits': sum(c['credits'] for c in current_term_courses)
                }
                
                current_term_courses = []
                current_workload = 0
                term += 1
        
        if current_term_courses:
            schedule[f'Term {term}'] = {
                'courses': current_term_courses,
                'total_workload': current_workload,
                'total_credits': sum(c['credits'] for c in current_term_courses)
            }
        
        return schedule
    
    def _calculate_course_priority(self, course, student_profile):
        """Calculate priority score for course scheduling"""
        score = 0
        
        # Career goal alignment
        career_goal = student_profile['career_goals'].lower()
        course_text = f"{course['course_name']} {course['course_description']}".lower()
        if career_goal in course_text:
            score += 3
        
        # Prerequisite chain importance
        # (In a real implementation, this would check actual prerequisite chains)
        
        # Difficulty balance
        difficulty_bonus = {
            'Beginner': 0.5,
            'Intermediate': 1.0,
            'Advanced': 1.5
        }
        score += difficulty_bonus.get(course['estimated_difficulty'], 1.0)
        
        return score
    
    def explain_recommendation(self, course_name, student_id):
        """Provide enhanced explanation for why a course was recommended"""
        student_profile = self.get_student_profile(student_id)
        course = self.courses_df[self.courses_df['course_name'] == course_name].iloc[0]
        
        explanation = {
            'course': course_name,
            'course_id': course.get('course_id', 'N/A'),
            'reasons': [],
            'alignment_score': 0,
            'skills_gained': course['skills_covered_str'],
            'professor': course.get('professor', 'TBA'),
            'credits': course.get('credits', 3),
            'duration': course.get('duration_weeks', 3)
        }
        
        # Check career goal alignment
        career_goal = student_profile['career_goals']
        course_text = course['combined_features'].lower()
        if career_goal.lower() in course_text:
            explanation['reasons'].append(f"Directly supports your career goal: {career_goal}")
            explanation['alignment_score'] += 0.3
        
        # Check interest alignment
        interests = student_profile['interests']
        matching_interests = [interest for interest in interests if interest.lower() in course_text]
        if matching_interests:
            explanation['reasons'].append(f"Aligns with your interests: {', '.join(matching_interests)}")
            explanation['alignment_score'] += len(matching_interests) * 0.15
        
        # Check major alignment
        if course['category'].lower() == student_profile['major'].lower():
            explanation['reasons'].append("Core requirement for your major")
            explanation['alignment_score'] += 0.2
        
        # Check difficulty appropriateness
        student_gpa = student_profile['current_gpa']
        course_difficulty = course['estimated_difficulty']
        if (course_difficulty == 'Beginner' and student_gpa < 3.0 or
            course_difficulty == 'Intermediate' and 3.0 <= student_gpa < 3.5 or
            course_difficulty == 'Advanced' and student_gpa >= 3.5):
            explanation['reasons'].append("Appropriate difficulty level for your academic performance")
            explanation['alignment_score'] += 0.15
        
        return explanation