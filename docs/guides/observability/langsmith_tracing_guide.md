# LangSmith Tracing and Observability Guide

This guide explains how to use LangSmith for comprehensive tracing and observability of the AI Development Agent workflow.

## Overview

LangSmith is LangChain's official observability platform that provides detailed tracing, monitoring, and debugging capabilities for AI workflows. The AI Development Agent system is fully integrated with LangSmith for comprehensive workflow observability.

## 🌐 LangSmith Dashboard

**View all agent logs, workflow traces, and LLM calls at:**

**🔗 [https://smith.langchain.com/](https://smith.langchain.com/)**

## What You Can Monitor

### Agent Executions
- **Input/Output Data**: Complete agent input and output for each execution
- **Execution Time**: Performance metrics for each agent
- **Success/Failure Status**: Agent execution results and error details
- **Session Tracking**: Complete session history across all agents

### Workflow Steps
- **State Changes**: Complete workflow state progression
- **Agent Transitions**: How data flows between agents
- **Error Propagation**: How errors affect the workflow
- **Performance Metrics**: Overall workflow performance

### LLM Calls
- **Prompt/Response Pairs**: Complete LLM interactions
- **Model Performance**: Response times and quality metrics
- **Token Usage**: Cost and efficiency tracking
- **Model Selection**: Which models are used for different tasks

### Error Tracking
- **Error Context**: Detailed error information with context
- **Stack Traces**: Complete error propagation paths
- **Recovery Attempts**: Retry logic and fallback mechanisms
- **Error Patterns**: Identification of recurring issues

## Configuration

### Setup in `.streamlit/secrets.toml`

```toml
# LangSmith Configuration
LANGSMITH_TRACING = "true"
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_API_KEY = "your-langsmith-api-key"
LANGSMITH_PROJECT = "ai-dev-agent"
```

### Getting Your LangSmith API Key

1. Visit [https://smith.langchain.com/](https://smith.langchain.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" in your settings
4. Create a new API key
5. Add it to your `.streamlit/secrets.toml` file

## Workflow Tracing Details

### Session-Based Tracing

Each workflow execution creates a unique session with:
- **Session ID**: Unique identifier for the entire workflow
- **Project Context**: The original project description
- **Agent Sequence**: Complete sequence of agent executions
- **Timeline**: Chronological execution timeline

### Agent-Level Tracing

Each agent execution is traced with:
- **Agent Name**: Which agent is executing
- **Input Data**: Complete input state and context
- **Output Data**: Agent's complete output
- **Execution Time**: Performance metrics
- **Error Details**: Any failures or issues

### LLM Call Tracing

Individual LLM calls are traced with:
- **Model Used**: Which Gemini model was selected
- **Prompt Content**: Complete prompt sent to the model
- **Response Content**: Complete response received
- **Token Usage**: Input/output token counts
- **Response Time**: How long the call took

## Using LangSmith Dashboard

### Project Organization

The system creates multiple projects in LangSmith:
- **`ai-dev-agent-agents`**: Individual agent executions
- **`ai-dev-agent-workflow`**: Complete workflow steps
- **`ai-dev-agent-llm`**: Individual LLM calls
- **`ai-dev-agent-errors`**: Error tracking and debugging
- **`ai-dev-agent-metrics`**: Performance metrics

### Dashboard Features

#### Run Explorer
- **Filter by Agent**: View executions for specific agents
- **Filter by Status**: Success, failure, or in-progress runs
- **Filter by Time**: Recent executions or specific time ranges
- **Search**: Find specific runs by content or metadata

#### Trace View
- **Complete Workflow**: See the entire agent sequence
- **State Changes**: How data flows between agents
- **Error Points**: Where failures occur in the workflow
- **Performance Bottlenecks**: Identify slow agents or LLM calls

#### Prompt Management
- **Prompt Versioning**: Track prompt changes over time
- **Performance Comparison**: Compare prompt effectiveness
- **A/B Testing**: Test different prompt variations
- **Optimization**: Identify opportunities for prompt improvement

## Debugging with LangSmith

### Error Investigation

1. **Find the Error**: Use the error project to locate failed runs
2. **Trace the Error**: Follow the error through the workflow
3. **Context Analysis**: Examine the state when the error occurred
4. **Root Cause**: Identify the underlying cause of the failure

### Performance Optimization

1. **Identify Bottlenecks**: Find slow agents or LLM calls
2. **Token Usage Analysis**: Optimize for cost and efficiency
3. **Model Selection**: Compare performance across different models
4. **Prompt Optimization**: Improve prompt effectiveness

### Workflow Analysis

1. **Agent Effectiveness**: Which agents are most successful
2. **Data Flow**: How information flows between agents
3. **State Management**: How workflow state evolves
4. **Error Patterns**: Common failure points and patterns

## Integration with Development

### Local Development

When running locally, all traces are automatically sent to LangSmith:
- **Real-time Monitoring**: See traces as they happen
- **Debugging Support**: Use traces for debugging issues
- **Performance Tracking**: Monitor local development performance

### Production Deployment

For production deployments:
- **Environment Separation**: Separate projects for different environments
- **Performance Monitoring**: Track production performance
- **Error Alerting**: Set up alerts for critical failures
- **Usage Analytics**: Monitor system usage and patterns

## Best Practices

### Effective Tracing

1. **Meaningful Names**: Use descriptive names for runs and sessions
2. **Rich Metadata**: Include relevant context in metadata
3. **Consistent Tagging**: Use consistent tags for categorization
4. **Error Context**: Include sufficient context for error debugging

### Performance Monitoring

1. **Regular Review**: Regularly review performance metrics
2. **Trend Analysis**: Track performance trends over time
3. **Alert Setup**: Set up alerts for performance degradation
4. **Optimization**: Continuously optimize based on metrics

### Debugging Workflow

1. **Start with Errors**: Begin debugging by examining error traces
2. **Follow the Data**: Trace data flow through the workflow
3. **Check Context**: Examine the context when issues occur
4. **Test Hypotheses**: Use traces to test debugging hypotheses

## Troubleshooting

### Common Issues

#### No Traces Appearing
- Check that `LANGSMITH_API_KEY` is set correctly
- Verify `LANGSMITH_TRACING` is set to "true"
- Ensure the LangSmith endpoint is accessible

#### Missing Agent Traces
- Verify that agents are using the LangChain logging manager
- Check that session IDs are being passed correctly
- Ensure callback managers are properly configured

#### Performance Issues
- Check for network connectivity to LangSmith
- Verify that tracing isn't causing performance degradation
- Consider reducing trace detail for high-volume operations

### Getting Help

- **LangSmith Documentation**: [https://docs.smith.langchain.com/](https://docs.smith.langchain.com/)
- **LangSmith Community**: Join the LangSmith Discord for support
- **Project Issues**: Report LangSmith integration issues in the project repository

## Benefits

### For Developers
- **Comprehensive Debugging**: Complete visibility into workflow execution
- **Performance Optimization**: Identify and fix performance bottlenecks
- **Error Resolution**: Quickly identify and resolve issues
- **Workflow Understanding**: Better understanding of agent interactions

### For Users
- **Reliability**: Better error handling and debugging capabilities
- **Performance**: Optimized workflows through performance analysis
- **Transparency**: Complete visibility into how the system works
- **Quality**: Improved system quality through better monitoring

### For the Project
- **Quality Assurance**: Better testing and validation capabilities
- **Continuous Improvement**: Data-driven optimization opportunities
- **Documentation**: Automatic documentation of workflow behavior
- **Collaboration**: Better collaboration through shared observability

## Conclusion

LangSmith provides comprehensive observability for the AI Development Agent workflow, enabling better debugging, performance optimization, and system understanding. By leveraging LangSmith's powerful tracing capabilities, developers can build more reliable and efficient AI workflows.

Visit [https://smith.langchain.com/](https://smith.langchain.com/) to start exploring your workflow traces and gain deeper insights into your AI agent system.
