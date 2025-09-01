#!/bin/bash

# AI-Dev-Agent Container Setup Script
# ===================================
# 
# One-command setup for complete AI development environment
# Eliminates all machine dependencies and path issues
#
# Usage:
#   chmod +x scripts/container_setup.sh
#   ./scripts/container_setup.sh
#

set -e  # Exit on any error

echo "🚀 AI-Dev-Agent Container Setup"
echo "==============================="
echo ""

# Check Docker installation
echo "🔍 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if containers are already running
echo "🔍 Checking for existing containers..."
if docker ps -q --filter "name=ai-dev-agent" | grep -q .; then
    echo "⚠️  AI-Dev-Agent containers are already running"
    echo "   Would you like to restart them? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🔄 Stopping existing containers..."
        docker-compose down
    else
        echo "ℹ️  Keeping existing containers running"
        exit 0
    fi
fi

# Build and start containers
echo "🏗️  Building AI-Dev-Agent containers..."
docker-compose build --no-cache

echo "🚀 Starting AI-Dev-Agent environment..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
if docker ps --filter "name=ai-dev-agent-system" --filter "status=running" | grep -q ai-dev-agent-system; then
    echo "✅ AI-Dev-Agent core system is running"
else
    echo "❌ AI-Dev-Agent core system failed to start"
    echo "📋 Container logs:"
    docker-compose logs ai-dev-agent
    exit 1
fi

# Display connection information
echo ""
echo "🎉 AI-Dev-Agent Environment Ready!"
echo "=================================="
echo ""
echo "📊 Services Available:"
echo "   • Core System:     http://localhost:8080"
echo "   • Web Interface:   http://localhost:3000 (if enabled)"
echo "   • Database:        localhost:5432 (postgres)"
echo "   • Cache:           localhost:6379 (redis)"
echo ""
echo "🔧 Useful Commands:"
echo "   • Enter container:      docker-compose exec ai-dev-agent bash"
echo "   • View logs:           docker-compose logs -f ai-dev-agent"
echo "   • Run tests:           docker-compose exec ai-dev-agent pytest"
echo "   • Stop services:       docker-compose down"
echo ""
echo "🚀 Quick Start:"
echo "   docker-compose exec ai-dev-agent python run_demo.py"
echo ""

# Test core functionality
echo "🧪 Testing core functionality..."
if docker-compose exec -T ai-dev-agent python -c "import utils.context.ontological_framework_system; print('✅ Ontological framework system loaded successfully')"; then
    echo "✅ Core systems test passed"
else
    echo "⚠️  Core systems test failed - check configuration"
fi

echo ""
echo "🌟 Container Setup Complete!"
echo "   Your AI-Dev-Agent environment is ready for development."
echo "   No more machine dependencies or path issues!"
echo ""
