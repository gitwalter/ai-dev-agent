# Git Pull Conflicts with Database Files - Solution Guide

## Problem Description

You're experiencing conflicts when running `git pull` because:

1. **Database cleaning system** modifies files (`.gitignore` and database files)
2. **IDE auto-stages these changes** automatically 
3. **Git pull conflicts** with staged changes
4. **Duplicate .gitignore entries** from multiple automation runs

## ✅ Complete Solution

### 1. Immediate Fix - Use Safe Pull

Instead of `git pull`, use our safe pull script:

```bash
# Use the safe pull script
python scripts/safe_pull.py

# Or set up git aliases (see step 2) and use:
git safe-pull
```

### 2. Set Up Git Aliases (Recommended)

```bash
# Set up convenient Git aliases
python scripts/setup_git_aliases.py

# Now you can use:
git safe-pull    # Safely pull with database automation
git db-status    # Check database automation status
git db-prepare   # Manually prepare database for GitHub
git db-restore   # Manually restore development database
```

### 3. Configure Your IDE

The project includes VS Code settings (`.vscode/settings.json`) that:
- Disable auto-staging of database files
- Exclude database files from file watchers
- Set up proper Python paths

**For other IDEs**: Configure them to exclude these files from auto-staging:
- `prompts/prompt_templates*.db`
- `.gitignore` (when modified by automation)

### 4. Manual Recovery (If Needed)

If you're currently stuck with staged database files:

```bash
# Option A: Stash and pull
git stash push -m "database files before pull"
git pull
git stash pop

# Option B: Reset and pull
git reset HEAD prompts/prompt_templates*.db .gitignore
git pull

# Option C: Use our safe operations utility
python -c "
from utils.safe_git_operations import SafeGitOperations
safe_git = SafeGitOperations()
success, stashed = safe_git.prepare_for_pull()
print(f'Prepared: {success}, Stashed: {stashed}')
"
git pull
```

## How The Solution Works

### Safe Pull Process

1. **Check for staged changes** - Identifies any staged database files
2. **Stash changes safely** - Stashes only database-related changes
3. **Perform git pull** - Pulls without conflicts
4. **Restore development database** - Runs database automation to restore your data
5. **Restore stashed changes** - Brings back any previous changes

### Database Automation Integration

The system automatically:
- **Before push**: Cleans database, commits clean version
- **After pull**: Restores development database with your data
- **During conflicts**: Safely handles staged changes

### IDE Configuration

VS Code settings prevent auto-staging of:
- Database files (`prompts/prompt_templates*.db`)
- Automation-modified files (`.gitignore`)
- Generated content (`logs/`, `generated_projects/`)

## File Organization

```
project/
├── scripts/
│   ├── safe_pull.py              # Safe pull with stash handling
│   └── setup_git_aliases.py      # Git aliases for convenience
├── utils/
│   ├── safe_git_operations.py    # Git utilities for database automation
│   └── github_database_automation.py  # Main automation system
├── .vscode/
│   └── settings.json             # IDE configuration
└── docs/troubleshooting/
    └── git_pull_conflicts.md     # This guide
```

## Common Scenarios

### Scenario 1: "I have staged database files and can't pull"

```bash
# Quick fix
python scripts/safe_pull.py

# Or manually
git stash push prompts/prompt_templates*.db .gitignore -m "temp stash"
git pull
git stash pop
```

### Scenario 2: "My IDE keeps staging database files"

1. Check if `.vscode/settings.json` exists and is configured properly
2. For other IDEs, configure them to exclude database files from auto-staging
3. Use `git safe-pull` instead of regular `git pull`

### Scenario 3: "Database automation isn't working after pull"

```bash
# Check status
python utils/github_database_automation.py status

# Manually restore development database
python utils/github_database_automation.py restore
```

### Scenario 4: "I lost my development data"

```bash
# Check for backup files
ls prompts/prompt_templates_backup.db
ls prompts/prompt_templates_development.db

# Restore from backup
python utils/github_database_automation.py restore

# If backups exist but automation fails, copy manually:
cp prompts/prompt_templates_backup.db prompts/prompt_templates.db
```

## Prevention Tips

### Daily Workflow

```bash
# ✅ Recommended workflow
git add .
git commit -m "your changes"
git safe-pull  # Instead of git pull
git push
```

### IDE Configuration

- Configure your IDE to exclude database files from auto-staging
- Use the provided VS Code settings
- Set up file watchers to ignore database changes

### Git Hooks

The system includes git hooks that automatically:
- Clean database before push
- Restore database after pull (via post-merge hook)

## Testing Your Setup

### 1. Test Safe Pull

```bash
# Create some test changes
echo "# test" >> README.md
git add README.md

# Test safe pull
python scripts/safe_pull.py
```

### 2. Test Database Automation

```bash
# Check automation status
python utils/github_database_automation.py status

# Test database operations
python utils/github_database_automation.py prepare
python utils/github_database_automation.py restore
```

### 3. Test Git Aliases

```bash
# Set up aliases
python scripts/setup_git_aliases.py

# Test aliases
git db-status
git safe-pull
```

## Advanced Configuration

### Custom Safe Pull Options

```bash
# Skip database restoration after pull
python scripts/safe_pull.py --no-restore-db

# With git alias
git config alias.quick-pull "!python scripts/safe_pull.py --no-restore-db"
```

### Manual Git Operations

```bash
# Check what's staged
git diff --cached --name-only

# Unstage database files only
git reset HEAD prompts/prompt_templates*.db

# Stash only database files
git stash push prompts/prompt_templates*.db -m "database files"
```

## Troubleshooting

### Issue: "Safe pull script fails"

1. Check if Python path is correct
2. Ensure you're in the project root
3. Check if git is available in PATH
4. Run with verbose output: `python scripts/safe_pull.py -v` (if implemented)

### Issue: "Git aliases don't work"

1. Check if aliases were created: `git config --global --list | grep alias`
2. Ensure Python scripts are executable
3. Use full paths if needed

### Issue: "Database automation fails"

1. Check database file permissions
2. Ensure no applications are using the database
3. Check if backup files exist
4. Run manual recovery: `python utils/github_database_automation.py restore --force`

## Summary

- **Use `git safe-pull`** instead of `git pull`
- **Configure your IDE** to not auto-stage database files
- **Set up git aliases** for convenience
- **The system handles everything automatically** - database cleaning, restoration, and conflict resolution

This solution eliminates pull conflicts while preserving your development data and maintaining the automated database cleaning system.
