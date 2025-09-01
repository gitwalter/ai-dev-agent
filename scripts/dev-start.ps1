# AI-Dev-Agent Development Environment Quick Start for Windows
# PowerShell Script

Write-Host "🚀 Starting AI-Dev-Agent on Windows" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check Docker Desktop
Write-Host "🔍 Checking Docker availability..." -ForegroundColor Yellow
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Desktop not found" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop for Windows" -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose not found" -ForegroundColor Red
    Write-Host "   Please ensure Docker Compose is installed" -ForegroundColor Red
    exit 1
}

# Stop existing containers
Write-Host "🧹 Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>$null

# Start development environment
Write-Host "🔧 Building and starting containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Health check with retries
Write-Host "🏥 Performing health checks..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8501/_stcore/health" -Method Get -TimeoutSec 5
        Write-Host "✅ AI-Dev-Agent is running successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Access the application at: http://localhost:8501" -ForegroundColor Cyan
        Write-Host "📊 Health status: http://localhost:8501/_stcore/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🎯 Development Environment Ready!" -ForegroundColor Green
        Write-Host "=================================" -ForegroundColor Green
        Write-Host "🔧 Hot reload enabled - code changes auto-refresh" -ForegroundColor Yellow
        Write-Host "📂 Logs available in ./logs directory" -ForegroundColor Yellow
        Write-Host "🔍 View logs: docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor Yellow
        Write-Host "🛑 Stop with: .\scripts\dev-stop.ps1" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Happy coding! 🎉" -ForegroundColor Magenta
        exit 0
    } catch {
        $retryCount++
        Write-Host "⏳ Waiting for service to be ready... ($retryCount/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

Write-Host "❌ Health check failed after $maxRetries attempts" -ForegroundColor Red
Write-Host "📋 Container logs:" -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml logs ai-dev-agent
Write-Host ""
Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
Write-Host "   1. Check if port 8501 is available" -ForegroundColor White
Write-Host "   2. Ensure Docker has enough resources (4GB+ RAM recommended)" -ForegroundColor White
Write-Host "   3. Check container status: docker-compose -f docker-compose.dev.yml ps" -ForegroundColor White
exit 1
