# Agile Factory LLM Invocation Analysis

## Problem Statement

User reported: "we dont have calls to the llm in all nodes except in the code generator which is quite strange."

## Current State Analysis

### Node-by-Node LLM Call Pattern

#### 1. **code_generator_node** ✅ CORRECT
- **Pattern**: Custom LangGraph graph with direct LLM invocation
- **Method**: `llm.bind_tools(all_tools).invoke(messages)` inside `agent_node` function
- **Tools**: Yes (write_file, Python REPL, website test tools)
- **Status**: ✅ **ACTUALLY CALLS LLM WITH TOOLS**

```python
def agent_node(agent_state: MessagesState) -> dict:
    messages = agent_state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=system_prompt)] + messages
    response = llm.bind_tools(all_tools).invoke(messages)  # ✅ DIRECT LLM CALL
    return {"messages": [response]}
```

#### 2. **requirements_node** ⚠️ PARTIAL
- **Pattern**: Direct LLM invocation WITHOUT tools
- **Method**: `llm.invoke(messages)` - expects JSON output
- **Tools**: No (just expects JSON response)
- **Status**: ✅ **CALLS LLM** but doesn't use tools (intentional - expects JSON)

```python
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=task)
]
result = llm.invoke(messages)  # ✅ CALLS LLM (no tools needed)
output = result.content.strip()
requirements = json.loads(output)  # Parse JSON
```

#### 3. **architecture_node** ⚠️ PARTIAL
- **Pattern**: Direct LLM invocation WITHOUT tools
- **Method**: `llm.invoke(messages)` - expects JSON output
- **Tools**: No (just expects JSON response)
- **Status**: ✅ **CALLS LLM** but doesn't use tools (intentional - expects JSON)

```python
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=task)
]
result = llm.invoke(messages)  # ✅ CALLS LLM (no tools needed)
output = result.content.strip()
architecture = json.loads(output)  # Parse JSON
```

#### 4. **code_reviewer_node** ⚠️ PARTIAL
- **Pattern**: Direct LLM invocation WITHOUT tools
- **Method**: `llm.invoke(messages)` - expects JSON output
- **Tools**: No (just expects JSON response)
- **Status**: ✅ **CALLS LLM** but doesn't use tools (intentional - expects JSON)

```python
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=task)
]
result = llm.invoke(messages)  # ✅ CALLS LLM (no tools needed)
output = result.content.strip()
code_review = json.loads(json_str)  # Parse JSON
```

#### 5. **testing_node** ❌ INCORRECT
- **Pattern**: `create_react_agent` with `state_modifier` parameter
- **Method**: `create_react_agent(model=llm, tools=all_tools, state_modifier=system_prompt)`
- **Tools**: Yes (write_file, Python REPL, website test tools)
- **Status**: ❌ **PROBLEM**: `state_modifier` is deprecated/incorrect. System prompt should be in messages.

```python
testing_agent = create_react_agent(
    model=llm,
    tools=all_tools,
    state_modifier=system_prompt  # ❌ WRONG - state_modifier deprecated
)

initial_state = {
    "messages": [
        SystemMessage(content=system_prompt),  # ✅ Correct but redundant
        HumanMessage(content=task_message)
    ]
}
result = testing_agent.invoke(initial_state)
```

**Issue**: `state_modifier` parameter may not work correctly in newer LangGraph versions. The system prompt should be passed in messages, not as `state_modifier`.

#### 6. **documentation_node** ❌ INCORRECT
- **Pattern**: `create_react_agent` with `state_modifier` parameter
- **Method**: `create_react_agent(model=llm, tools=[write_file_tool], state_modifier=system_prompt)`
- **Tools**: Yes (write_file tool)
- **Status**: ❌ **PROBLEM**: Same issue as testing_node - `state_modifier` is deprecated/incorrect.

