# AI-Dev-Agent Quick Start (PowerShell)
# ====================================
# 
# Fastest way to get AI-Dev-Agent running on Windows
# No setup, no configuration, just run!
#
# Usage: .\scripts\quick_start.ps1
#

Write-Host "🚀 AI-Dev-Agent Quick Start" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green
Write-Host ""

# Method 1: Try native Python first (if available)
Write-Host "🔍 Checking for working Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    Write-Host "   Trying native execution..." -ForegroundColor White
    
    python run_demo.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Demo completed successfully!" -ForegroundColor Green
        Read-Host "Press Enter to continue..."
        exit 0
    } else {
        Write-Host "⚠️  Native Python had issues - switching to Docker..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Python not found or not working - using Docker approach..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🐳 Using Docker for guaranteed compatibility..." -ForegroundColor Cyan

# Method 2: Use Docker (guaranteed to work)
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please either:" -ForegroundColor Red
    Write-Host "   1. Install Python 3.11+ and run: python run_demo.py" -ForegroundColor Yellow
    Write-Host "   2. Install Docker Desktop and re-run this script" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📥 Get Docker: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Blue
    Read-Host "Press Enter to continue..."
    exit 1
}

Write-Host "🏗️  Building container (first time only)..." -ForegroundColor Yellow
docker-compose build ai-dev-agent

Write-Host "🚀 Running AI-Dev-Agent Demo..." -ForegroundColor Yellow
docker-compose run --rm ai-dev-agent python run_demo.py

Write-Host ""
Write-Host "🌟 Thank you for trying AI-Dev-Agent!" -ForegroundColor Green
Write-Host "   Visit our docs/ folder for complete documentation" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue..."
