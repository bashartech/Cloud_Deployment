---
name: mcp-server-tools-for-openai-agents
description: Guide for setting up MCP (Model Context Protocol) servers with tools that can be accessed by OpenAI Agent SDK agents. This skill explains how to create MCP servers with custom tools and connect them to agents for enhanced functionality.
---

# MCP Server Tools for OpenAI Agent SDK

## Overview

This skill provides guidance for creating Model Context Protocol (MCP) servers with custom tools that can be accessed by OpenAI Agent SDK agents. MCP servers allow you to extend agent capabilities by providing external tools and prompts that agents can use during their operation.

## When to Use This Skill

Use this skill when you want to:
- Create custom tools for your agents to access external services
- Extend agent capabilities beyond their native LLM functions
- Share tools across multiple agents
- Provide agents with access to internal systems, databases, or APIs
- Implement reusable prompt templates for agents

## Prerequisites

- Python 3.11 or higher
- `mcp` package (version 1.21.0 or higher)
- `openai-agents` package (version 0.5.0 or higher)
- An LLM service (OpenAI, Gemini, or similar)

## Setting Up an MCP Server

### 1. Basic MCP Server Structure

```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("YourServerName", stateless_http=True)

# Define tools using the @mcp.tool decorator
@mcp.tool(name="tool_name", description="Description of what the tool does")
def your_tool_function(param1: str = "default_value") -> str:
    """Brief description of the function."""
    # Your tool implementation
    result = f"Processing with param1: {param1}"
    return result

# Define prompts using the @mcp.prompt decorator
@mcp.prompt(name="prompt_name")
def your_prompt_function(user_name: str):
    return f"You are an agent that helps {user_name} with specific tasks"

# Export the app for Uvicorn
mcp_app = mcp.streamable_http_app()
```

### 2. Creating Custom Tools

Tools are functions decorated with `@mcp.tool` that can be called by agents. They should:

- Have clear, descriptive names
- Include comprehensive descriptions
- Use type hints for parameters
- Return appropriate data types (str, dict, list, etc.)

Example with multiple tools:

```python
@mcp.tool(name="get_weather", description="Get current weather information for a specified location.")
def get_weather(location: str) -> str:
    """Get weather for the specified location."""
    # In a real implementation, you would call a weather API
    return f"The weather in {location} is sunny with a temperature of 72°F."

@mcp.tool(name="calculate_distance", description="Calculate the distance between two locations.")
def calculate_distance(origin: str, destination: str) -> str:
    """Calculate distance between origin and destination."""
    # In a real implementation, you would calculate the distance
    return f"The distance between {origin} and {destination} is 150 miles."
```

### 3. Creating Custom Prompts

Prompts define the agent's behavior and can be customized with parameters:

```python
@mcp.prompt(name="personal_assistant")
def personal_assistant(user_name: str, context: str = "general"):
    """Generate a personalized assistant prompt."""
    if context == "work":
        return f"You are a professional assistant helping {user_name} with work-related tasks. Provide concise, business-focused responses."
    else:
        return f"You are a helpful assistant for {user_name}. Provide friendly and informative responses for {context} topics."
```

## Connecting MCP Server to OpenAI Agent SDK

### 1. Basic Agent Configuration

```python
import os, asyncio
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

_: bool = load_dotenv(find_dotenv())

# Configure LLM client
external_client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://your-llm-provider/v1/"
)

# Configure LLM model
llm_model = OpenAIChatCompletionsModel(
    model="your-model-name",
    openai_client=external_client
)
```

### 2. Connecting to MCP Server

```python
async def main():
    # Configure MCP server connection
    params_config = MCPServerStreamableHttpParams(url="http://localhost:8000/mcp/")

    async with MCPServerStreamableHttp(
        params=params_config,
        name="MySharedMCPServerClient",
    ) as mcp_server:

        # List available prompts from the server
        prompts = await mcp_server.list_prompts()
        print("Available prompts:", prompts)

        # Get a specific prompt with arguments
        greeting_prompt = await mcp_server.get_prompt("personal_assistant", arguments={
            "user_name": "John Doe",
            "context": "work"
        })

        # List available tools from the server
        tools = await mcp_server.list_tools()
        print("Available tools:", tools)

        # Create agent with MCP server integration
        base_agent = Agent(
            name="EnhancedAgent",
            instructions=greeting_prompt.messages[0].content.text,
            model=llm_model,
            mcp_servers=[mcp_server]
        )

        # Run the agent with MCP tools available
        result = await Runner.run(base_agent, "What's the weather like today?")
        print(result.final_output)
```

