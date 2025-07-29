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
    selenium_id=$(docker-compose ps -q selenium)
    if [ -n "$selenium_id" ] && [ "$(docker inspect -f '{{.State.Health.Status}}' "$selenium_id" 2>/dev/null)" = "healthy" ]; then
        # Now check if the app is healthy
        app_id=$(docker-compose ps -q app)
        if [ -n "$app_id" ] && [ "$(docker inspect -f '{{.State.Health.Status}}' "$app_id" 2>/dev/null)" = "healthy" ]; then
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

echo "" # Newline for cleaner output
echo "✅ All services are healthy and running!"
echo "📋 Service URLs:"
echo "   • Flask API: http://localhost:5000"
echo "   • API Status: http://localhost:5000/api/status"
echo "   • Selenium Hub: http://localhost:4444"
echo "   • VNC Viewer: http://localhost:7900 (password: secret)"
