# AI-Dev-Agent Docker Deployment Guide
=====================================

**🚀 One-Command Setup - No More Machine Dependencies!**

This Docker setup eliminates all path issues, Anaconda dependencies, and machine-specific configurations. Get up and running in minutes!

## Quick Start (30 seconds)

### Windows
```cmd
# Clone and run
git clone <repo-url>
cd ai-dev-agent
scripts\container_setup.bat
```

### Linux/Mac
```bash
# Clone and run
git clone <repo-url>
cd ai-dev-agent
chmod +x scripts/container_setup.sh
./scripts/container_setup.sh
```

### Super Quick (Any Platform)
```cmd
# Just run the demo
scripts\quick_start.bat    # Windows
./scripts/quick_start.sh   # Linux/Mac
```

**That's it!** Your complete AI development environment is running.

## What You Get

### ✅ Complete Environment
- **Zero Configuration**: No Python path issues, no Anaconda setup
- **Consistent Environment**: Same setup on Windows, Mac, Linux
- **Full Development Stack**: All tools, dependencies, and services ready
- **Persistent Data**: Your projects and logs survive container restarts

### ✅ Multiple Services
- **Core AI System**: Main AI-Dev-Agent on port 8080
- **Web Interface**: User-friendly interface on port 3000 (future)
- **Database**: PostgreSQL for persistence on port 5432
- **Cache**: Redis for performance on port 6379

### ✅ Developer Experience
- **Instant Demo**: `docker-compose exec ai-dev-agent python run_demo.py`
- **Interactive Shell**: `docker-compose exec ai-dev-agent bash`
- **Live Development**: Source code mounted for real-time changes
- **Comprehensive Testing**: Full test suite in isolated environment

## Usage Examples

### Basic Usage
```bash
# Start the complete environment
docker-compose up -d

# Run the working demo
docker-compose exec ai-dev-agent python run_demo.py

# Enter the development environment
docker-compose exec ai-dev-agent bash

# Run tests
docker-compose exec ai-dev-agent pytest -v

# View logs
docker-compose logs -f ai-dev-agent
```

### Development Workflow
```bash
# Start development environment
docker-compose up -d

# Enter container for development
docker-compose exec ai-dev-agent bash

# Inside container - all paths work perfectly
cd /app
python run_demo.py                    # Run demo
pytest tests/ -v                     # Run tests
python examples/gem_1_smart_code_reviewer.py  # Run gems
python utils/context/ontological_framework_system.py  # Test systems

# Changes persist in mounted volumes
exit
```

### Production Deployment
```bash
# Build optimized production image
docker-compose -f docker-compose.prod.yml build

# Deploy with scaling
docker-compose -f docker-compose.prod.yml up -d --scale ai-dev-agent=3
```

## System Architecture

### Container Structure
```
ai-dev-agent-system/
├── Core Application     (Port 8080)
├── Web Interface       (Port 3000)
├── PostgreSQL Database (Port 5432)
├── Redis Cache        (Port 6379)
└── Persistent Volumes
    ├── /generated_projects
    ├── /logs
    └── /data
```

### Network Configuration
- **Internal Network**: All services communicate securely
- **External Access**: Only necessary ports exposed
- **Load Balancing**: Ready for horizontal scaling
- **Health Monitoring**: Automatic service health checks

## Configuration

### Environment Variables
```bash
# Core settings
CONTAINER_MODE=true
DEVELOPMENT_MODE=true
PYTHONPATH=/app

# Database settings
POSTGRES_DB=ai_dev_agent
POSTGRES_USER=developer
POSTGRES_PASSWORD=dev_password_123

# Cache settings
REDIS_URL=redis://cache:6379
```

### Volume Mounts
```yaml
volumes:
  - .:/app                           # Source code (development)
  - ai-dev-agent-projects:/app/generated_projects  # Persistent projects
  - ai-dev-agent-logs:/app/logs      # Persistent logs
  - ai-dev-agent-db:/var/lib/postgresql/data  # Database persistence
```

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs ai-dev-agent