## Tool Filtering and Security

### Static Tool Filtering

You can restrict which tools are available to agents using static filters:

```python
from agents.mcp import create_static_tool_filter

# Block specific tools
static_filter = create_static_tool_filter(blocked_tool_names=["sensitive_tool"])

# Or allow only specific tools
static_filter = create_static_tool_filter(allowed_tool_names=["get_weather", "calculate_distance"])

# Apply filter when connecting to MCP server
async with MCPServerStreamableHttp(
    params=params_config,
    name="MySharedMCPServerClient",
    tool_filter=static_filter
) as mcp_server:
    # ... rest of configuration
```

### Dynamic Tool Filtering

For more complex filtering logic, use dynamic filtering:

```python
async def dynamic_tool_filter(context, tool):
    """Custom logic to determine if a tool should be available."""
    print("Context:", context)
    print("Tool:", tool)

    # Example: Only allow tools that start with specific prefixes
    allowed_prefixes = ["get_", "calculate_"]
    return any(tool.name.startswith(prefix) for prefix in allowed_prefixes)

# Apply dynamic filter
async with MCPServerStreamableHttp(
    params=params_config,
    name="MySharedMCPServerClient",
    tool_filter=dynamic_tool_filter
) as mcp_server:
    # ... rest of configuration
```

## Running the MCP Server

### Starting the Server

Save your MCP server code (e.g., as `mcp_server.py`) and start it with Uvicorn:

```bash
uvicorn mcp_server:mcp_app --port 8000
```

The server will be available at `http://localhost:8000/mcp/` by default.

### Complete Example

Here's a complete MCP server example:

```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ExampleServer", stateless_http=True)

# Define multiple tools
@mcp.tool(name="greet_user", description="Return a personalized greeting.")
def greet_user(name: str = "World") -> str:
    """Greet the user."""
    return f"Hello {name}! Welcome to our service."

@mcp.tool(name="get_current_mood", description="Return a positive mood message.")
def get_mood(name: str = "User") -> str:
    """Get current mood."""
    return f"{name}, I'm happy to assist you today! 😊"

@mcp.tool(name="get_date_info", description="Get current date information.")
def get_date_info() -> str:
    """Get current date."""
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Current date and time: {current_date}"

# Define prompts
@mcp.prompt(name="general_assistant")
def general_assistant(user_name: str):
    return f"You are a helpful assistant for {user_name}. Provide friendly and informative responses."

# Export for Uvicorn
mcp_app = mcp.streamable_http_app()
```

## Best Practices

### 1. Tool Design
- Use descriptive names that clearly indicate what the tool does
- Include comprehensive descriptions that agents can understand
- Use appropriate type hints for all parameters
- Handle errors gracefully and return meaningful error messages
- Keep tool functionality focused and single-purpose

### 2. Security Considerations
- Validate all input parameters to prevent injection attacks
- Implement proper authentication if needed
- Use tool filtering to restrict access to sensitive functions
- Log tool usage for monitoring and debugging

### 3. Performance
- Make tools efficient and fast to avoid blocking agent responses
- Consider caching results for expensive operations
- Use async functions when appropriate for I/O operations

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the MCP server is running and accessible at the specified URL
2. **Tool Not Found**: Verify the tool name matches exactly what's defined in the MCP server
3. **Parameter Mismatch**: Check that parameters passed to tools match the expected types
4. **Authentication Issues**: Verify API keys and authentication headers if required

### Debugging Tips

- Enable logging to see detailed information about tool calls
- Test tools directly with the MCP server before integrating with agents
- Check the server logs for any error messages
- Verify network connectivity between agent and server

## References

- [MCP Documentation](https://modelcontextprotocol.ai/)
- [OpenAI Agent SDK Documentation](https://github.com/openai/openai-agents)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/fastmcp)