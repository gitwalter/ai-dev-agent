# How to Upload Prompts to LangSmith

## Method 1: Via Web UI (Recommended)

For each prompt file:

1. **Go to LangSmith Hub**: https://smith.langchain.com/hub

2. **Create New Prompt**:
   - Click "+ New Prompt"
   - Select "Prompt Template" type

3. **Configure Prompt**:
   - **Name**: Use exact name from filename (e.g., `complexity_analyzer_v1`)
   - **Description**: Copy from metadata JSON file
   - **Template**: Copy entire content from .txt file

4. **Add Variables**:
   - Click "Add Variable" for each variable in metadata
   - Variable names must match exactly

5. **Test Prompt**:
   - Use test input in playground
   - Verify output format
   - Check variable substitution

6. **Commit and Publish**:
   - Click "Commit"
   - Add commit message
   - Make it available to team

7. **Verify**:
   ```bash
   python scripts/pull_all_langsmith_prompts.py
   ```

## Method 2: Via LangChain Hub (If Available)

```python
from langchain import hub

# This may not work depending on permissions
# Usually prompts are created via UI
try:
    hub.push("complexity_analyzer_v1", prompt_template)
except:
    print("Use web UI instead")
```

## Prompt Files Created

- complexity_analyzer_v1.txt
- complexity_analyzer_v1_metadata.json

- agent_selector_v1.txt
- agent_selector_v1_metadata.json

- router_v1.txt
- router_v1_metadata.json

- project_manager_supervisor_v1.txt
- project_manager_supervisor_v1_metadata.json

- quality_control_supervisor_v1.txt
- quality_control_supervisor_v1_metadata.json

- task_router_supervisor_v1.txt
- task_router_supervisor_v1_metadata.json

