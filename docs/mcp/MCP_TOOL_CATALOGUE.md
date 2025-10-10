# MCP Tool Catalogue
**Comprehensive catalogue of all MCP tools available in the AI-Dev-Agent system**

**Created**: 2025-10-10  
**Sprint**: US-RAG-001 Phase 5 Enhancement  
**Last Updated**: 2025-10-10  

---

## 📋 **Table of Contents**

1. [Database Tools](#database-tools)
2. [Agile Automation Tools](#agile-automation-tools)
3. [RAG & Context Tools](#rag--context-tools)
4. [Git & Version Control Tools](#git--version-control-tools)
5. [File & Link Integrity Tools](#file--link-integrity-tools)
6. [Testing & Quality Tools](#testing--quality-tools)
7. [System & Monitoring Tools](#system--monitoring-tools)
8. [Validation & Consistency Tools](#validation--consistency-tools)

---

## 🗄️ **Database Tools**

**Location**: `utils/mcp/tools/database_tools.py`

### Available Databases (12 Total)

| Database | Path | Purpose |
|----------|------|---------|
| `agent_tracking` | `utils/universal_agent_tracking.db` | Agent sessions, events, context switches |
| `rag_system` | `data/rag_system.db` | RAG document indexing and query logs |
| `optimization` | `utils/optimization.db` | System optimization tracking |
| `prompt_optimization` | `prompts/optimization/optimization.db` | Prompt optimization metrics |
| `prompt_templates` | `prompts/prompt_templates.db` | Prompt template storage |
| `analytics` | `utils/analytics.db` | System-wide analytics |
| `security_events` | `utils/security_events.db` | Security event logging |
| `learning_experiences` | `utils/learning_experiences.db` | Learning and pattern detection |
| `test_results` | `utils/test_pipeline_results.db` | Test execution results |
| `research_cache` | `data/research_cache.db` | Research data caching |
| `strategic_selection` | `utils/strategic_selection.db` | Rule selection tracking |
| `rule_optimization` | `utils/rule_optimization.db` | Rule performance tracking |

### MCP Tools

#### `db.list_databases`
**Access Level**: UNRESTRICTED  
**Category**: SYSTEM  
**Description**: List all available project databases with their descriptions  
**Returns**: Database registry with size, status, and metadata  

**Example**:
```python
result = await mcp_client.call_tool("db.list_databases")
# Returns: {"total_databases": 12, "databases": [...]}
```

#### `db.get_schema`
**Access Level**: UNRESTRICTED  
**Category**: SYSTEM  
**Parameters**:
- `database_name` (str): Database name from registry  

**Description**: Get schema information including tables, columns, and row counts  

**Example**:
```python
result = await mcp_client.call_tool("db.get_schema", {"database_name": "agent_tracking"})
```

#### `db.query_agent_activities`
**Access Level**: UNRESTRICTED  
**Category**: SYSTEM  
**Parameters**:
- `agent_id` (str, optional): Filter by agent ID
- `activity_type` (str, optional): Filter by activity type
- `limit` (int, default=50): Maximum results

**Description**: Query agent activities across all tracking databases  

**Example**:
```python
result = await mcp_client.call_tool("db.query_agent_activities", {
    "agent_id": "context_aware_agent_001",
    "limit": 100
})
```

#### `db.get_agent_timeline`
**Access Level**: UNRESTRICTED  
**Category**: SYSTEM  
**Parameters**:
- `agent_id` (str, optional): Filter by agent ID
- `hours` (int, default=24): Time window

**Description**: Get comprehensive timeline of agent activities with events and context switches  

#### `db.get_rag_statistics`
**Access Level**: UNRESTRICTED  
**Category**: SYSTEM  
**Description**: Get RAG system statistics including indexed documents, query logs, and usage metrics  

**Example**:
```python
result = await mcp_client.call_tool("db.get_rag_statistics")
# Returns: indexed docs, chunks, recent queries, query types, most accessed
```

#### `db.execute_custom_query`
**Access Level**: RESTRICTED  
**Category**: SYSTEM  
**Parameters**:
- `database_name` (str): Database name
- `query` (str): SQL SELECT query (read-only)

**Description**: Execute custom read-only SQL queries (SELECT only, no modifications)  

**Security**: Only SELECT queries allowed. DROP, DELETE, INSERT, UPDATE, ALTER, CREATE are blocked.

---

## 📊 **Agile Automation Tools**

**Location**: `utils/mcp/tools/agile_tools.py` (To be created)

### High-Value Utilities

#### User Story Automation
**Source**: `utils/agile/agile_story_automation.py`  
**Primary Functions**:
- Story creation from templates
- Story status updates
- Story validation
- Template management

#### Artifacts Automation
**Source**: `utils/agile/artifacts_automation.py`  
**Primary Functions**:
- Catalog synchronization
- Backlog updates
- Sprint artifact management
- Velocity tracking

#### Automatic Story Detection
**Source**: `utils/agile/automatic_story_detection.py`  
**Primary Functions**:
- Context-based story detection
- Keyword-based story identification
- Story recommendation engine

### MCP Tools (Proposed)

#### `agile.create_user_story`
**Parameters**: story_template, title, description, acceptance_criteria, story_points  
**Description**: Create new user story from template  

#### `agile.update_story_status`
**Parameters**: story_id, new_status, notes  
**Description**: Update story status with automation (uses `scripts/automate_user_story_updates.py`)  

#### `agile.sync_artifacts`
**Parameters**: artifact_type (catalog, backlog, velocity)  
**Description**: Synchronize agile artifacts  

#### `agile.detect_active_story`
**Parameters**: context, files_modified  
**Description**: Detect which user story is currently being worked on  

---

## 🧠 **RAG & Context Tools**

**Location**: `utils/mcp/tools/rag_tools.py` (Existing)

### Available Tools

#### `rag.upload_document`
**Parameters**: file_path, category  
**Description**: Upload and index document for RAG retrieval  

#### `rag.semantic_search`
**Parameters**: query, limit, search_type  
**Description**: Semantic search across indexed documents  

#### `rag.get_context_for_file`
**Parameters**: file_path  
**Description**: Get relevant context for specific file  

#### `rag.index_codebase`
**Parameters**: root_path, file_types  
**Description**: Index entire codebase for semantic search  

---

## 🔗 **Git & Version Control Tools**

**Location**: `utils/mcp/tools/git_tools.py` (To be created)

### High-Value Utilities

#### Git Automation Wrapper
**Source**: `utils/git/git_automation_wrapper.py`  
**Primary Functions**:
- Safe git operations (add, commit, push)
- Branch management
- Conflict detection
- Git history analysis

#### GitHub Database Automation
**Source**: `utils/git/github_database_automation.py`  
**Primary Functions**:
- GitHub API integration
- Issue/PR management
- Repository statistics

### MCP Tools (Proposed)

#### `git.safe_commit`
**Parameters**: message, files  
**Description**: Perform safe git commit with validation  

#### `git.create_branch`
**Parameters**: branch_name, base_branch  
**Description**: Create and checkout new branch  

#### `git.get_status`
**Description**: Get current git status with file changes  

#### `git.sync_with_github`
**Description**: Synchronize local changes with GitHub  

---

## 🔧 **File & Link Integrity Tools**

**Location**: `utils/mcp/tools/link_integrity_tools.py` (Existing)

### Available Tools

#### `link.scan_all`
**Description**: Scan project for all internal documentation links  

#### `link.validate`
**Description**: Validate all links and find broken ones  

#### `link.heal`
**Parameters**: rename_mapping  
**Description**: Heal links after file renames/moves  

#### `link.generate_report`
**Description**: Generate comprehensive link analysis report  

#### `link.check_before_move`
**Parameters**: old_path, new_path  
**Description**: Check link impact before moving files  

---

## 🧪 **Testing & Quality Tools**

**Location**: `utils/mcp/tools/testing_tools.py` (To be created)

### High-Value Scripts

#### Test Catalogue Automation
**Source**: `scripts/automate_test_catalogue.py`  
**Purpose**: Maintain test catalogue automatically  

#### Test Pipeline
**Source**: `scripts/run_test_pipeline.py`  
**Purpose**: Execute comprehensive test pipeline  

### MCP Tools (Proposed)

#### `test.update_catalogue`
**Description**: Update test catalogue with latest test status  

#### `test.run_suite`
**Parameters**: suite_name, test_path  
**Description**: Run specific test suite  

#### `test.get_coverage`
**Parameters**: path  
**Description**: Get test coverage statistics  

#### `test.validate_quality`
**Description**: Run quality assurance checks  

---

## 🖥️ **System & Monitoring Tools**

**Location**: `utils/mcp/tools/system_tools.py` (To be created)

### High-Value Utilities

#### Agent Monitor
**Source**: `utils/monitoring/agent_monitor.py`  
**Purpose**: Real-time agent activity monitoring  

#### Health Dashboard
**Source**: `utils/monitoring/health_dashboard.py`  
**Purpose**: System health monitoring  

### MCP Tools (Proposed)

#### `system.get_health`
**Description**: Get current system health status  

#### `system.get_agent_status`
**Parameters**: agent_id  
**Description**: Get specific agent status and metrics  

#### `system.list_active_agents`
**Description**: List all currently active agents  

#### `system.get_performance_metrics`
**Parameters**: time_window  
**Description**: Get system performance metrics  

---

## ✅ **Validation & Consistency Tools**

**Location**: `utils/mcp/tools/validation_tools.py` (To be created)

### High-Value Scripts

#### Hilbert Consistency Validator
**Source**: `scripts/hilbert_consistency_validator.py`  
**Purpose**: Formal consistency validation using Hilbert system  

#### Cursor Rules Validator
**Source**: `scripts/validate_cursor_rules.py`  
**Purpose**: Validate Cursor rule YAML frontmatter  

#### File Organization Validator
**Source**: `scripts/validate_file_organization.py`  
**Purpose**: Validate file organization standards  

### MCP Tools (Proposed)

#### `validate.hilbert_consistency`
**Parameters**: scope (file, directory, project)  
**Description**: Run Hilbert formal consistency validation  

#### `validate.cursor_rules`
**Description**: Validate all Cursor rule files  

#### `validate.file_organization`
**Parameters**: path  
**Description**: Validate file organization compliance  

#### `validate.code_quality`
**Parameters**: file_path  
**Description**: Run comprehensive code quality checks  

---

## 📊 **Tool Statistics**

### Current MCP Tools
- **Database Tools**: 6 tools (IMPLEMENTED ✅)
- **RAG Tools**: 5 tools (EXISTING ✅)
- **Link Integrity Tools**: 5 tools (EXISTING ✅)
- **Software Catalog Tools**: 8 tools (EXISTING ✅)

### Proposed MCP Tools
- **Agile Automation**: 4 tools (HIGH PRIORITY 🔴)
- **Git Tools**: 4 tools (HIGH PRIORITY 🔴)
- **Testing Tools**: 4 tools (MEDIUM PRIORITY 🟡)
- **System Monitoring**: 4 tools (MEDIUM PRIORITY 🟡)
- **Validation Tools**: 4 tools (MEDIUM PRIORITY 🟡)

### Total Tool Count
- **Implemented**: 24 tools ✅
- **Proposed**: 20 tools 📋
- **Target Total**: 44 tools 🎯

---

## 🚀 **Implementation Priority**

### Phase 1: Critical Automation (Sprint 6)
1. ✅ Database Tools (COMPLETE)
2. 🔴 Agile Automation Tools (HIGH PRIORITY)
3. 🔴 Git Tools (HIGH PRIORITY)

### Phase 2: Quality & Testing (Sprint 7)
4. 🟡 Testing Tools
5. 🟡 Validation Tools

### Phase 3: Monitoring & Analytics (Sprint 8)
6. 🟡 System Monitoring Tools
7. 🟡 Analytics Tools

---

## 📖 **Usage Guidelines**

### For Agents
1. **Use MCP tools** instead of direct file/script access
2. **Check tool availability** before execution
3. **Handle errors gracefully** with fallback strategies
4. **Log tool usage** for analytics and debugging

### For Developers
1. **Follow MCP tool standards** when creating new tools
2. **Document all parameters** and return values
3. **Implement access level restrictions** appropriately
4. **Add comprehensive error handling**
5. **Write unit tests** for each tool

### Access Levels
- **UNRESTRICTED**: Safe read-only operations
- **RESTRICTED**: Operations requiring validation
- **ADMIN**: Destructive or sensitive operations

---

## 🔄 **Maintenance**

This catalogue is automatically updated when new MCP tools are added to the system. Last sync: 2025-10-10

**Maintenance Scripts**:
- `scripts/update_mcp_catalogue.py` - Auto-update this catalogue
- `utils/mcp/tools/tool_registry.py` - Central tool registry

**Related Documentation**:
- `docs/mcp/MCP_ARCHITECTURE.md` - MCP system architecture
- `docs/mcp/TOOL_DEVELOPMENT_GUIDE.md` - How to create new tools
- `.cursor/rules/enforcement/AUTOMATION_SCRIPT_ENFORCEMENT_RULE.mdc` - Automation rules

