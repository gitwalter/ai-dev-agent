# Code Generator Node - Isolated Testing in LangGraph Studio

**Purpose**: Test the `code_generator_node` from Agile Factory in isolation to debug why it's not producing code.

## Prerequisites

1. **LangGraph Studio installed and running**
   - Install: `pip install langgraph-studio` or use LangGraph Cloud
   - Make sure you're in the project root directory

2. **Environment variables set**
   ```bash
   export GEMINI_API_KEY="your-api-key"
   export GOOGLE_API_KEY="your-api-key"  # Alternative name
   export LANGSMITH_API_KEY="your-langsmith-key"  # Optional, for prompt loading
   ```

3. **Graph registered in langgraph.json**
   - Already configured: `"code_generator_test": "agents/agile_factory/test_code_generator_studio.py:graph"`

## Step-by-Step Testing Instructions

### Step 1: Launch LangGraph Studio

```bash
# From project root directory
langgraph studio
```

Or if using LangGraph Cloud:
- Navigate to https://studio.langchain.com
- Select your project: `ai-dev-agent`

### Step 2: Select the Code Generator Test Graph

1. In LangGraph Studio, locate the **Graph Selection** dropdown (usually at the top)
2. Select `code_generator_test` from the dropdown
3. Wait for the graph to load - you should see a simple graph with:
   - Entry point: `code_generator`
   - End point: `END`

### Step 3: Prepare Initial State

The code generator node requires these fields:

**Required Fields:**
- `user_story`: The user story describing what to build
- `project_type`: Either `"website"` or `"streamlit_app"`
- `thread_id`: Unique identifier for this test run

**Optional but Recommended:**
- `requirements`: Dictionary with requirements analysis (from requirements_analyst)
- `architecture`: Dictionary with architecture design (from architecture_designer)

### Step 4: Test Cases

#### Test Case 1: Simple Website (Minimal Input)

```json
{
  "user_story": "As a user, I want a simple portfolio website with a home page, about page, and contact page.",
  "project_type": "website",
  "thread_id": "test-website-001",
  "requirements": {},
  "architecture": {},
  "status": "processing",
  "errors": []
}
```

#### Test Case 2: Website with Requirements and Architecture

```json
{
  "user_story": "As a user, I want a personal portfolio website that displays my projects, skills, and contact information.",
  "project_type": "website",
  "thread_id": "test-website-002",
  "requirements": {
    "summary": "Create a personal portfolio website",
    "functional_requirements": [
      {
        "id": "FR-001",
        "title": "Home Page",
        "description": "Display welcome message and introduction"
      },
      {
        "id": "FR-002",
        "title": "Projects Page",
        "description": "Showcase portfolio projects with descriptions"
      },
      {
        "id": "FR-003",
        "title": "Contact Page",
        "description": "Display contact information and form"
      }
    ]
  },
  "architecture": {
    "system_overview": "Simple static website with HTML, CSS, and JavaScript",
    "architecture_pattern": "Static Site",
    "components": [
      {
        "name": "Home Page",
        "description": "Main landing page"
      },
      {
        "name": "Projects Page",
        "description": "Portfolio showcase"
      },
      {
        "name": "Contact Page",
        "description": "Contact information and form"
      }
    ],
    "technology_stack": {
      "frontend": ["HTML5", "CSS3", "JavaScript"]
    }
  },
  "status": "processing",
  "errors": []
}
```

#### Test Case 3: Streamlit App

```json
{
  "user_story": "As a data analyst, I want a Streamlit app that loads CSV data and displays interactive charts.",
  "project_type": "streamlit_app",
  "thread_id": "test-streamlit-001",
  "requirements": {
    "summary": "Create a Streamlit app for data visualization",
    "functional_requirements": [
      {
        "id": "FR-001",
        "title": "CSV Upload",
        "description": "Allow users to upload CSV files"
      },
      {
        "id": "FR-002",
        "title": "Data Visualization",
        "description": "Display interactive charts based on uploaded data"
      }
    ]
  },
  "architecture": {
    "system_overview": "Streamlit application for data analysis",
    "architecture_pattern": "Single Page Application",
    "components": [
      {
        "name": "File Upload Component",
        "description": "Handles CSV file upload"
      },
      {
        "name": "Chart Component",
        "description": "Displays interactive visualizations"
      }
    ],
    "technology_stack": {
      "framework": ["Streamlit"],
      "data_processing": ["pandas"],
      "visualization": ["plotly", "matplotlib"]
    }
  },
  "status": "processing",
  "errors": []
}
```

## What to Check

### 1. Agent Execution
- Check if the agent is invoked successfully
- Look for any error messages in the state
- Verify the LLM is being called

### 2. Tool Calls
- Check if `write_file` tool is being called
- Verify tool names are correct: `write_file`, `python_repl`, `streamlit_validate_app`, etc.
- Check if tools are available to the agent

### 3. Workspace Directory
- Check `workspace_locations.code_generator_workspace` in the state
- Verify the directory exists: `agile_factory_workspace/code_gen_{thread_id}/`
- Check if files are being written to disk

### 4. Agent Response
- Check the agent's messages in the response
- Look for tool calls in the messages
- Verify the agent understands the task

### 5. File Extraction
- Check `code_files` in the final state
- Verify files are extracted from the workspace directory
- Check file paths and content

## Debugging Tips

### If No Files Are Generated:

1. **Check Agent Messages**
   - Look at the agent's response messages
   - Check if the agent mentions creating files but didn't call `write_file`
   - Verify the agent understands it needs to use tools

2. **Check Tool Availability**
   - Verify `write_file` tool is in the tools list
   - Check tool descriptions are clear
   - Ensure tools are properly formatted for LangChain

3. **Check System Prompt**
   - Verify the prompt emphasizes using `write_file` tool
   - Check if instructions are clear about file creation
   - Ensure the prompt mentions the workspace directory

4. **Check Workspace Directory**
   - Verify the directory is created
   - Check file permissions
   - Ensure the path is correct

5. **Check LLM Response**
   - Look at raw LLM output
   - Check if LLM is generating tool calls
   - Verify tool call format is correct

### Common Issues:

1. **Agent doesn't call write_file**
   - **Solution**: Strengthen the system prompt to emphasize tool usage
   - Add explicit examples of tool calls
   - Make tool descriptions more prominent

2. **Files written but not extracted**
   - **Solution**: Check `extract_files_from_directory` function
   - Verify file extensions match
   - Check workspace directory path

3. **Agent returns empty response**
   - **Solution**: Check API key is set
   - Verify LLM model is available
   - Check for rate limiting or API errors

## Expected Output

After successful execution, you should see:

```json
{
  "code_files": {
    "index.html": "<html>...</html>",
    "styles.css": "/* CSS styles */",
    "script.js": "// JavaScript code"
  },
  "workspace_locations": {
    "code_generator_workspace": "agile_factory_workspace/code_gen_test-website-001",
    "absolute_path": "/full/path/to/agile_factory_workspace/code_gen_test-website-001",
    "files_found_in": "agile_factory_workspace/code_gen_test-website-001"
  },
  "status": "processing",
  "current_node": "code_generator"
}
```

## Next Steps

Once the isolated test works:
1. Check what's different between the isolated test and the full workflow
2. Compare tool configurations
3. Check state passing between nodes
4. Verify prompt loading works correctly

