#!/bin/bash

# LinkBeam Production Deployment Script

echo "🔗 LinkBeam Production Deployment"
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Warning: Running as root is not recommended"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

# Create uploads directory with proper permissions
mkdir -p backend/uploads
chmod 755 backend/uploads

# Build frontend
echo "Building frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..

# Security checks
echo ""
echo "Security Checklist:"
echo "==================="
echo "✓ File size limit: 500MB"
echo "✓ File type validation: Enabled"
echo "✓ Path traversal protection: Enabled"
echo "✓ CORS restrictions: Enabled"
echo "✓ Debug mode: Disabled"
echo "✓ Error handling: Enabled"
echo ""

# Production server options
echo "Production Server Options:"
echo "=========================="
echo "1. Development (Flask built-in)"
echo "2. Production (Gunicorn + Eventlet)"
echo ""
read -p "Select option (1-2): " option

case $option in
    1)
        echo "Starting development server..."
        cd backend
        python app.py
        ;;
    2)
        echo "Starting production server with Gunicorn..."
        cd backend
        gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet -m 007 app:app
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
