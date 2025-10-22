"""
Development Agents Graph for LangGraph Studio.

Provides compiled LangGraph workflows for all development agents.
"""

from typing import TypedDict, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.development.requirements_analyst import RequirementsAnalyst
from agents.development.architecture_designer import ArchitectureDesigner
from agents.development.code_generator import CodeGenerator
from agents.development.code_reviewer import CodeReviewer
from agents.development.test_generator import TestGenerator
from agents.development.documentation_generator import DocumentationGenerator


class DevelopmentAgentState(TypedDict):
    """State for development agent workflows."""
    task_type: Annotated[str, "Type of development task"]
    input_data: Annotated[Dict[str, Any], "Input data for the task"]
    output: Annotated[Dict[str, Any], "Output from the agent"]
    error: Annotated[str, "Error message if any"]


def create_requirements_analyst_graph():
    """Create graph for Requirements Analyst."""
    
    async def analyze_requirements(state: DevelopmentAgentState) -> DevelopmentAgentState:
        agent = RequirementsAnalyst()
        try:
            result = await agent.analyze(state["input_data"])
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state
    
    workflow = StateGraph(DevelopmentAgentState)
    workflow.add_node("analyze", analyze_requirements)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", END)
    
    return workflow.compile(checkpointer=MemorySaver())


def create_architecture_designer_graph():
    """Create graph for Architecture Designer."""
    
    async def design_architecture(state: DevelopmentAgentState) -> DevelopmentAgentState:
        agent = ArchitectureDesigner()
        try:
            result = await agent.design(state["input_data"])
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state
    
    workflow = StateGraph(DevelopmentAgentState)
    workflow.add_node("design", design_architecture)
    workflow.set_entry_point("design")
    workflow.add_edge("design", END)
    
    return workflow.compile(checkpointer=MemorySaver())


def create_code_generator_graph():
    """Create graph for Code Generator."""
    
    async def generate_code(state: DevelopmentAgentState) -> DevelopmentAgentState:
        agent = CodeGenerator()
        try:
            result = await agent.generate(state["input_data"])
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state
    
    workflow = StateGraph(DevelopmentAgentState)
    workflow.add_node("generate", generate_code)
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile(checkpointer=MemorySaver())


def create_code_reviewer_graph():
    """Create graph for Code Reviewer."""
    
    async def review_code(state: DevelopmentAgentState) -> DevelopmentAgentState:
        agent = CodeReviewer()
        try:
            result = await agent.review(state["input_data"])
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state
    
    workflow = StateGraph(DevelopmentAgentState)
    workflow.add_node("review", review_code)
    workflow.set_entry_point("review")
    workflow.add_edge("review", END)
    
    return workflow.compile(checkpointer=MemorySaver())


def create_test_generator_graph():
    """Create graph for Test Generator."""
    
    async def generate_tests(state: DevelopmentAgentState) -> DevelopmentAgentState:
        agent = TestGenerator()
        try:
            result = await agent.generate(state["input_data"])
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state
    
    workflow = StateGraph(DevelopmentAgentState)
    workflow.add_node("generate_tests", generate_tests)
    workflow.set_entry_point("generate_tests")
    workflow.add_edge("generate_tests", END)
    
    return workflow.compile(checkpointer=MemorySaver())


def create_documentation_generator_graph():
    """Create graph for Documentation Generator."""
    
    async def generate_documentation(state: DevelopmentAgentState) -> DevelopmentAgentState:
        agent = DocumentationGenerator()
        try:
            result = await agent.generate(state["input_data"])
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state
    
    workflow = StateGraph(DevelopmentAgentState)
    workflow.add_node("generate_docs", generate_documentation)
    workflow.set_entry_point("generate_docs")
    workflow.add_edge("generate_docs", END)
    
    return workflow.compile(checkpointer=MemorySaver())


# Export all graphs
requirements_analyst = create_requirements_analyst_graph()
architecture_designer = create_architecture_designer_graph()
code_generator = create_code_generator_graph()
code_reviewer = create_code_reviewer_graph()
test_generator = create_test_generator_graph()
documentation_generator = create_documentation_generator_graph()

