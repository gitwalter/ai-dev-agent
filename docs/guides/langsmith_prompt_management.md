# LangSmith Prompt Management Guide

## Overview

The AI-Dev-Agent project now uses a **hybrid prompt management system** that integrates [LangSmith Prompt Hub](https://smith.langchain.com) for centralized prompt management with local fallbacks for reliability.

Based on official documentation: [LangSmith - Manage Prompts Programmatically](https://docs.langchain.com/langsmith/manage-prompts-programmatically)

## Architecture

### Loading Strategy (Priority Order)

```
1. LangSmith Prompt Hub (cached)
   ↓ (if not available or failed)
2. LangSmith Prompt Hub (fresh pull)
   ↓ (if not available or failed)
3. Hardcoded Fallback
```

**Note**: The local database layer has been removed as it was redundant. The system now directly falls back to hardcoded prompts if LangSmith is unavailable.

### Benefits

✅ **Centralized Management**: All prompts in LangSmith Hub  
✅ **Version Control**: Track prompt changes over time  
✅ **A/B Testing**: Test different prompt versions  
✅ **Team Collaboration**: Easy sharing across team  
✅ **Caching**: Minimize API calls with local cache  
✅ **Offline Support**: Fallback to hardcoded prompts  
✅ **Free Tier**: Works with LangSmith Developer plan  

## Setup Complete

### What Was Migrated

All 8 agent system prompts have been successfully migrated to LangSmith:

| Agent | Prompt Name | Status |
|-------|-------------|--------|
| Requirements Analyst | `requirements_analyst_v1` | ✅ Migrated |
| Architecture Designer | `architecture_designer_v1` | ✅ Migrated |
| Code Generator | `code_generator_v1` | ✅ Migrated |
| Test Generator | `test_generator_v1` | ✅ Migrated |
| Code Reviewer | `code_reviewer_v1` | ✅ Migrated |
| Security Analyst | `security_analyst_v1` | ✅ Migrated |
| Documentation Generator | `documentation_generator_v1` | ✅ Migrated |
| Project Manager | `project_manager_v1` | ✅ Migrated |

View all prompts: [LangSmith Prompts Dashboard](https://smith.langchain.com/prompts)

## How It Works

### Agent Prompt Loading

When an agent initializes, the `AgentPromptLoader` automatically:

1. **Tries LangSmith first** (with caching)
2. **Uses hardcoded prompt** as fallback

```python
from prompts import get_agent_prompt_loader

# Default: LangSmith enabled
loader = get_agent_prompt_loader('requirements_analyst')
prompt = loader.get_system_prompt()  # Loads from LangSmith

# Disable LangSmith (use hardcoded only)
loader = AgentPromptLoader('code_generator', use_langsmith=False)
prompt = loader.get_system_prompt()  # Uses hardcoded fallback

# Force refresh from LangSmith (bypass cache)
prompt = loader.get_system_prompt(force_refresh=True)
```

### API Keys

API keys are loaded from `.streamlit/secrets.toml`:

```toml
LANGSMITH_API_KEY = "lsv2_pt_..."
LANGSMITH_PROJECT = "ai-dev-agent"
LANGSMITH_TRACING = "true"
```

## Managing Prompts

### View Prompts in LangSmith UI

1. Visit [https://smith.langchain.com/prompts](https://smith.langchain.com/prompts)
2. Browse your workspace prompts
3. View versions, tags, and history
4. Test prompts in the playground

### Update a Prompt

**Option 1: Via LangSmith UI** (Recommended for iterative testing)
1. Go to [https://smith.langchain.com/prompts](https://smith.langchain.com/prompts)
2. Select the prompt to edit
3. Make changes in the editor
4. Save as new version/commit
5. Agents will automatically use the latest version

**Option 2: Via Python Script**

```python
from langsmith import Client
from langchain_core.prompts import PromptTemplate

client = Client()

# Update prompt
new_prompt = PromptTemplate.from_template("""
You are an expert Requirements Analyst...
[your updated prompt text]
""")

# Push update (creates new commit)
url = client.push_prompt(
    "requirements_analyst_v1",
    object=new_prompt,
    description="Updated for better clarity",
    tags=["production", "v1.1"]
)
print(f"Updated: {url}")
```

### Pull Specific Versions

```python
from langsmith import Client

client = Client()

# Latest version
prompt = client.pull_prompt("requirements_analyst_v1")

# Specific commit
prompt = client.pull_prompt("requirements_analyst_v1:8d99cb87")

# Tagged version
prompt = client.pull_prompt("requirements_analyst_v1:prod")
```

### Create New Agent Prompt

```python
from langsmith import Client
from langchain_core.prompts import PromptTemplate

client = Client()

# Create new prompt
prompt = PromptTemplate.from_template("""
You are an expert [Agent Type]...
""")

# Push to LangSmith
url = client.push_prompt(
    "new_agent_v1",
    object=prompt,
    is_public=False,
    description="New agent system prompt",
    tags=["development", "v1.0"]
)
```

## Verification

To verify the system is working, check that agents load prompts correctly:

```python
from prompts import get_agent_prompt_loader

loader = get_agent_prompt_loader('requirements_analyst')
prompt = loader.get_system_prompt()
print(f"Loaded prompt: {len(prompt)} characters")
# Should print: "Loaded prompt: 461 characters" (from LangSmith)
```

All prompts have been migrated and are available in LangSmith Hub.

## LangSmith Free Tier Limits

| Resource | Developer Plan (Free) |
|----------|----------------------|
| **Seats** | 1 user |
| **Base Traces** | 5,000/month |
| **Trace Retention** | 14 days |
| **Rate Limit** | 50,000 events/hour |
| **Prompts** | Unlimited storage ✅ |

### Monitoring Usage

1. Visit [LangSmith Dashboard](https://smith.langchain.com)
2. Check "Settings" → "Usage"
3. Monitor trace consumption

**Note**: Prompt loading does NOT count toward trace limits! Only agent executions with tracing enabled count as traces.

## Caching

The system uses intelligent caching to minimize API calls:

- **First load**: Pulls from LangSmith, caches locally
- **Subsequent loads**: Uses cache (instant)
- **Force refresh**: Bypasses cache on demand

```python
# Clear cache for specific agent
from utils.prompt_management.langsmith_prompt_loader import get_langsmith_loader

loader = get_langsmith_loader()
loader.clear_cache('requirements_analyst')

# Clear all cache
loader.clear_cache()
```

## Troubleshooting

### Prompts Not Loading from LangSmith

**Check 1: API Key**
```python
import os
print(os.getenv('LANGSMITH_API_KEY'))  # Should show your key
```

**Check 2: Test Connection**
```python
from langsmith import Client
client = Client()
prompts = list(client.list_prompts())
print(f"Found {len(prompts)} prompts")
```

**Check 3: Verify Prompt Exists**
```python
from langchain import hub
try:
    prompt = hub.pull("requirements_analyst_v1")
    print("Prompt loaded successfully")
except Exception as e:
    print(f"Error: {e}")
```

### Fallback to Hardcoded Prompts

If LangSmith is unavailable, agents automatically fall back to hardcoded prompts in `prompts/agent_prompt_loader.py`. This ensures agents continue working even offline.

## Best Practices

1. **Test in Playground**: Use LangSmith UI to test prompts before deploying
2. **Version Control**: Tag important versions (prod, staging, dev)
3. **Descriptive Commits**: Add clear descriptions when updating prompts
4. **Monitor Usage**: Check LangSmith dashboard monthly
5. **Cache Management**: Clear cache after significant prompt updates
6. **Fallback Testing**: Periodically test offline mode

## Migration Status

✅ **Phase 1 Complete**: All prompts migrated to LangSmith  
✅ **Phase 2 Complete**: Hybrid loader implemented and tested  
✅ **Phase 3 Complete**: Documentation created  

**Next Steps**:
- Use LangSmith UI to refine prompts
- A/B test different prompt versions
- Monitor agent performance in LangSmith dashboard

## Resources

- [LangSmith Documentation](https://docs.langchain.com/langsmith)
- [Prompt Management Guide](https://docs.langchain.com/langsmith/manage-prompts-programmatically)
- [LangSmith Dashboard](https://smith.langchain.com)
- [Pricing Information](https://www.langchain.com/pricing-langsmith)

## Support

For issues or questions:
1. Check LangSmith [status page](https://status.langchain.com/)
2. Review [LangSmith documentation](https://docs.langchain.com/langsmith)
3. Check project logs for error details
4. Verify API key and network connectivity

