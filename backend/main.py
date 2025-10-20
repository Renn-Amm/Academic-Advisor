from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base
from backend.routers import auth, courses, recommendations, chat, feedback, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    yield
    print("🛑 Application shutting down")


# Initialize FastAPI app
app = FastAPI(
    title="Harbour Space AI Academic Advisor API",
    description="REST API for AI-powered academic advising system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Harbour Space AI Academic Advisor API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-advisor-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
