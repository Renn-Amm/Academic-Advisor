# Harbour Space AI Academic Advisor - Backend API

A production-ready FastAPI backend for the AI Academic Advisor system.

## Features

- 🔐 **JWT Authentication** - Secure user authentication with JWT tokens
- 📚 **Course Management** - Full CRUD operations for courses
- 🤖 **AI Recommendations** - Personalized course recommendations based on user profile
- 💬 **Chat Interface** - Natural language queries for course discovery
- 📊 **Feedback System** - Course ratings and reviews
- 📅 **Schedule Generation** - Automated modular schedule creation
- 🔍 **Advanced Search** - Filter and search courses by category, type, etc.

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite/PostgreSQL** - Database (SQLite for dev, PostgreSQL for production)
- **JWT** - Secure authentication
- **Pydantic** - Data validation
- **Scikit-learn** - ML-based recommendations

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables (optional):**
   ```bash
   # Create .env file in backend directory
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./harbour_space_advisor.db
   ```

3. **Seed the database:**
   ```bash
   python seed_data.py
   ```

4. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/token` - OAuth2 compatible token endpoint

### Users

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `GET /api/users/me/enrollments` - Get user enrollments
- `GET /api/users/me/stats` - Get user statistics

### Courses

- `GET /api/courses/` - List all courses (with filters)
- `GET /api/courses/{course_id}` - Get specific course
- `POST /api/courses/enroll` - Enroll in a course
- `DELETE /api/courses/enroll/{enrollment_id}` - Drop a course
- `GET /api/courses/category/{category}` - Get courses by category

### Recommendations

- `POST /api/recommendations/` - Get personalized recommendations
- `GET /api/recommendations/schedule` - Generate personalized schedule
- `GET /api/recommendations/major/{major}` - Get recommendations for a major

### Chat

- `POST /api/chat/` - Send chat message and get AI response
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

### Feedback

- `POST /api/feedback/` - Submit course feedback
- `GET /api/feedback/my-feedback` - Get user's feedback
- `GET /api/feedback/course/{course_id}` - Get feedback for a course

## Test User

A test user is created during database seeding:

- **Email:** test@harbour.space
- **Password:** password123

## Example Usage

### Register a new user

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@harbour.space",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "major": "Computer Science",
    "career_goal": "Software Engineer"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@harbour.space",
    "password": "securepassword"
  }'
```

### Get recommendations (requires authentication)

```bash
curl -X POST "http://localhost:8000/api/recommendations/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "limit": 6
  }'
```

## Database Schema

### Users
- Student ID, email, password (hashed)
- Major, program, career goal
- GPA, completed credits
- Experience level

### Courses
- Course ID, name, description
- Category, type (mandatory/secondary/audit)
- Credits, duration, professor
- Skills covered, difficulty
- Prerequisites, max students

### Enrollments
- User-Course relationship
- Status (enrolled/completed/dropped)
- Grade, enrollment/completion dates

### Feedback
- Course ratings (1-5)
- Difficulty assessment
- Comments and recommendations
- Skills gained

### Chat Messages
- User queries and AI responses
- Query type classification
- Timestamp

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth.py                # Authentication utilities
├── seed_data.py           # Database seeding script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── routers/              # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── users.py          # User management
│   ├── courses.py        # Course management
│   ├── recommendations.py # Recommendation engine
│   ├── chat.py           # Chat interface
│   └── feedback.py       # Feedback system
└── services/             # Business logic
    └── recommendation_service.py  # Recommendation algorithms
```

## Production Deployment

### Environment Variables

Set these environment variables for production:

```bash
SECRET_KEY=your-secure-secret-key-minimum-32-characters
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_ORIGINS=https://yourdomain.com
```

### Database Migration

For production, use Alembic for database migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### CORS Configuration

Update the CORS settings in `main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Tips

- Use PostgreSQL for production (better performance than SQLite)
- Enable connection pooling
- Add Redis for caching
- Use Gunicorn with Uvicorn workers for production
- Set up proper logging and monitoring
- Implement rate limiting

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

Copyright © 2024 Harbour Space University

## Support

For issues and questions, please contact the development team.
