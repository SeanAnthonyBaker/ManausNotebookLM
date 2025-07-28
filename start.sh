#!/bin/bash

# NotebookLM Automation Docker Startup Script
# This script starts the Selenium Chrome container and Flask API

set -e

echo "🚀 Starting NotebookLM Automation Services..."

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
echo "⏳ Waiting for services to become healthy..."

for i in {1..30}; do
    # Check if selenium is healthy
    if [ "$(docker-compose ps -q selenium | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null)" = "healthy" ]; then
        echo "✅ Selenium Chrome is ready at http://localhost:4444"
        # Now check if the app is healthy
        if [ "$(docker-compose ps -q app | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null)" = "healthy" ]; then
            echo "✅ Flask API is ready at http://localhost:5000"
            break
        fi
    fi
    echo -n "."
    sleep 2
done

if [ "$i" -eq 30 ]; then
    echo ""
    echo "❌ One or more services failed to become healthy in time."
    echo "📊 Final service status:"
    docker-compose ps
    echo "🪵 To see detailed logs, run: docker-compose logs -f"
    exit 1
fi

echo ""
echo "🎉 Services are starting up!"
echo ""
echo "📋 Service URLs:"
echo "   • Flask API: http://localhost:5000"
echo "   • API Status: http://localhost:5000/api/get_status"
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
