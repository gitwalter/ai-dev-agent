# Database Automation Guide

This guide explains how the automated database cleaning system works to ensure the app can run when pulled from GitHub while preserving user data during development.

## Overview

The system automatically manages the prompt database to solve the problem where:
- **Development**: Contains user data, chat history, and execution statistics
- **GitHub**: Should contain only essential prompt templates, no user data



## How It Works

### 1. Automatic Database Cleaning (Before Push)

When you run `git push`, the system automatically:

1. **Creates a clean database** by removing:
   - Execution data (chat history, user interactions)
   - Usage statistics and performance metrics
   - RAG documents and embeddings
   - Analysis and improvement data

2. **Keeps essential data**:
   - Core prompt templates for all agents
   - System configuration and settings
   - Agent definitions and capabilities

3. **Updates .gitignore** to include the clean database

### 2. Development Database Restoration (After Pull)

When you run `git pull`, the system automatically:

1. **Restores the development database** with all user data
2. **Updates .gitignore** to exclude the development database
3. **Preserves all user interactions and chat history**

### 3. Git Hooks Automation

The system uses Git hooks to automate the process:

- **Pre-push Hook**: Automatically cleans database before pushing
- **Post-merge Hook**: Automatically restores development database after pulling

## Setup Instructions

### 1. Initial Setup

```bash
# Run the setup script to configure Git hooks
python setup_git_hooks.py

# Test the automation system
python utils/github_database_automation.py status
```

### 2. Verify Configuration

```bash
# Check Git hooks status
python setup_git_hooks.py status

# Check database automation status
python utils/github_database_automation.py status
```

## Usage

### Normal Development Workflow

1. **Develop with full database**: All user data and chat history preserved
2. **Push to GitHub**: Database automatically cleaned and included
3. **Pull from GitHub**: Development database automatically restored

### Manual Operations

```bash
# Prepare database for GitHub (manual)
python utils/github_database_automation.py prepare

# Restore development database (manual)
python utils/github_database_automation.py restore

# Check system status
python utils/github_database_automation.py status
```

## File Structure

```
prompts/
├── prompt_templates.db              # Main database (development)
├── prompt_templates_clean.db        # Clean database (GitHub)
└── prompt_templates_backup.db       # Backup of development data
```

## Configuration

### .gitignore Updates

The system automatically manages `.gitignore` entries:

```gitignore
# Database files (managed by automation)
prompts/prompt_templates.db
prompts/prompt_templates_backup.db

# Include clean database for GitHub
!prompts/prompt_templates_clean.db
```

### Environment Variables

No additional environment variables required. The system uses existing configuration.

## Troubleshooting

### Common Issues

1. **Database Locked**: Close any applications using the database
2. **Git Hooks Not Working**: Run `python setup_git_hooks.py` to reinstall
3. **LangSmith Not Logging**: Check API key in `.streamlit/secrets.toml`

### Manual Recovery

```bash
# Force restore development database
python utils/github_database_automation.py restore --force

# Reinstall Git hooks
python setup_git_hooks.py --force
```

## Benefits

- **Seamless Collaboration**: Team members can run the app immediately after pull
- **Data Preservation**: User data and chat history preserved during development
- **Automated Process**: No manual intervention required
- **Git Integration**: Works with existing Git workflow
- **Automated Process**: No manual intervention required

## Support

For issues with:
- **Database automation**: Check the troubleshooting section
- **Git hooks**: Run the setup script again

The system is designed to be self-maintaining and requires minimal manual intervention.
