#!/bin/bash
# AI-Dev-Agent Development Environment Quick Start

echo "🚀 Starting AI-Dev-Agent Development Environment"
echo "================================================"

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop"
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop"
    exit 1
fi

# Check Docker Compose availability
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose"
    echo "   Instructions: https://docs.docker.com/compose/install/"
    exit 1
fi

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true

# Start development environment
echo "🔧 Building and starting development containers..."
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start (this may take a minute)..."
sleep 30

# Health check with retries
echo "🏥 Performing health checks..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
        echo "✅ AI-Dev-Agent is running successfully!"
        echo ""
        echo "🌐 Access the application at: http://localhost:8501"
        echo "📊 Health status: http://localhost:8501/_stcore/health"
        echo "📝 Streamlit UI: http://localhost:8501"
        echo ""
        echo "🎯 Development Environment Ready!"
        echo "================================="
        echo "🔧 Hot reload enabled - code changes auto-refresh"
        echo "📂 Logs available in ./logs directory"
        echo "🔍 View logs: docker-compose -f docker-compose.dev.yml logs -f"
        echo "🛑 Stop with: ./scripts/dev-stop.sh"
        echo ""
        echo "Happy coding! 🎉"
        exit 0
    fi
    
    retry_count=$((retry_count + 1))
    echo "⏳ Waiting for service to be ready... ($retry_count/$max_retries)"
    sleep 10
done

echo "❌ Health check failed after $max_retries attempts"
echo "📋 Container logs:"
docker-compose -f docker-compose.dev.yml logs ai-dev-agent
echo ""
echo "🔧 Troubleshooting:"
echo "   1. Check if port 8501 is available"
echo "   2. Ensure Docker has enough resources (4GB+ RAM recommended)"
echo "   3. Check container status: docker-compose -f docker-compose.dev.yml ps"
exit 1
