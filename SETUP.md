# Setup Guide - Harbour Space AI Advisor Complete setup instructions for both backend and frontend. ## Prerequisites Before starting, ensure you have: - Python 3.8 or higher installed
- pip package manager
- Git (for cloning the repository)
- Terminal/Command Prompt access Check your Python version:
```bash
python --version
``` ## Quick Setup (5 Minutes) ### Step 1: Clone & Navigate ```bash
git clone <repository-url>
cd AI-Advisor
``` ### Step 2: Install All Dependencies ```bash
pip install -r requirement.txt
``` This installs both frontend and backend dependencies. ### Step 3: Setup Backend ```bash
cd backend
python seed_data.py
``` This creates the database and populates it with sample courses and a test user. ### Step 4: Start Backend API**Option A - Using Python directly:**
```bash
python main.py
```**Option B - Using convenience scripts:** Windows:
```bash
run.bat
``` Linux/Mac:
```bash
chmod +x run.sh
./run.sh
``` The API will start at http://localhost:8000 Verify backend: Open http://localhost:8000/api/docs ### Step 5: Start Frontend Open a**new terminal window** (keep backend running), then: ```bash
cd AI-Advisor # Navigate to project root
streamlit run app.py
``` The Streamlit app will open automatically at http://localhost:8501 ## Login to the Application Use the test account created during setup: ```
Email: test@harbour.space
Password: password123
``` Or create a new account using the "Create Account" tab. ## You're Done! You should now have:
- Backend API running on port 8000
- Frontend app running on port 8501
- Database with sample courses
- Test user account ready ## Detailed Setup ### Virtual Environment (Recommended) For a cleaner installation, use a virtual environment:**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirement.txt
```**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
``` ### Environment Variables (Optional) For production or custom configuration: 1. Copy the example file: ```bash cd backend cp .env.example .env ``` 2. Edit `.env` with your settings: ```env SECRET_KEY=your-secure-secret-key DATABASE_URL=sqlite:///./harbour_space_advisor.db ACCESS_TOKEN_EXPIRE_MINUTES=1440 ``` ### Database Configuration**SQLite (Default - Development):**
- Automatically created as `harbour_space_advisor.db`
- No additional setup required
- Located in `backend/` directory**PostgreSQL (Production):** 1. Install PostgreSQL
2. Create database: ```sql CREATE DATABASE harbour_advisor; ```
3. Update `.env`: ```env DATABASE_URL=postgresql://user:password@localhost:5432/harbour_advisor ``` ## Verifying Installation ### Test Backend 1. Open http://localhost:8000/api/docs
2. Try the `/api/health` endpoint
3. Expected response: ```json { "status": "healthy", "service": "ai-advisor-api" } ``` ### Test Authentication 1. In Swagger UI (http://localhost:8000/api/docs)
2. Expand `POST /api/auth/login`
3. Click "Try it out"
4. Enter test credentials: ```json { "email": "test@harbour.space", "password": "password123" } ```
5. Should return JWT token ### Test Frontend 1. Open http://localhost:8501
2. Login with test credentials
3. Try: - Browsing courses - Getting recommendations - Asking chat questions - Viewing your schedule ## Database Seeding The `seed_data.py` script does: 1. Creates all database tables
2. Loads courses from CSV (if available)
3. Creates 15+ sample courses
4. Creates test user account
5. Shows database statistics**Re-seed database:**
```bash
cd backend
rm harbour_space_advisor.db # Delete existing database
python seed_data.py # Re-create and seed
``` ## Troubleshooting ### Port Already in Use**Backend (Port 8000):**
```bash
# Find process using port 8000
netstat -ano | findstr :8000 # Windows
lsof -i :8000 # Mac/Linux # Kill the process or use different port
uvicorn main:app --port 8001
```**Frontend (Port 8501):**
```bash
streamlit run app.py --server.port 8502
``` ### Module Not Found Errors ```bash
# Ensure you're in the correct directory
cd AI-Advisor # Reinstall dependencies
pip install -r requirement.txt # For backend-specific issues
cd backend
pip install -r requirements.txt
``` ### Database Connection Errors 1. Check if `harbour_space_advisor.db` exists in `backend/`
2. Try re-seeding: ```bash cd backend python seed_data.py ```
3. Check file permissions
4. Ensure SQLite is properly installed ### Import Errors in Backend If you see "No module named 'backend'": ```bash
# Ensure you're running from backend directory
cd backend
python main.py # Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.." # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%\.. # Windows
``` ### Streamlit Not Loading ```bash
# Clear Streamlit cache
streamlit cache clear # Run with verbose logging
streamlit run app.py --logger.level=debug
``` ## Updating the Project ```bash
# Pull latest changes
git pull origin main # Update dependencies
pip install -r requirement.txt --upgrade # Restart backend
cd backend
python main.py # Restart frontend (in new terminal)
streamlit run app.py
``` ## Customization ### Change API Port Edit `backend/main.py`:
```python
if __name__ == "__main__": import uvicorn uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
``` ### Add More Courses 1. Edit `backend/seed_data.py`
2. Add courses to `sample_courses` list
3. Run: `python seed_data.py` ### Modify Frontend Theme Edit `app.py` CSS in the `<style>` section around line 26. ## Development vs Production ### Development
- Use SQLite database
- Debug mode enabled
- Auto-reload on changes
- Detailed error messages
- CORS allows all origins ### Production
- Use PostgreSQL
- Disable debug mode
- Static builds
- Generic error messages
- Restrict CORS origins
- Use environment variables
- Add logging and monitoring ## Next Steps 1. Explore API documentation: http://localhost:8000/api/docs
2. Browse courses in Streamlit app
3. Test course recommendations
4. Try the AI chat interface
5. Enroll in courses
6. Generate your schedule
7. Leave course feedback ## Tips - Keep both backend and frontend terminals open
- Backend must run before frontend for full functionality
- Check API docs for all available endpoints
- Use test account for quick testing
- Clear browser cache if Streamlit behaves oddly ## Additional Resources - [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Backend README: `backend/README.md`
- Main README: `README.md` ## Setup Checklist - [ ] Python 3.8+ installed
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Backend database seeded
- [ ] Backend API running on port 8000
- [ ] API docs accessible at /api/docs
- [ ] Frontend running on port 8501
- [ ] Test login successful
- [ ] Courses visible
- [ ] Recommendations working ---**Need help? Check the troubleshooting section or review the API documentation.**
