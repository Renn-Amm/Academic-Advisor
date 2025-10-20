@echo off
echo Starting Harbour Space AI Advisor Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Seed database if needed
if not exist "harbour_space_advisor.db" (
    echo Database not found. Running seed script...
    python seed_data.py
)

REM Run the server
echo.
echo Starting FastAPI server...
echo API Documentation: http://localhost:8000/api/docs
echo.
python main.py
