#!/bin/bash

# NotebookLM Automation Docker Startup Script
# This script starts the Selenium Chrome container and Flask API

set -e

echo "🚀 Starting NotebookLM Automation Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start the services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Checking service status..."

# Check Selenium
if curl -f http://localhost:4444/wd/hub/status > /dev/null 2>&1; then
    echo "✅ Selenium Chrome is ready at http://localhost:4444"
else
    echo "❌ Selenium Chrome is not responding"
fi

# Check Flask API
if curl -f http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "✅ Flask API is ready at http://localhost:5000"
else
    echo "❌ Flask API is not responding"
fi

echo ""
echo "🎉 Services are starting up!"
echo ""
echo "📋 Service URLs:"
echo "   • Flask API: http://localhost:5000"
echo "   • API Status: http://localhost:5000/api/status"
echo "   • Selenium Hub: http://localhost:4444"
echo "   • VNC Viewer: http://localhost:7900 (password: secret)"
echo ""
echo "📖 Usage:"
echo "   1. Open http://localhost:5000 in your browser"
echo "   2. Use the web interface to test the API endpoints"
echo "   3. Or make direct API calls to http://localhost:5000/api/"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "📊 To view logs: docker-compose logs -f"
echo "🔍 To check status: docker-compose ps"

