# Smart Prompt Sync System

**Version**: 2.0  
**Status**: ✅ Implemented  
**Principle**: Hub = Source of Truth

## Overview

Intelligent synchronization system that keeps local prompts in sync with LangSmith Hub while respecting the hub as the authoritative source.

## Key Principles

### 1. Hub = Source of Truth ⭐
- LangSmith Hub is always the authoritative source
- Local cache is for offline fallback only
- Default behavior: Pull updates from hub

### 2. Safe Local Editing 
- Mark prompts as "locally modified" BEFORE editing
- Only push to hub if explicitly edited locally AND different from hub version
- Otherwise, always prefer hub version

### 3. Automatic Conflict Detection
- Compares content hashes to detect changes
- Warns about conflicts between local and hub versions
- Prevents accidental overwrites

## Usage

### Basic Sync (Pull Updates from Hub)

```bash
# Sync all prompts
python scripts/sync_prompts.py --all

# Sync specific prompt
python scripts/sync_prompts.py --prompt test_generator_v1

# Check current status
python scripts/sync_prompts.py --status
```

### Editing Local Prompts Safely

```bash
# Step 1: Mark as locally edited (IMPORTANT!)
python scripts/sync_prompts.py --mark-edited test_generator_v1

# Step 2: Edit the file
# Edit: prompts/langsmith_cache/test_generator_v1.txt

# Step 3: Push your changes to hub
python scripts/sync_prompts.py --prompt test_generator_v1 --auto-push
```

### Dry Run Mode

```bash
# See what would happen without making changes
python scripts/sync_prompts.py --all --dry-run
```

## How It Works

### Metadata Tracking

Each prompt has a metadata file: `prompts/langsmith_cache/metadata/{prompt-name}.json`

```json
{
  "prompt_name": "test_generator_v1",
  "last_fetched_from_hub": "2025-10-27T10:30:00",
  "locally_modified": false,
  "local_edit_timestamp": null,
  "hub_content_hash": "abc123...",
  "local_content_hash": "abc123...",
  "last_sync_timestamp": "2025-10-27T10:30:00",
  "sync_direction": "pull"
}
```

### Sync Logic

```
┌─────────────────────────────────────┐
│   Sync Prompt                       │
└─────────────────────────────────────┘
           │
           ▼
  ┌─────────────────┐
  │ Fetch from Hub  │
  └─────────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ Load Local Version   │
  └──────────────────────┘
           │
           ▼
  ┌──────────────────────┐
  │ Compare Hashes       │
  └──────────────────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌──────────────┐
│ Same    │ │ Different    │
└─────────┘ └──────────────┘
     │           │
     │      ┌────┴────┐
     │      │         │
     │      ▼         ▼
     │  ┌────────┐ ┌─────────────┐
     │  │ Local  │ │ Hub Newer   │
     │  │Modified│ │             │
     │  └────────┘ └─────────────┘
     │      │         │
     │      ▼         ▼
     │  ┌────────┐ ┌─────────────┐
     │  │ Push   │ │ Pull Update │
     │  │to Hub  │ │from Hub     │
     │  └────────┘ └─────────────┘
     │      │         │
     └──────┴─────────┴────────►
                   │
                   ▼
            ┌──────────────┐
            │ Update       │
            │ Metadata     │
            └──────────────┘
```

### Safety Features

1. **Content Hashing**: SHA256 hashes detect actual content changes
2. **Backup on Update**: Old versions backed up before overwriting
3. **Conflict Detection**: Warns when local edits conflict with hub updates
4. **Dry Run Mode**: Test sync without making changes
5. **Metadata Tracking**: Complete audit trail of all changes

## Automatic Integration

The sync system is automatically integrated into the prompt loader:

```python
from utils.prompt_management.langsmith_prompt_loader import get_langsmith_loader

# Auto-sync enabled by default
loader = get_langsmith_loader()

# Automatically syncs when loading
prompt = loader.load_from_langsmith("test_generator")
```