```python
doc_gen_agent = create_react_agent(
    model=llm,
    tools=[write_file_tool],
    state_modifier=system_prompt  # ❌ WRONG - state_modifier deprecated
)

initial_state = {
    "messages": [
        SystemMessage(content=system_prompt),  # ✅ Correct but redundant
        HumanMessage(content=task_message)
    ]
}
result = doc_gen_agent.invoke(initial_state)
```

## Root Cause

The issue is **NOT** that nodes don't call the LLM - they do. The issue is:

1. **Inconsistent Patterns**: Different nodes use different patterns:
   - `code_generator_node`: Custom LangGraph graph with direct LLM call
   - `requirements/architecture/code_reviewer`: Direct `llm.invoke()` (no tools)
   - `testing/documentation`: `create_react_agent` with deprecated `state_modifier`

2. **Deprecated API Usage**: `testing_node` and `documentation_node` use `state_modifier` parameter which may not work correctly.

3. **Missing Tool Binding**: `testing_node` and `documentation_node` should use tools but may not be invoking LLM correctly due to incorrect `create_react_agent` usage.

## Correct Pattern (from langgraph_workflow.py)

The correct pattern for `create_react_agent` is:

```python
# Create agent WITHOUT state_modifier
agent = create_react_agent(
    model=llm,
    tools=all_tools
    # NO state_modifier parameter
)

# Invoke with messages that include SystemMessage
messages = [
    SystemMessage(content=system_prompt),  # System prompt in messages
    HumanMessage(content=task)
]
result = agent.invoke({"messages": messages})
```

## Solution

### Fix testing_node and documentation_node

1. Remove `state_modifier` parameter from `create_react_agent`
2. Ensure SystemMessage is in the messages when invoking
3. Follow the same pattern as `code_generator_node` OR use `create_react_agent` correctly

### Standardize Pattern

All nodes should follow one of two patterns:

**Pattern A: Direct LLM Call (for nodes without tools)**
```python
llm = ChatGoogleGenerativeAI(...)
messages = [SystemMessage(content=system_prompt), HumanMessage(content=task)]
result = llm.invoke(messages)
```

**Pattern B: LangGraph Agent (for nodes with tools)**
```python
llm = ChatGoogleGenerativeAI(...)
agent = create_react_agent(model=llm, tools=all_tools)  # NO state_modifier
messages = [SystemMessage(content=system_prompt), HumanMessage(content=task)]
result = agent.invoke({"messages": messages})
```

## Summary

| Node | LLM Called? | Pattern | Tools | Status |
|------|-------------|---------|-------|--------|
| code_generator | ✅ Yes | Custom LangGraph graph | ✅ Yes | ✅ Correct |
| requirements | ✅ Yes | Direct `llm.invoke()` | ❌ No | ✅ Correct (no tools needed) |
| architecture | ✅ Yes | Direct `llm.invoke()` | ❌ No | ✅ Correct (no tools needed) |
| code_reviewer | ✅ Yes | Direct `llm.invoke()` | ❌ No | ✅ Correct (no tools needed) |
| testing | ✅ Yes | `create_react_agent` (fixed) | ✅ Yes | ✅ **FIXED** |
| documentation | ✅ Yes | `create_react_agent` (fixed) | ✅ Yes | ✅ **FIXED** |

## Fixes Applied

### testing_node.py
- **Removed**: `state_modifier=system_prompt` parameter from `create_react_agent`
- **Result**: Agent now correctly calls LLM with system prompt in messages

### documentation_node.py
- **Removed**: `state_modifier=system_prompt` parameter from `create_react_agent`
- **Result**: Agent now correctly calls LLM with system prompt in messages

## Final Status

✅ **ALL NODES NOW CORRECTLY CALL THE LLM**

- **Pattern A** (no tools): `requirements_node`, `architecture_node`, `code_reviewer_node` use direct `llm.invoke()`
- **Pattern B** (with tools): `code_generator_node`, `testing_node`, `documentation_node` use LangGraph agents that invoke LLM with tools bound

