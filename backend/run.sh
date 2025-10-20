#!/bin/bash

echo "Starting Harbour Space AI Advisor Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Seed database if needed
if [ ! -f "harbour_space_advisor.db" ]; then
    echo "Database not found. Running seed script..."
    python seed_data.py
fi

# Run the server
echo ""
echo "Starting FastAPI server..."
echo "API Documentation: http://localhost:8000/api/docs"
echo ""
python main.py