Disable auto-sync if needed:
```python
loader = LangSmithPromptLoader(auto_sync=False)
```

## Examples

### Example 1: Pull Latest Updates

```bash
$ python scripts/sync_prompts.py --all

🔄 Syncing all prompts...

⬇️ test_generator_v1: Updated local with newer hub version (5432 chars)
⬇️ code_generator_v1: Pulled fresh version from hub (8901 chars)
✅ requirements_analyst_v1: Hub and local are identical - no sync needed

📊 Sync Summary
================
Total prompts:     10
Pulled from hub:   2
Updated from hub:  1
Pushed to hub:     0
Conflicts:         0
Errors:            0
```

### Example 2: Push Local Edits

```bash
$ python scripts/sync_prompts.py --mark-edited test_generator_v1
📝 Marking test_generator_v1 as locally edited...
✅ Done! Now you can safely edit prompts/langsmith_cache/test_generator_v1.txt

# Edit the file...

$ python scripts/sync_prompts.py --prompt test_generator_v1 --auto-push
🔄 Syncing test_generator_v1...
⚠️  Auto-push enabled - local changes will be pushed if different

⬆️ test_generator_v1: Pushed local changes to hub (5678 chars)
```

### Example 3: Check Status

```bash
$ python scripts/sync_prompts.py --status

📊 Prompt Sync Status
==================================================
Prompt Name                    Modified   Last Sync                 Direction
--------------------------------------------------
test_generator_v1              ✏️ YES     2025-10-27T10:30:00       push
code_generator_v1              📥 No      2025-10-27T10:25:00       pull
requirements_analyst_v1        📥 No      2025-10-27T10:20:00       pull
==================================================

📝 Summary: 10 prompts, 1 locally modified
```

## Best Practices

### ✅ DO

- **Always mark prompts as edited** before modifying locally
- **Sync regularly** to get hub updates
- **Use dry-run** to preview changes
- **Check status** to see which prompts are modified
- **Trust the hub** as source of truth

### ❌ DON'T

- Don't edit local prompts without marking them first
- Don't manually edit metadata files
- Don't ignore conflict warnings
- Don't disable auto-sync unless necessary
- Don't push unfinished edits to hub

## Troubleshooting

### Conflict Detected

```bash
⚠️ test_generator_v1: Local modified and differs from hub - manual resolution needed
```

**Resolution:**
1. View local version: `prompts/langsmith_cache/test_generator_v1.txt`
2. View hub version: Check LangSmith UI
3. Choose:
   - Keep local: `python scripts/sync_prompts.py --prompt test_generator_v1 --auto-push`
   - Use hub: Delete local file and re-sync

### Sync Failed

If sync fails, the system falls back to cached local version. Check:
- LangSmith API key is set
- Network connection is available
- Prompt exists in LangSmith Hub

### Local Cache Corrupted

Delete cache and re-sync:
```bash
rm -rf prompts/langsmith_cache/*.txt
python scripts/sync_prompts.py --all
```

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                 Smart Prompt Sync                    │
└──────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌───────────┐ ┌──────────────┐
│ Sync Manager │ │  Prompt   │ │   Metadata   │
│              │ │  Loader   │ │   Tracker    │
└──────────────┘ └───────────┘ └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  LangSmith Hub │
              │ (Source of     │
              │  Truth)        │
              └────────────────┘
```

## Files

- `utils/prompt_management/prompt_sync_manager.py` - Core sync logic
- `utils/prompt_management/langsmith_prompt_loader.py` - Integrated loader
- `scripts/sync_prompts.py` - CLI interface
- `prompts/langsmith_cache/` - Local cache directory
- `prompts/langsmith_cache/metadata/` - Sync metadata

## Testing

```bash
# Test sync without changes
python scripts/sync_prompts.py --all --dry-run

# Test specific prompt
python scripts/sync_prompts.py --prompt test_generator_v1 --dry-run

# Verify status
python scripts/sync_prompts.py --status
```

---

**Remember**: Hub = Source of Truth. Always sync before editing locally!

