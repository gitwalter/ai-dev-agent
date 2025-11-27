# Code Review Rigidity Parameter

## Overview

The Agile Factory workflow now supports a configurable `review_rigidity` parameter that controls how strict the code review process is. This allows you to balance between code quality and workflow efficiency.

## Parameters

### `review_rigidity` (float)
- **Range**: 0.0 to 1.0
- **Default**: 0.3 (lenient)
- **Description**: Controls how strict the code review is

### `skip_code_review` (bool)
- **Default**: False
- **Description**: If True, completely skips code review and goes directly to testing

## Rigidity Levels

### 0.0 - Very Lenient / Skip Review
- **Behavior**: Code review is skipped entirely
- **Use Case**: Rapid prototyping, when you trust the code generator
- **Auto-pass**: Immediate (if review happens, passes if code exists)

### 0.1 - 0.3 - Very Lenient
- **Behavior**: Review happens but auto-passes if code files exist
- **Use Case**: Quick iterations, functional code is sufficient
- **Auto-pass**: Immediate if code files exist
- **Max iterations**: 1

### 0.4 - 0.5 - Lenient
- **Behavior**: Review happens, auto-passes after 1 attempt if no critical bugs
- **Use Case**: Standard development, minor issues acceptable
- **Auto-pass**: After 1 failed attempt if no critical bugs
- **Max iterations**: 1-2

### 0.6 - 0.7 - Medium Strictness
- **Behavior**: Review happens, auto-passes after 2 attempts if no critical bugs
- **Use Case**: Production code, moderate quality requirements
- **Auto-pass**: After 2 failed attempts if no critical bugs
- **Max iterations**: 2

### 0.8 - 1.0 - Very Strict
- **Behavior**: Review happens, requires high quality code
- **Use Case**: Critical production code, high quality requirements
- **Auto-pass**: Only after max iterations (3)
- **Max iterations**: 3

## Usage Examples

### Skip Review Entirely
```python
initial_state = {
    "user_story": "...",
    "project_type": "website",
    "skip_code_review": True,  # Skip review completely
    # ... other state
}
```

### Very Lenient (Default)
```python
initial_state = {
    "user_story": "...",
    "project_type": "website",
    "review_rigidity": 0.2,  # Very lenient - auto-pass quickly
    # ... other state
}
```

### Medium Strictness
```python
initial_state = {
    "user_story": "...",
    "project_type": "website",
    "review_rigidity": 0.6,  # Medium - allow some iterations
    # ... other state
}
```

### Very Strict
```python
initial_state = {
    "user_story": "...",
    "project_type": "website",
    "review_rigidity": 0.9,  # Very strict - require high quality
    # ... other state
}
```

## How It Works

1. **Skip Check**: If `skip_code_review=True` or `rigidity <= 0.0`, code review is skipped entirely
2. **Review Execution**: If review happens, the LLM receives guidance based on rigidity level
3. **Auto-Pass Logic**: Based on rigidity, the system auto-approves after certain conditions:
   - Very lenient: Auto-pass if code files exist
   - Lenient: Auto-pass after 1 attempt if no critical bugs
   - Medium: Auto-pass after 2 attempts if no critical bugs
   - Strict: Only pass if review explicitly approves or max iterations reached

## Benefits

- **Faster Workflows**: Lower rigidity = faster completion
- **Flexible Quality Control**: Adjust strictness based on project needs
- **Prevents Infinite Loops**: Auto-pass logic prevents getting stuck
- **Configurable**: Easy to adjust per project or use case

## Recommendations

- **Prototyping**: Use `rigidity=0.1` or `skip_code_review=True`
- **Standard Development**: Use `rigidity=0.3` (default)
- **Production Code**: Use `rigidity=0.7`
- **Critical Systems**: Use `rigidity=0.9`

