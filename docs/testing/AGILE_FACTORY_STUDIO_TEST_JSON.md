# Agile Factory Studio - Test JSON Examples

## 🚀 Initial State JSON (Start Agile Factory Workflow)

### Example 1: Website Project (Simple)

Use this JSON to start the agile factory workflow for a website project in LangGraph Studio.

```json
{
  "user_story": "As a user, I want a personal portfolio website that displays my projects, skills, and contact information so that potential employers can learn about me.",
  "project_type": "website",
  "thread_id": "portfolio-website-001",
  "max_iterations": 3,
  "code_review_iteration_count": 0,
  "test_iteration_count": 0,
  "hitl_approvals": {},
  "hitl_feedback": {},
  "status": "processing",
  "errors": [],
  "current_node": ""
}
```

### Example 2: Streamlit App Project (Data Analysis)

Use this JSON to start the agile factory workflow for a Streamlit app project.

```json
{
  "user_story": "As a data analyst, I want a Streamlit app that loads CSV data, displays interactive charts, and allows filtering by date range so that I can analyze sales trends.",
  "project_type": "streamlit_app",
  "thread_id": "sales-analytics-app-001",
  "max_iterations": 3,
  "code_review_iteration_count": 0,
  "test_iteration_count": 0,
  "hitl_approvals": {},
  "hitl_feedback": {},
  "status": "processing",
  "errors": [],
  "current_node": ""
}
```

### Example 3: Website Project (E-commerce)

```json
{
  "user_story": "As a business owner, I want an e-commerce website with product listings, shopping cart, and checkout functionality so that customers can purchase products online.",
  "project_type": "website",
  "thread_id": "ecommerce-site-001",
  "max_iterations": 3,
  "code_review_iteration_count": 0,
  "test_iteration_count": 0,
  "hitl_approvals": {},
  "hitl_feedback": {},
  "status": "processing",
  "errors": [],
  "current_node": ""
}
```

### Example 4: Streamlit App Project (Dashboard)

```json
{
  "user_story": "As a project manager, I want a Streamlit dashboard that visualizes project metrics, team performance, and task completion rates so that I can track project progress.",
  "project_type": "streamlit_app",
  "thread_id": "project-dashboard-001",
  "max_iterations": 3,
  "code_review_iteration_count": 0,
  "test_iteration_count": 0,
  "hitl_approvals": {},
  "hitl_feedback": {},
  "status": "processing",
  "errors": [],
  "current_node": ""
}
```

## 📋 Field Descriptions

### Required Fields

- **`user_story`** (string): The user story describing what needs to be built
- **`project_type`** (string): Either `"website"` or `"streamlit_app"`
- **`thread_id`** (string): Unique identifier for this workflow run (used for checkpointer persistence)

### Optional Fields (with defaults)

- **`max_iterations`** (int): Maximum iterations for feedback loops (default: 3)
- **`code_review_iteration_count`** (int): Current iteration count for code review loop (default: 0)
- **`test_iteration_count`** (int): Current iteration count for test loop (default: 0)
- **`hitl_approvals`** (dict): Dictionary tracking approvals at each checkpoint (default: {})
- **`hitl_feedback`** (dict): Dictionary storing feedback at each checkpoint (default: {})
- **`status`** (string): Workflow status - `"processing"`, `"complete"`, `"error"`, `"needs_revision"` (default: `"processing"`)
- **`errors`** (list): List of error messages (default: [])
- **`current_node`** (string): Current workflow node name (default: "")

## 🔄 Workflow Flow

The workflow follows this sequence:

1. **HITL Story Review** → Review initial user story
2. **Requirements Analyst** → Analyze and extract requirements
3. **HITL Requirements Review** → Review requirements
4. **Architecture Designer** → Design system architecture
5. **HITL Architecture Review** → Review architecture
6. **Code Generator** → Generate code files
7. **HITL Code Review Checkpoint** → Review generated code
8. **Code Reviewer** → Review code quality
9. **Testing Agent** → Generate and execute tests
10. **Documentation Generator** → Generate documentation
11. **HITL Final Review** → Final approval

## 💡 Tips

- Use descriptive `thread_id` values to track different workflow runs
- The workflow will pause at each HITL checkpoint for human approval
- Feedback loops (code review ↔ code generator, testing ↔ code generator) have max 3 iterations
- All generated files are stored in `agile_factory_workspace/{thread_id}/` directories

## 🧪 Testing in LangGraph Studio

1. Open LangGraph Studio
2. Load the `agile_factory` graph from `langgraph.json`
3. Use one of the JSON examples above as the initial state
4. The workflow will start at the `hitl_story_review` node
5. Follow the workflow through each HITL checkpoint

