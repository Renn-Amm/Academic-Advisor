"""
Comprehensive Data Loader for Harbour Space Academic Advisor
Loads and processes all datasets with proper course IDs and skills mapping
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class DataLoader:
    """Load and process all Harbour Space datasets"""
    
    def __init__(self):
        self.bachelors_df = None
        self.masters_df = None
        self.lecturers_df = None
        self.programs_df = None
        self.courses_df = None
        
        # Program code mappings
        self.program_codes = {
            # Bachelor Programs
            'Computer Science': 'CS',
            'Data Science': 'DS',
            'Cyber Security': 'CY',
            'Front-End Development': 'FE',
            'Front-end Development': 'FE',
            'Interaction Design': 'ID',
            'Digital Marketing': 'DM',
            'High-Tech Entrepreneurship': 'HT',
            
            # Master Programs
            'Digital Transformation': 'DT',
            'Product Management': 'PM',
            'Fintech': 'FT',
            'Applied Data and Computer Science': 'ADCS',
            'Computer Science Masters': 'CSM',
            
            # General
            'Robotics': 'RB',
            'Architecture': 'AR',
            'Business': 'BU',
            'Marketing': 'MK'
        }
        
        # Skills mapping based on course names and categories
        # More specific keywords first (longer matches have priority)
        self.skills_map = {
            # Specific computing topics (check course name first)
            'physical computing': ['Arduino', 'Raspberry Pi', 'IoT', 'Hardware Programming', 'Sensors'],
            'machine learning': ['Machine Learning', 'Python', 'TensorFlow', 'Statistics', 'Data Science'],
            'deep learning': ['Deep Learning', 'Neural Networks', 'TensorFlow', 'PyTorch', 'Python'],
            'computer vision': ['Computer Vision', 'OpenCV', 'Image Processing', 'Python', 'Deep Learning'],
            'natural language': ['NLP', 'Text Processing', 'NLTK', 'Python', 'Linguistics'],
            'game development': ['Game Design', 'Unity', 'Unreal Engine', 'C#', '3D Graphics'],
            'web development': ['HTML', 'CSS', 'JavaScript', 'React', 'Full-Stack'],
            'mobile development': ['React Native', 'iOS', 'Android', 'Mobile UI', 'Swift'],
            'cloud computing': ['AWS', 'Azure', 'Cloud Architecture', 'Docker', 'Kubernetes'],
            
            # General topics
            'programming': ['Python', 'JavaScript', 'Java', 'C++', 'Git'],
            'data science': ['Data Analysis', 'SQL', 'Statistics', 'Data Visualization', 'Python'],
            'data analysis': ['SQL', 'Python', 'Statistics', 'Data Visualization', 'Excel'],
            'data': ['Data Analysis', 'SQL', 'Statistics', 'Python', 'Excel'],
            'web': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js'],
            'design': ['UI/UX Design', 'Figma', 'Adobe XD', 'Prototyping', 'User Research'],
            'security': ['Cybersecurity', 'Network Security', 'Cryptography', 'Penetration Testing'],
            'cyber': ['Network Security', 'Ethical Hacking', 'Security Analysis', 'Linux'],
            'business': ['Business Strategy', 'Analytics', 'Project Management', 'Leadership'],
            'backend': ['Node.js', 'Python', 'Databases', 'API Development', 'Server Management'],
            'frontend': ['HTML', 'CSS', 'JavaScript', 'React', 'Vue.js'],
            'algorithms': ['Algorithms', 'Data Structures', 'Problem Solving', 'Complexity Analysis'],
            'database': ['SQL', 'NoSQL', 'Database Design', 'MongoDB', 'PostgreSQL'],
            'devops': ['Docker', 'CI/CD', 'AWS', 'Linux', 'Git'],
            'ai': ['Artificial Intelligence', 'Machine Learning', 'Neural Networks', 'Python'],
            'artificial intelligence': ['AI', 'Machine Learning', 'Neural Networks', 'Python', 'Deep Learning'],
            'mobile': ['React Native', 'iOS', 'Android', 'Mobile UI', 'Swift'],
            '3d': ['3D Modeling', 'WebGL', 'Three.js', 'Graphics Programming'],
            'graphics': ['Computer Graphics', '3D Modeling', 'Rendering', 'OpenGL', 'Shaders'],
            'project': ['Project Management', 'Agile', 'Scrum', 'Team Collaboration'],
            'networking': ['Network Protocols', 'TCP/IP', 'Routing', 'Network Security'],
            'mathematics': ['Mathematics', 'Linear Algebra', 'Calculus', 'Statistics'],
            'statistics': ['Statistics', 'Probability', 'Data Analysis', 'R', 'Python'],
            'marketing': ['Digital Marketing', 'SEO', 'Analytics', 'Social Media', 'Content Strategy'],
            'entrepreneurship': ['Business Development', 'Startup Strategy', 'Innovation', 'Pitching'],
            'robotics': ['Robotics', 'Automation', 'Control Systems', 'ROS', 'Arduino'],
            'iot': ['IoT', 'Embedded Systems', 'Sensors', 'MQTT', 'Arduino'],
            'blockchain': ['Blockchain', 'Smart Contracts', 'Ethereum', 'Solidity', 'Cryptocurrency']
        }
    
    def load_all_datasets(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all datasets and return combined courses, lecturers, programs"""
        try:
            # Load raw datasets
            print("Loading datasets...")
            self.bachelors_df = pd.read_csv('data/processed/harbour_space_bachelors.csv', on_bad_lines='skip')
            print(f"Loaded {len(self.bachelors_df)} bachelor courses")
            
            self.masters_df = pd.read_csv('data/processed/habour_space_masters.csv', on_bad_lines='skip')
            print(f"Loaded {len(self.masters_df)} master courses")
            
            self.lecturers_df = pd.read_csv('data/processed/harbour_space_lecturers.csv')
            print(f"Loaded {len(self.lecturers_df)} lecturers")
            
            self.programs_df = pd.read_csv('data/processed/harbour_space_programs.csv')
            print(f"Loaded {len(self.programs_df)} programs")
            
            # Load prerequisites parquet if exists
            try:
                self.prerequisites_df = pd.read_parquet('data/prerequisites/prerequisites.parquet')
                print(f"Loaded {len(self.prerequisites_df)} prerequisites")
            except:
                self.prerequisites_df = None
                print("No prerequisites file found")
            
            # Process and combine courses
            self.courses_df = self._process_courses()
            print(f"Processed total {len(self.courses_df)} courses")
            
            # Process lecturers - DO NOT FILTER
            lecturers_processed = self._process_lecturers()
            print(f"Processed {len(lecturers_processed)} lecturers")
            
            return self.courses_df, lecturers_processed, self.programs_df
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            return self._create_fallback_data()
    
    def _process_courses(self) -> pd.DataFrame:
        """Process and combine bachelor and master courses with proper IDs"""
        # Add level identifier
        self.bachelors_df['Level'] = 'Bachelor'
        self.masters_df['Level'] = 'Master'
        
        # Combine both datasets
        all_courses = pd.concat([self.bachelors_df, self.masters_df], ignore_index=True)
        
        # Generate course IDs
        all_courses['course_id'] = all_courses.apply(self._generate_course_id, axis=1)
        
        # Extract skills
        all_courses['skills_covered'] = all_courses.apply(self._extract_skills, axis=1)
        all_courses['skills_covered_str'] = all_courses['skills_covered'].apply(lambda x: ', '.join(x))
        
        # Add additional fields
        all_courses['course_name'] = all_courses['Course']
        all_courses['course_description'] = all_courses.apply(self._generate_description, axis=1)
        all_courses['category'] = all_courses['Program']
        all_courses['duration_weeks'] = 12  # Standard module duration
        all_courses['estimated_difficulty'] = all_courses.apply(self._estimate_difficulty, axis=1)
        all_courses['course_type'] = all_courses.apply(self._determine_course_type, axis=1)
        all_courses['prerequisites'] = all_courses.apply(self._determine_prerequisites, axis=1)
        
        # Add class times (distribute across morning, afternoon, evening)
        times = ['09:00-12:00', '13:00-16:00', '17:00-20:00']
        all_courses['class_time'] = [times[i % len(times)] for i in range(len(all_courses))]
        
        # Rename Credits column
        all_courses = all_courses.rename(columns={'Credits': 'credits'})
        
        return all_courses
    
    def _generate_course_id(self, row) -> str:
        """Generate course ID based on program"""
        program = row['Program']
        code = self.program_codes.get(program, 'GE')  # GE for General
        
        # Use row index for numbering
        number = str(row.name + 101).zfill(3)
        
        return f"{code}-{number}"
    
    def _extract_skills(self, row) -> List[str]:
        """Extract relevant skills from course name - IMPROVED ACCURACY"""
        course_name = str(row['Course']).lower()
        category = str(row['Category']).lower()
        program = str(row['Program']).lower()
        
        skills = []
        
        # STRATEGY: Extract skills based on key words/phrases in the course name
        # Priority: Most specific matches first
        
        # 1. EXACT PHRASE MATCHING (highest priority)
        exact_matches = {
            'physical computing': ['Arduino', 'Raspberry Pi', 'IoT', 'Sensors', 'Hardware'],
            'machine learning': ['ML Algorithms', 'Python', 'TensorFlow', 'Statistics', 'Neural Networks'],
            'deep learning': ['Neural Networks', 'TensorFlow', 'PyTorch', 'Computer Vision', 'Python'],
            'computer vision': ['Image Processing', 'OpenCV', 'Deep Learning', 'Python', 'Pattern Recognition'],
            'natural language processing': ['NLP', 'Text Analysis', 'NLTK', 'Transformers', 'Python'],
            'game development': ['Unity', 'Game Design', 'C#', '3D Graphics', 'Game Physics'],
            'web development': ['HTML/CSS', 'JavaScript', 'React', 'Node.js', 'REST APIs'],
            'mobile development': ['React Native', 'iOS/Android', 'Mobile UI', 'Swift/Kotlin', 'App Design'],
            'cloud computing': ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Cloud Architecture'],
            'data science': ['Data Analysis', 'Statistics', 'Python', 'SQL', 'Visualization'],
            'cyber security': ['Network Security', 'Ethical Hacking', 'Cryptography', 'Penetration Testing', 'Linux'],
            'digital marketing': ['SEO', 'Social Media', 'Analytics', 'Content Strategy', 'Google Ads'],
            'entrepreneurship': ['Business Planning', 'Startup Strategy', 'Innovation', 'Pitching', 'Leadership'],
            'artificial intelligence': ['AI', 'Machine Learning', 'Neural Networks', 'Python', 'Deep Learning'],
        }
        
        # Check for exact phrase matches
        for phrase, phrase_skills in exact_matches.items():
            if phrase in course_name:
                return phrase_skills[:5]
        
        # 2. KEYWORD-BASED MATCHING (analyze individual words)
        course_words = course_name.split()
        
        # Programming-related courses
        if any(word in course_name for word in ['programming', 'coding', 'software']):
            if 'introduction' in course_name or 'fundamental' in course_name or 'basic' in course_name:
                return ['Python', 'Programming Basics', 'Variables & Loops', 'Functions', 'Debugging']
            elif 'advanced' in course_name:
                return ['Advanced Python', 'OOP', 'Design Patterns', 'Testing', 'Clean Code']
            else:
                return ['Python', 'Java', 'Programming', 'Algorithms', 'Problem Solving']
        
        # Data-related courses
        if any(word in course_name for word in ['data', 'analytics', 'statistics']):
            if 'visualization' in course_name:
                return ['Data Visualization', 'Matplotlib', 'Tableau', 'D3.js', 'Storytelling']
            elif 'mining' in course_name:
                return ['Data Mining', 'Pattern Recognition', 'Clustering', 'Association Rules', 'Python']
            else:
                return ['Data Analysis', 'SQL', 'Statistics', 'Python', 'Excel']
        
        # Web-related courses
        if any(word in course_name for word in ['web', 'html', 'css', 'javascript', 'frontend', 'backend']):
            if 'frontend' in course_name or 'front-end' in course_name:
                return ['HTML/CSS', 'JavaScript', 'React', 'Responsive Design', 'UI/UX']
            elif 'backend' in course_name or 'back-end' in course_name:
                return ['Node.js', 'Python', 'Databases', 'APIs', 'Server Management']
            else:
                return ['HTML', 'CSS', 'JavaScript', 'Web Design', 'HTTP']
        
        # Database courses
        if 'database' in course_name or 'sql' in course_name:
            return ['SQL', 'Database Design', 'Queries', 'Normalization', 'PostgreSQL']
        
        # Algorithm courses
        if 'algorithm' in course_name or 'data structure' in course_name:
            return ['Algorithms', 'Data Structures', 'Complexity Analysis', 'Problem Solving', 'Optimization']
        
        # Math courses
        if any(word in course_name for word in ['mathematics', 'calculus', 'algebra', 'discrete']):
            return ['Mathematics', 'Calculus', 'Linear Algebra', 'Logic', 'Proofs']
        
        # Design courses
        if any(word in course_name for word in ['design', 'ux', 'ui', 'interaction']):
            if 'interaction' in course_name:
                return ['UX Design', 'Prototyping', 'User Research', 'Figma', 'Usability Testing']
            else:
                return ['Design Principles', 'Figma', 'Adobe XD', 'Color Theory', 'Typography']
        
        # Project courses
        if 'project' in course_name:
            return ['Project Management', 'Agile', 'Teamwork', 'Git', 'Documentation']
        
        # Security courses
        if 'security' in course_name or 'cyber' in course_name:
            return ['Network Security', 'Cryptography', 'Ethical Hacking', 'Linux', 'Security Protocols']
        
        # Network courses
        if 'network' in course_name:
            return ['Network Protocols', 'TCP/IP', 'Routing', 'Switching', 'Network Design']
        
        # Mobile courses
        if 'mobile' in course_name or 'ios' in course_name or 'android' in course_name:
            return ['Mobile Development', 'Swift/Kotlin', 'Mobile UI', 'APIs', 'App Publishing']
        
        # AI/ML courses (that didn't match exact phrases)
        if 'ai' in course_words or 'ml' in course_words:
            return ['Artificial Intelligence', 'Machine Learning', 'Python', 'Algorithms', 'Data']
        
        # Business courses
        if 'business' in course_name or 'management' in course_name:
            return ['Business Strategy', 'Management', 'Analytics', 'Leadership', 'Communication']
        
        # Marketing courses
        if 'marketing' in course_name:
            return ['Digital Marketing', 'SEO', 'Social Media', 'Analytics', 'Content Creation']
        
        # 3. FALLBACK TO PROGRAM (if no specific match)
        if 'computer science' in program:
            return ['Programming', 'Algorithms', 'Problem Solving', 'Software Development', 'Logic']
        elif 'data science' in program or 'data' in program:
            return ['Data Analysis', 'Statistics', 'Python', 'Visualization', 'SQL']
        elif 'cyber security' in program or 'security' in program:
            return ['Network Security', 'Cryptography', 'Linux', 'Security Analysis', 'Ethical Hacking']
        elif 'front-end' in program or 'interaction design' in program or 'design' in program:
            return ['HTML/CSS', 'JavaScript', 'UI/UX', 'Design', 'Prototyping']
        elif 'marketing' in program:
            return ['Digital Marketing', 'SEO', 'Analytics', 'Social Media', 'Strategy']
        elif 'business' in program or 'entrepreneur' in program:
            return ['Business Strategy', 'Management', 'Innovation', 'Leadership', 'Analytics']
        
        # 4. ULTIMATE FALLBACK (generic skills)
        return ['Critical Thinking', 'Problem Solving', 'Communication', 'Analysis', 'Collaboration']
    
    def _generate_description(self, row) -> str:
        """Generate course description from available data"""
        course = row['Course']
        category = row['Category']
        program = row['Program']
        year = row['Year']
        
        # Use the category as part of the description for better context
        descriptions = {
            'programming': f"Master {course} through hands-on coding exercises. Part of {category} curriculum focusing on practical programming skills and software development.",
            'data': f"Explore {course} with real-world datasets and analytical tools. {category} module covering data manipulation, visualization, and statistical analysis.",
            'design': f"Learn {course} through interactive projects. {category} course developing creative problem-solving and user-centered design thinking.",
            'machine learning': f"Study {course} with practical implementations. {category} covering ML algorithms, neural networks, and modern AI techniques.",
            'web': f"Build {course} skills through modern development practices. {category} focusing on responsive design, frameworks, and full-stack development.",
            'security': f"Understand {course} principles and practices. {category} covering threat analysis, secure coding, and system protection strategies.",
            'business': f"Develop {course} competencies through case studies. {category} applying business theory to real-world scenarios and strategic decision-making.",
            'project': f"Apply your skills in {course}. {category} providing hands-on experience with client work and professional project delivery.",
            'mathematical': f"Study {course} with theoretical and applied approaches. {category} building mathematical foundations essential for computer science.",
            'algorithms': f"Learn {course} through problem-solving. {category} covering computational thinking, complexity analysis, and efficient solutions.",
            'leadership': f"Develop {course} through practical exercises. {category} focusing on team management, communication, and professional development."
        }
        
        # Find matching description
        course_lower = course.lower()
        category_lower = category.lower()
        
        for key, desc in descriptions.items():
            if key in course_lower or key in category_lower:
                return desc
        
        # Default description using actual category from CSV
        return f"{course} is part of the {category} curriculum in {year}. This course provides comprehensive coverage of key concepts and practical applications in {program}."
    
    def _estimate_difficulty(self, row) -> str:
        """Estimate difficulty based on year and course name"""
        year = str(row['Year']).lower()
        course = str(row['Course']).lower()
        
        if 'first' in year or 'introduction' in course or 'basics' in course:
            return 'Beginner'
        elif 'third' in year or 'fourth' in year or 'advanced' in course or 'senior' in course:
            return 'Advanced'
        else:
            return 'Intermediate'
    
    def _determine_course_type(self, row) -> str:
        """Determine if course is mandatory, secondary, or audit"""
        course = str(row['Course']).lower()
        category = str(row['Category']).lower()
        
        # Project courses are typically mandatory
        if 'project' in course or 'project' in category:
            return 'mandatory'
        
        # Introduction and fundamental courses are mandatory
        if 'introduction' in category or 'foundation' in course:
            return 'mandatory'
        
        # Advanced and specialized courses are secondary
        if 'advanced' in course or 'emerging' in category or 'applied' in category:
            return 'secondary'
        
        # Default to secondary
        return 'secondary'
    
    def _determine_prerequisites(self, row) -> List[str]:
        """Determine prerequisites based on course level"""
        course = str(row['Course']).lower()
        
        if 'ii' in course or '2' in course:
            base = course.replace('ii', 'i').replace('2', '1')
            return [base.title()]
        elif 'iii' in course or '3' in course:
            return ['Programming I', 'Programming II']
        elif 'advanced' in course:
            return ['Introduction to ' + course.replace('advanced', '').strip()]
        
        return []
    
    def _process_lecturers(self) -> pd.DataFrame:
        """Process lecturers data - return ALL lecturers"""
        lecturers = self.lecturers_df.copy()
        
        # Add lecturer_id
        lecturers['lecturer_id'] = [f"L{str(i+1).zfill(4)}" for i in range(len(lecturers))]
        
        # Clean and format - using 'name' for compatibility with AI advisor
        lecturers['name'] = lecturers['Name']
        lecturers['lecturer_name'] = lecturers['Name']  # Keep both for compatibility
        lecturers['job_title'] = lecturers['Title']
        lecturers['company'] = lecturers['Title'].apply(lambda x: x.split('@')[-1].strip() if '@' in str(x) else 'Harbour.Space')
        lecturers['profile_url'] = lecturers['Profile_URL']
        lecturers['program'] = lecturers['Program']
        
        # Add expertise_areas and background from program and title
        lecturers['expertise_areas'] = lecturers['Program'].apply(
            lambda x: f"{x}, Technology Education, Industry Practice" if pd.notna(x) else 'Education'
        )
        lecturers['background'] = lecturers.apply(
            lambda row: f"Expert in {row['Program']} with industry experience at {row['company']}" if pd.notna(row['Program']) else "Experienced educator",
            axis=1
        )
        
        # Generate email addresses
        lecturers['email'] = lecturers['Name'].apply(
            lambda x: f"{x.lower().replace(' ', '.')}@harbour.space" if pd.notna(x) else ''
        )
        
        # Return ALL lecturers without any filtering
        print(f"Returning all {len(lecturers)} lecturers")
        return lecturers
    
    def _create_fallback_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Create minimal fallback data if loading fails"""
        courses = pd.DataFrame({
            'course_id': ['CS-101', 'DS-101'],
            'course_name': ['Introduction to Programming', 'Data Science Fundamentals'],
            'category': ['Computer Science', 'Data Science'],
            'credits': [4, 4],
            'Level': ['Bachelor', 'Bachelor'],
            'course_description': ['Learn programming basics', 'Learn data science basics'],
            'skills_covered': [['Python', 'Programming'], ['Python', 'Data Analysis']],
            'skills_covered_str': ['Python, Programming', 'Python, Data Analysis'],
            'duration_weeks': [12, 12],
            'estimated_difficulty': ['Beginner', 'Beginner'],
            'course_type': ['mandatory', 'mandatory'],
            'prerequisites': [[], []],
            'class_time': ['09:00-12:00', '13:00-16:00']
        })
        
        lecturers = pd.DataFrame({
            'lecturer_id': ['L0001'],
            'name': ['Dr. John Smith'],
            'lecturer_name': ['Dr. John Smith'],
            'job_title': ['Professor of Computer Science'],
            'company': ['Harbour.Space'],
            'program': ['Computer Science'],
            'expertise_areas': ['Computer Science, Programming, Education'],
            'background': ['Expert in Computer Science with industry experience'],
            'email': ['dr.john.smith@harbour.space'],
            'profile_url': ['https://harbour.space/faculty/john-smith']
        })
        
        programs = pd.DataFrame({
            'Program': ['Computer Science'],
            'Level': ['Bachelor'],
            'Field': ['Technology'],
            'Campus': ['Barcelona'],
            'Description': ['Computer Science program']
        })
        
        return courses, lecturers, programs

# Global instance
data_loader = DataLoader()
