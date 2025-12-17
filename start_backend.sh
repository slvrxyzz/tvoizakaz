#!/bin/bash

echo "Starting TeenFreelance Backend..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env file from .env.example"
    echo ""
fi

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -e .
fi

# Start the backend server
echo "Starting backend server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""
python main.py










