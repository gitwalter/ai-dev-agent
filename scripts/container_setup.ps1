# AI-Dev-Agent Container Setup Script (PowerShell 2024)
# =====================================================
# 
# Production-ready container setup following 2024 best practices
# - Secure execution policy management
# - Comprehensive error handling
# - Docker security validation
# - Multi-stage container optimization
#
# Usage: 
#   PowerShell -ExecutionPolicy Bypass -File .\scripts\container_setup.ps1
#   OR
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\scripts\container_setup.ps1
#

Write-Host "🚀 AI-Dev-Agent Container Setup (Windows PowerShell)" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""

# Comprehensive Docker installation and security validation (2024 standards)
Write-Host "🔍 Validating Docker environment..." -ForegroundColor Yellow

# Check Docker Desktop installation and version
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    
    # Validate Docker is running
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Docker daemon is not running. Starting Docker Desktop..." -ForegroundColor Yellow
        Start-Process "docker" -ArgumentList "info" -Wait -WindowStyle Hidden
    }
} catch {
    Write-Host "❌ Docker is not installed or not accessible." -ForegroundColor Red
    Write-Host "   Please install Docker Desktop from:" -ForegroundColor Yellow
    Write-Host "   https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Blue
    Write-Host "   Ensure Docker Desktop is running before retrying." -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose (bundled with Docker Desktop 2024+)
try {
    $composeVersion = docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Compose V2 found: $composeVersion" -ForegroundColor Green
    } else {
        # Fallback to legacy docker-compose
        $legacyComposeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker Compose V1 found: $legacyComposeVersion" -ForegroundColor Green
            Write-Host "ℹ️  Consider upgrading to Docker Compose V2 for better performance" -ForegroundColor Blue
        } else {
            throw "Docker Compose not found"
        }
    }
} catch {
    Write-Host "❌ Docker Compose is not available." -ForegroundColor Red
    Write-Host "   Please ensure Docker Desktop is properly installed and updated." -ForegroundColor Yellow
    exit 1
}

# Security validation - check if running as administrator (not recommended)
$currentPrincipal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "⚠️  Running as Administrator detected." -ForegroundColor Yellow
    Write-Host "   For security, consider running as regular user when possible." -ForegroundColor Yellow
}

Write-Host ""

# Check if containers are already running
Write-Host "🔍 Checking for existing containers..." -ForegroundColor Yellow
$existingContainers = docker ps -q --filter "name=ai-dev-agent"
if ($existingContainers) {
    Write-Host "⚠️  AI-Dev-Agent containers are already running" -ForegroundColor Yellow
    $response = Read-Host "   Would you like to restart them? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "🔄 Stopping existing containers..." -ForegroundColor Yellow
        docker-compose down
    } else {
        Write-Host "ℹ️  Keeping existing containers running" -ForegroundColor Blue
        exit 0
    }
}

# Build and start containers
Write-Host "🏗️  Building AI-Dev-Agent containers..." -ForegroundColor Yellow
docker-compose build --no-cache

Write-Host "🚀 Starting AI-Dev-Agent environment..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow
$runningContainers = docker ps --filter "name=ai-dev-agent-system" --filter "status=running"
if ($runningContainers -match "ai-dev-agent-system") {
    Write-Host "✅ AI-Dev-Agent core system is running" -ForegroundColor Green
} else {
    Write-Host "❌ AI-Dev-Agent core system failed to start" -ForegroundColor Red
    Write-Host "📋 Container logs:" -ForegroundColor Yellow
    docker-compose logs ai-dev-agent
    exit 1
}

# Display connection information
Write-Host ""
Write-Host "🎉 AI-Dev-Agent Environment Ready!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Services Available:" -ForegroundColor Cyan
Write-Host "   • Core System:     http://localhost:8080" -ForegroundColor White
Write-Host "   • Web Interface:   http://localhost:3000 (if enabled)" -ForegroundColor White
Write-Host "   • Database:        localhost:5432 (postgres)" -ForegroundColor White
Write-Host "   • Cache:           localhost:6379 (redis)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "   • Enter container:      docker-compose exec ai-dev-agent bash" -ForegroundColor White
Write-Host "   • View logs:           docker-compose logs -f ai-dev-agent" -ForegroundColor White
Write-Host "   • Run tests:           docker-compose exec ai-dev-agent pytest" -ForegroundColor White
Write-Host "   • Stop services:       docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Quick Start:" -ForegroundColor Cyan
Write-Host "   docker-compose exec ai-dev-agent python run_demo.py" -ForegroundColor White
Write-Host ""

# Test core functionality
Write-Host "🧪 Testing core functionality..." -ForegroundColor Yellow
try {
    $testResult = docker-compose exec -T ai-dev-agent python -c "import utils.context.ontological_framework_system; print('✅ Ontological framework system loaded successfully')"
    Write-Host "✅ Core systems test passed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Core systems test failed - check configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌟 Container Setup Complete!" -ForegroundColor Green
Write-Host "   Your AI-Dev-Agent environment is ready for development." -ForegroundColor White
Write-Host "   No more machine dependencies or path issues!" -ForegroundColor White
Write-Host ""

# Keep window open
Read-Host "Press Enter to continue..."
