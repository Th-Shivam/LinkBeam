#!/bin/bash

# LinkBeam Startup Script
# This script starts both the backend server and frontend development server

echo "🔗 Starting LinkBeam..."
echo ""

# Check if running in the correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the LinkBeam root directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    exit 1
fi

# Install backend dependencies if needed
if [ ! -f "backend/.dependencies_installed" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt > /dev/null 2>&1
    touch .dependencies_installed
    cd ..
    echo "✅ Backend dependencies installed"
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install > /dev/null 2>&1
    cd ..
    echo "✅ Frontend dependencies installed"
fi

echo ""
echo "🚀 Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

echo "🚀 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ LinkBeam is running!"
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Trap Ctrl+C to clean up
trap "echo ''; echo 'Stopping LinkBeam...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for processes
wait
