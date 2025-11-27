# LLM Model Configuration

## Overview

The Agile Factory workflow supports switching between different Gemini models to optimize for rate limits, cost, or performance.

## Available Models

- **gemini-2.5-flash-lite** (Default): Faster, lower cost, better rate limits
- **gemini-2.5-flash**: More capable, higher rate limits on paid plans

## Configuration Methods

### Method 1: State Parameter (Recommended)

Set the model in the initial state:

```python
initial_state = {
    "user_story": "...",
    "project_type": "website",
    "llm_model": "gemini-2.5-flash-lite",  # or "gemini-2.5-flash"
    # ... other state
}
```

**Aliases Supported:**
- `"flash"` → `"gemini-2.5-flash"`
- `"flash-lite"` → `"gemini-2.5-flash-lite"`
- `"lite"` → `"gemini-2.5-flash-lite"`
- `"default"` → `"gemini-2.5-flash-lite"`

### Method 2: Environment Variable

Set the `GEMINI_MODEL` environment variable:

```bash
# Windows PowerShell
$env:GEMINI_MODEL = "gemini-2.5-flash-lite"

# Linux/macOS
export GEMINI_MODEL=gemini-2.5-flash-lite
```

**Aliases Supported:** Same as state parameter

### Method 3: Default Behavior

If neither state nor environment variable is set, defaults to `gemini-2.5-flash-lite`.

## Priority Order

1. **State parameter** (`llm_model` or `model_name` in state)
2. **Environment variable** (`GEMINI_MODEL`)
3. **Default** (`gemini-2.5-flash-lite`)

## Usage Examples

### Use Flash Lite (Default - Better Rate Limits)
```python
initial_state = {
    "llm_model": "gemini-2.5-flash-lite",  # or omit for default
    # ... other state
}
```

### Use Flash (More Capable)
```python
initial_state = {
    "llm_model": "gemini-2.5-flash",
    # ... other state
}
```

### Use Alias
```python
initial_state = {
    "llm_model": "lite",  # Automatically converts to "gemini-2.5-flash-lite"
    # ... other state
}
```

### Environment Variable
```bash
# Set once, applies to all runs
export GEMINI_MODEL=gemini-2.5-flash-lite
python -m pytest tests/agile_factory/test_workflow_prompt_llm_verification.py
```

## Benefits

- **Rate Limits**: Flash-lite typically has better rate limits on free tier
- **Cost**: Flash-lite is more cost-effective
- **Performance**: Flash may be more capable for complex tasks
- **Flexibility**: Easy to switch based on needs

## When to Use Each Model

### Use Flash Lite When:
- Hitting rate limits with Flash
- Cost is a concern
- Tasks are relatively straightforward
- Testing/development

### Use Flash When:
- Need maximum capability
- Complex code generation tasks
- Paid plan with higher rate limits
- Production critical workflows

## Implementation Details

All nodes automatically use the configured model:
- `requirements_node`
- `architecture_node`
- `code_generator_node`
- `code_reviewer_node`
- `testing_node`
- `documentation_node`

The model is determined once per node execution using the `get_llm_model()` utility function.

