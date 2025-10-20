import pandas as pd
import numpy as np
from faker import Faker
import random
from typing import List, Dict

class DataGenerator:
    def __init__(self):
        self.faker = Faker()
    
    def generate_faculty_data(self, num_faculty: int = 20) -> pd.DataFrame:
        """Generate sample faculty data"""
        faculty = []
        
        departments = ['Data Science', 'Computer Science', 'Cybersecurity', 'Business', 'Design', 'Web Development', 'Marketing']
        expertise_areas = {
            'Data Science': ['Machine Learning', 'Data Mining', 'Statistics', 'Big Data', 'AI'],
            'Computer Science': ['Algorithms', 'Software Engineering', 'Systems', 'Theory', 'Security'],
            'Cybersecurity': ['Network Security', 'Cryptography', 'Digital Forensics', 'Ethical Hacking'],
            'Business': ['Entrepreneurship', 'Finance', 'Marketing', 'Strategy', 'Management'],
            'Design': ['UX Research', 'UI Design', 'Product Design', 'User Testing', 'Interaction'],
            'Web Development': ['Frontend', 'Backend', 'Full Stack', 'React', 'Node.js'],
            'Marketing': ['Digital Marketing', 'Social Media', 'Content Strategy', 'SEO']
        }
        
        for i in range(num_faculty):
            department = random.choice(departments)
            expertise = random.sample(expertise_areas.get(department, ['Technology', 'Innovation']), 2)
            
            faculty_member = {
                'faculty_id': f"PROF{i+1:03d}",
                'name': self.faker.name(),
                'email': self.faker.email(),
                'department': department,
                'position': random.choice(['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']),
                'expertise': ', '.join(expertise),
                'years_experience': random.randint(5, 30)
            }
            faculty.append(faculty_member)
        
        return pd.DataFrame(faculty)