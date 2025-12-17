# Wrap the code in an async function
import asyncio

async def main():
    from langchain_mcp_adapters.client import MultiServerMCPClient  
    from deepagents import create_deep_agent
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    client = MultiServerMCPClient(  
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["C:\\Users\\pogawal\\WorkFolder\\Documents\\Python\\ai-dev-agent\\utils\\mcp\\fastmcp\\math_server.py"],
            },
            # "weather": {
            #     "transport": "streamable_http",
            #     "url": "http://localhost:8000/mcp",
            # },
            # "fastmcp": {
            #     "transport": "streamable_http",
            #     "url": "https://gofastmcp.com/mcp",                
            # },
        }
    )

    tools = await client.get_tools()  
    agent = create_deep_agent(model=llm, tools=tools)
    
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print(math_response)
    
    last_message = math_response['messages'][-1]
    
    # weather_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "what is the weather in Sao Paulo, Brazil?"}]}
    # )
    # print(weather_response)
    
    # last_message = weather_response['messages'][-1]
    # fastmcp_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "Describe what is fastmcp?"}]}
    # )
    # print(fastmcp_response)
    
    # last_message = fastmcp_response['messages'][-1]
    
    print("--------------------------------")
    print(last_message)
    
if __name__ == "__main__":
    asyncio.run(main())