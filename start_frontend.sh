#!/bin/bash

echo "Starting TeenFreelance Frontend..."
echo ""

# Navigate to frontend directory
cd fronted || exit 1

# Check if .env.local file exists
if [ ! -f .env.local ]; then
    echo "WARNING: .env.local file not found!"
    echo "Creating .env.local from example..."
    if [ -f .env.example ]; then
        cp .env.example .env.local
    else
        echo "Creating default .env.local..."
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_MODE=dev
EOF
    fi
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the frontend server
echo "Starting frontend server on http://localhost:3000"
echo ""
npm run dev










