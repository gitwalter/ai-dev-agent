#!/bin/bash
# AI-Dev-Agent Development Environment Stop Script

echo "🛑 Stopping AI-Dev-Agent Development Environment"
echo "================================================"

# Stop and remove containers
echo "🔧 Stopping containers..."
docker-compose -f docker-compose.dev.yml down

# Optional: Remove volumes (uncomment if you want to clean data)
# echo "🧹 Removing volumes..."
# docker-compose -f docker-compose.dev.yml down -v

echo "✅ Development environment stopped successfully!"
echo ""
echo "💡 To remove all data (volumes), run:"
echo "   docker-compose -f docker-compose.dev.yml down -v"
echo ""
echo "🚀 To start again, run: ./scripts/dev-start.sh"