# Rebuild without cache
docker-compose build --no-cache

# Check system resources
docker system df
docker system prune  # Clean up if needed
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild with correct user
docker-compose build --no-cache
```

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :8080

# Change ports in docker-compose.yml
ports:
  - "8081:8080"  # Use different external port
```

### Performance Optimization

#### For Development
```bash
# Use volume for faster file access
docker-compose -f docker-compose.dev.yml up -d
```

#### For Production
```bash
# Use optimized production configuration
docker-compose -f docker-compose.prod.yml up -d
```

#### Memory Management
```bash
# Monitor resource usage
docker stats

# Set memory limits
docker-compose up -d --memory 2g
```

## Advanced Features

### Custom Configuration
```bash
# Override default settings
cp config/default.yml config/local.yml
# Edit config/local.yml
docker-compose restart
```

### Integration with CI/CD
```yaml
# .github/workflows/test.yml
- name: Test with Docker
  run: |
    docker-compose up -d
    docker-compose exec -T ai-dev-agent pytest
    docker-compose down
```

### Scaling for Production
```bash
# Horizontal scaling
docker-compose up -d --scale ai-dev-agent=3

# Load balancer configuration
# Add nginx reverse proxy
```

## Benefits Over Local Installation

### ✅ Eliminates Common Problems
- **No Anaconda Path Issues**: Container handles all Python environments
- **No Machine Dependencies**: Same environment everywhere
- **No Version Conflicts**: Isolated dependency management
- **No Setup Complexity**: One command gets everything running

### ✅ Enhanced Development Experience
- **Instant Onboarding**: New developers productive in minutes
- **Consistent Environments**: Dev, test, and prod match exactly
- **Easy Collaboration**: Share exact same environment
- **Simple Deployment**: Same container works everywhere

### ✅ Production Ready
- **Security**: Isolated, non-root user, minimal attack surface
- **Scalability**: Easy horizontal scaling and load balancing
- **Monitoring**: Built-in health checks and logging
- **Reliability**: Automatic restarts and error recovery

## Migration from Local Setup

### Step 1: Backup Your Work
```bash
# Backup your existing work
cp -r generated_projects generated_projects_backup
cp -r logs logs_backup
```

### Step 2: Start Container Environment
```bash
# Follow quick start above
./scripts/container_setup.sh
```

### Step 3: Import Your Work
```bash
# Copy your work into container volumes
docker cp generated_projects_backup/. ai-dev-agent-system:/app/generated_projects/
docker cp logs_backup/. ai-dev-agent-system:/app/logs/
```

### Step 4: Verify Everything Works
```bash
# Test your setup
docker-compose exec ai-dev-agent python run_demo.py
docker-compose exec ai-dev-agent pytest
```

## Next Steps

### For Developers
1. **Explore the Gems**: Check out `examples/` directory
2. **Read the Docs**: Browse `docs/` for complete documentation
3. **Run Tests**: Execute `pytest` to see everything working
4. **Create Your Own**: Use our templates to build new gems

### For Production
1. **Configure Secrets**: Set up proper secret management
2. **Set up Monitoring**: Add Prometheus/Grafana monitoring
3. **Configure Backups**: Set up automated backup procedures
4. **Scale Services**: Configure load balancing and scaling

## Support

### Getting Help
- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issues for bugs
- **Community**: Join our development community
- **Examples**: Study working examples in `examples/`

### Contributing
1. **Fork the Repository**: Create your own fork
2. **Development Environment**: Use this Docker setup
3. **Make Changes**: Develop in the container
4. **Test Everything**: All tests must pass
5. **Submit PR**: Follow our contribution guidelines

---

**🎉 Welcome to hassle-free AI development!**

No more path issues, no more setup complexity, no more machine dependencies. Just pure, productive AI development with Docker! 🚀
