# Harbour Space AI Academic Advisor

An intelligent academic advising system powered by AI, helping students make informed decisions about their course selections, schedules, and academic paths.

## Latest Updates

### Version 3.8.0 - October 20, 2025

#### Hub-Style UI Redesign
- Professional black background with clean, minimal design
- Removed gradient overuse for simple solid color scheme
- Blue accent color (#2563eb) for consistency across interface
- Dark theme optimized for extended use and reduced eye strain
- Removed all emojis for professional, enterprise-grade appearance
- Streamlined navigation with 7 essential tabs
- Real-Time Hub functionality integrated into Schedule Calendar

### Version 3.5.0 - October 20, 2025

#### Collision Detection and Time Conflict Warnings
- Real-time conflict detection prevents time slot collisions
- Visual error messages when attempting to enroll in conflicting courses
- Comprehensive validation checks all enrolled courses before new enrollment
- Intelligent suggestions recommend courses in different time slots
- Fail-safe protection prevents enrollment in courses with same time slot

#### Schedule Calendar View
- Weekly calendar provides visual timeline of enrolled courses
- Grid view displays traditional calendar format showing daily schedule
- Timeline view shows module-based projection for upcoming courses
- Color-coded time slots differentiate Morning, Afternoon, and Evening sessions
- Interactive Gantt-style visualizations powered by Plotly

#### Real-Time Hub
- Live clock displays current time and date
- Active class tracker identifies currently active sessions
- Time remaining countdown for active class sessions
- Complete daily timetable view
- Context-aware greetings based on time of day
- Quick statistics for enrolled and completed courses

#### Enhanced LLM Conversation System
- Knowledge base integration with comprehensive tech topics
- Natural conversation handling for greetings and general queries
- Technical explanations for Computer Science, AI, Machine Learning, Cybersecurity, Web Development
- Detailed career guidance and path information
- Complete university policies and program information
- Extended conversation history supports 20 messages (10 exchanges)
- Increased response capacity to 1200 tokens for detailed answers
- Silent fallback mode when OpenAI configuration unavailable

#### Redesigned Performance Insights
- Color-coded GPA display with visual indicators
- Learning velocity tracking measures courses completed per module
- Skill gap analysis provides targeted recommendations
- Graduation forecast estimates remaining modules and weeks
- Workload monitor assesses current course load in real-time
- Personalized performance recommendations based on GPA trends
- Unique metrics eliminate duplication with overview statistics

### System Enhancements
- Collision detection fully operational and prevents time slot conflicts
- Complete 3-year bachelor program support with all years displayed correctly
- AI interprets single-word queries including "software", "ml", and "business"
- Enrollment system prevents scheduling conflicts through automatic validation
- Class times displayed for all enrolled courses
- Form validation ensures complete information before submission
- Streamlined user interface with compact chat layout
- Standardized course duration display shows "3 weeks" consistently
- Integration of 50+ lecturers with expertise mapping to relevant courses
- Prerequisite analysis identifies required skills before course enrollment
- Intelligent course combination suggestions for optimal audit pairings
- Comprehensive time slot assignment across Morning, Afternoon, and Evening sessions
- Flexible course type selection allows students to choose Mandatory, Secondary, or Audit
- Program-specific recommendations tailored for Bachelor's and Master's programs
- Three schedule visualization options for enhanced planning
- Real-time tracking with live clock and active class monitoring
- Performance analytics provide unique insights without statistical duplication

## Features

### Frontend (Streamlit)
- User Authentication - Secure login and registration system
- Course Catalog - Browse all courses without type labels (student decides how to take them)
- AI-Powered Recommendations - Personalized suggestions with lecturer information
- Interactive Chat - Ask about lecturers, prerequisites, course combinations, and timings
- Smart Path Planner
- Auto-generated personalized academic timeline based on major
- Varied course types (40% mandatory, 40% secondary, 20% audit)
- Changeable course types - convert mandatory to audit or vice versa
- Course prerequisites and sequencing
- Workload optimization
- Module-based planning (3-4 weeks per module)
- Shows 3 active modules, rest marked as "Coming Soon"
- Fixed card display - proper spacing, no overflow
- Buttons remain accessible after enrollment plan with time slots, remaining shown as "Coming Soon"
- Progress Tracking - Monitor GPA, credits, and course completion
- Course Feedback - Rate and review completed courses

### AI Assistant Features

- LLM-Powered Responses: Uses OpenAI GPT for dynamic, human-like conversations
- Self-Generated Answers: AI creates unique responses without pre-written templates
- Context-Aware Processing: Maintains conversation history for improved follow-up responses
- Timetable Conflict Detection: Automatically identifies and warns about scheduling conflicts
- Conversational AI: Generates natural responses and communicates limitations transparently
- Natural Language Understanding: Processes diverse student queries including:
  - Single-word and short queries: "ML", "software", "business", "data"
  - Major detection: Recognizes software development, business, design, marketing, and other fields
  - Program information: Course listings and major descriptions
  - Attendance consequences: Policy explanations and impact analysis
  - Student issues: Support for scheduling conflicts and emergency situations
  - Class preparation: Prerequisites and recommended preparation
  - Specific preparation: Tools, languages, projects, and resources by field
  - Lecturer profiles: Information on up to 8 instructors
  - Schedule queries: Morning, afternoon, and evening time slots
  - Career guidance: Path recommendations and industry insights
  - Course type explanations: Mandatory, secondary, and audit classifications
  - Attendance policy: 3+ absences result in course failure, 10-minute lateness counts as absence
  - Module planning: Academic timeline organization
  - Course recommendations: Up to 10 personalized suggestions
- Honest Communication: Explains limitations and suggests alternatives when uncertain
- Response Variation: Employs diverse phrasing to avoid repetitive answers
- Professional Tone: Maintains appropriate communication standards
- Natural Dialogue: Context-aware processing enables human-like conversation flow
- Student Support: Provides guidance through academic challenges and problems
- Comprehensive Guidance: Combines academic planning with career development advice
- Lecturer Knowledge: Access to profiles and backgrounds of 50+ industry experts
- Modern Interface: Chat UI features message bubbles and user avatars
- Prerequisites Calculator: Identifies required skills for course enrollment
- Course Pairing Advisor: Recommends optimal audit course combinations
- Scheduling Intelligence: Flexible time slot management across Morning, Afternoon, and Evening

### Enhanced AI Engine
- Multi-Intent Recognition: Processes general information, lecturer, schedule, career, and recommendation queries
- Short Query Support: Interprets abbreviations and concise queries (ML, DS, CS, etc.)
- Lecturer Expertise Matching: Automatically maps 50+ lecturers to relevant courses
- Prerequisites Calculator: Identifies required skills and preparation for each course
- Course Combination Advisor: Recommends complementary audit course pairings
- Time Slot Management: Assigns class schedules (9:00-12:20, 13:00-16:20, 17:00-20:20)
- Intelligent Scoring Algorithm: Ranks courses by major, career goals, and experience level
- Flexible Course Classification: Enables student selection of mandatory, secondary, or audit status

### Backend (FastAPI)
- JWT Authentication: Secure API authentication system
- Database Layer: SQLAlchemy ORM supporting SQLite and PostgreSQL
- RESTful API: Well-structured endpoints for comprehensive feature access
- Recommendation Engine: Machine learning-based course recommendations with lecturer integration
- Auto-generated Documentation: Swagger UI and ReDoc interfaces
- Advanced Filtering: Search capabilities by category, type, and difficulty
- Persistent Storage: User data, enrollment records, and feedback management

## Project Structure

```
AI-Advisor/
├── backend/                    # FastAPI backend
│   ├── main.py                # API entry point
│   ├── database.py           # Database configuration
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── auth.py               # Authentication utilities
│   ├── seed_data.py          # Database seeding
│   ├── requirements.txt      # Backend dependencies
│   ├── README.md            # Backend documentation
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── users.py         # User management
│   │   ├── courses.py       # Course operations
│   │   ├── recommendations.py # Recommendations
│   │   ├── chat.py          # Chat interface
│   │   └── feedback.py      # Feedback system
│   └── services/            # Business logic
│       └── recommendation_service.py
│
├── app.py                    # Streamlit frontend
├── ui_components.py          # Enhanced UI components (NEW)
├── advisor/                  # Advisor logic
│   ├── recommendation_engine.py
│   └── enhanced_ai_advisor.py  # Enhanced AI with lecturer integration (NEW)
├── scraper/                  # Web scraping
│   ├── main_scraper.py
│   ├── data_processor.py
│   └── config.py
├── data/                     # Data storage
│   ├── processed/           # Processed datasets
│   │   ├── harbour_space_courses.csv
│   │   ├── harbour_space_programs.csv
│   │   └── lecturers.csv    # 50+ lecturers with expertise (NEW)
│   ├── raw/                 # Raw scraped data
│   └── prerequisites/       # Course prerequisites
├── util/                     # Utilities
│   └── data_generator.py
├── config.yaml              # Configuration
├── requirement.txt          # All dependencies
├── README.md               # This file
└── IMPROVEMENTS.md         # Detailed improvements documentation (NEW)
```

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AI-Advisor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

### Running the Backend API

3. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

4. **Seed the database:**
   ```bash
   python seed_data.py
   ```

5. **Start the API server:**
   ```bash
   python main.py
   ```
   
   Or use the convenience script:
   - **Windows:** `run.bat`
   - **Linux/Mac:** `./run.sh`

   The API will be available at:
   - **API:** http://localhost:8000
   - **Swagger Docs:** http://localhost:8000/api/docs
   - **ReDoc:** http://localhost:8000/api/redoc

### Running the Frontend (Streamlit)

6. **In a new terminal, from the project root:**
   ```bash
   streamlit run app.py
   ```

   The Streamlit app will open at http://localhost:8501

## Test Credentials

A test user is created during database seeding:

- **Email:** test@harbour.space
- **Password:** password123

## API Documentation

### Authentication Endpoints

```
POST /api/auth/register    - Register new user
POST /api/auth/login       - Login and get JWT token
POST /api/auth/token       - OAuth2 compatible token
```

### User Endpoints

```
GET  /api/users/me              - Get current user profile
PUT  /api/users/me              - Update user profile
GET  /api/users/me/enrollments  - Get user enrollments
GET  /api/users/me/stats        - Get user statistics
```

### Course Endpoints

```
GET    /api/courses/                    - List all courses
GET    /api/courses/{course_id}         - Get specific course
POST   /api/courses/enroll              - Enroll in course
DELETE /api/courses/enroll/{id}         - Drop course
GET    /api/courses/category/{category} - Get courses by category
```

### Recommendation Endpoints

```
POST /api/recommendations/           - Get personalized recommendations
GET  /api/recommendations/schedule   - Generate personalized schedule
GET  /api/recommendations/major/{major} - Get major-specific recommendations
```

### Chat Endpoints

```
POST   /api/chat/         - Send chat message
GET    /api/chat/history  - Get chat history
DELETE /api/chat/history  - Clear chat history
```

### Feedback Endpoints

```
POST /api/feedback/                 - Submit course feedback
GET  /api/feedback/my-feedback      - Get user's feedback
GET  /api/feedback/course/{course_id} - Get course feedback
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite/PostgreSQL** - Database
- **JWT** - Authentication tokens
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Streamlit** - Interactive web apps
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation

### Machine Learning
- **Scikit-learn** - ML algorithms
- **TF-IDF** - Text vectorization
- **Cosine Similarity** - Course matching

### Data Collection
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP client

## Database Schema

### Core Tables

- **users** - Student profiles and authentication
- **courses** - Course catalog with metadata
- **enrollments** - Student course enrollments
- **chat_messages** - Chat history
- **course_feedback** - Ratings and reviews
- **schedules** - Generated schedules

## Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./harbour_space_advisor.db
ALLOWED_ORIGINS=http://localhost:8501
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Application Configuration

Edit `config.yaml` for scraper and data processing settings.

## Development

### Running in Development Mode

**Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Frontend:**
```bash
streamlit run app.py
```

### Code Structure Guidelines

- **Models** - Database models in `backend/models.py`
- **Schemas** - Request/response schemas in `backend/schemas.py`
- **Routers** - API endpoints in `backend/routers/`
- **Services** - Business logic in `backend/services/`
- **Authentication** - JWT handling in `backend/auth.py`

## Deployment

### Backend Deployment

1. **Use PostgreSQL for production:**
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db
   ```

2. **Set secure SECRET_KEY:**
   ```env
   SECRET_KEY=<generate-strong-random-key>
   ```

3. **Configure CORS properly:**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

4. **Use Gunicorn with Uvicorn workers:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment

Create `Dockerfile` in backend:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Features in Detail

### Enhanced AI Recommendation Engine

The system uses multiple factors to recommend courses:

- **Major Alignment** - Courses matching student's major (+10 points)
- **Program Fit** - Bachelor's vs Master's program alignment (+5 points)
- **Career Goals** - Skills alignment with career objectives (+3 points per match)
- **Experience Level** - Beginner/Intermediate/Advanced matching (+4 points)
- **Query Matching** - Natural language understanding (+8 points exact, +2 partial)
- **Course Type Priority** - Mandatory +7, Secondary +4, Audit +2
- **Lecturer Expertise** - Automatically matched to courses based on background
- **Prerequisites** - AI calculates what skills you need before enrolling
- **Course Combinations** - Suggests complementary audit courses
- **Time Slots** - Assigns morning/afternoon/evening times to all courses

### Smart Scheduling

Generates 3-4 active modules (remaining shown as "Coming Soon"):

- **Module 1** (Weeks 1-3) - Foundation courses with time slots
- **Module 2** (Weeks 4-6) - Advanced concepts
- **Module 3** (Weeks 7-9) - Specialization & electives
- **Module 4+** - Shown as "Coming Soon"

Each module includes:
- Assigned time slots (9:00-12:20, 1:00-4:20, 5:00-8:20)
- Flexible course types (student can choose mandatory/secondary/audit)
- Lecturer information and expertise
- Prerequisites you need to prepare
- Recommended audit course combinations
- Credit load (typically 10-14 credits)

### Feedback Loop

Student feedback improves recommendations:

- Course ratings (1-5 stars)
- Difficulty assessment
- Skills gained validation
- Recommendation likelihood
- Detailed comments

### Lecturer Information

Every course includes:

- Lecturer name and credentials
- Job title and company
- Areas of expertise
- Educational background
- Contact email
- What other courses they teach

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

Copyright © 2024 Harbour Space University

## Authors

- Development Team - AI Academic Advisor Project

## Recent Improvements

### Version 2.0 (Current)
- Added comprehensive lecturer integration (50+ lecturers)
- Implemented time slot assignment for all courses
- Added prerequisite skill calculator
- Created course combination advisor
- Made course types flexible (student choice)
- Removed type badges from course catalog
- Fixed grid layout gaps when filtering
- Enhanced AI with lecturer-aware responses
- Limited smart planner to 3-4 modules
- Added "Coming Soon" for future modules

### Known Issues

- Streamlit frontend uses in-memory session state (not persistent)
- Backend and frontend run as separate services
- For production, consider integrating frontend with backend API

## Known Issues

- Streamlit frontend uses in-memory session state (not persistent)
- Backend and frontend run as separate services
- For production, consider integrating frontend with backend API

## Future Enhancements

- [ ] Real-time notifications
- [ ] Lecturer ratings and reviews
- [ ] Grade prediction models
- [ ] Peer recommendations
- [ ] Mobile application
- [ ] Integration with university systems
- [ ] Advanced analytics dashboard
- [ ] Group study recommendations
- [ ] Career path visualization
- [ ] Historical enrollment data analysis
- [ ] Course capacity management
- [ ] Waitlist functionality
- [ ] Multi-semester planning

## Support

For questions or issues:
- Check API documentation at `/api/docs`
- Review backend README in `backend/README.md`
- Contact development team

## Acknowledgments

- Harbour Space University
- 50+ Industry Expert Lecturers
- Course instructors and advisors
- Student feedback contributors

## Additional Documentation

- **IMPROVEMENTS.md** - Detailed documentation of all enhancements
- **backend/README.md** - Backend API documentation
- **SETUP.md** - Complete setup guide
- **API_EXAMPLES.md** - API usage examples

---

**Built for Harbour Space students with intelligent AI guidance**
