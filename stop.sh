#!/bin/bash

# NotebookLM Automation Docker Stop Script

set -e

echo "🛑 Stopping NotebookLM Automation Services..."

# Stop and remove containers
docker-compose down --remove-orphans

# Optional: Remove volumes (uncomment if you want to clean up completely)
# docker-compose down --volumes

echo "✅ All services stopped successfully!"
echo ""
echo "🔍 To check if containers are stopped: docker-compose ps"
echo "🚀 To start again: ./start.sh"

