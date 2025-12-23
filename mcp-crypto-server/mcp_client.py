# Import necessary libraries
import os
import json
import asyncio
from typing import List, Dict, Any

# MCP libraries for connecting to server
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# OpenAI API 
from openai import AsyncOpenAI

from dotenv import load_dotenv
import os

# Load environment variables and set OpenAI API key
load_dotenv()

# Initialize the OpenAI client
client = AsyncOpenAI(base_url=os.getenv("OPENAI_API_BASE"), api_key=os.getenv("OPENAI_API_KEY"))

# Path to your MCP server
mcp_server_path = "E:\\LLM_IN_ACTION\\Langgraph_in_action\\mcp-crypto-server\\mcp_server.py"
print("Setup complete!")

async def discover_tools():
    """
    Connect to the MCP server and discover available tools.
    Returns information about the available tools.
    """
    # ANSI color codes for better log visibility
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RESET = "\033[0m"
    SEP = "=" * 40
    
    # Create server parameters for connecting to your MCP server through stdio
    server_params = StdioServerParameters(
        command="python",  # Command to run the server
        args=[mcp_server_path],  # Path to your MCP server script
    )
    
    print(f"{BLUE}{SEP}\n🔍 DISCOVERY PHASE: Connecting to MCP server...{RESET}")
    
    # Connect to the server via stdio
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the connection
            print(f"{BLUE}📡 Initializing MCP connection...{RESET}")
            await session.initialize()
            
            # List the available tools
            print(f"{BLUE}🔎 Discovering available tools...{RESET}")
            tools = await session.list_tools()
            
            # Format the tools information for easier viewing
            tool_info = []
            for tool_type, tool_list in tools:
                if tool_type == "tools":
                    for tool in tool_list:
                        tool_info.append({
                            "name": tool.name,
                            "description": tool.description,
                            "schema": tool.inputSchema
                        })
            
            print(f"{GREEN}✅ Successfully discovered {len(tool_info)} tools{RESET}")
            print(f"{SEP}")
            return tool_info
        
async def execute_tool(tool_name: str, arguments: Dict[str, Any]):
    """
    Execute a specific tool provided by the MCP server.
    
    Args:
        tool_name: The name of the tool to execute
        arguments: A dictionary of arguments to pass to the tool
        
    Returns:
        The result from executing the tool
    """
    # ANSI color codes for better log visibility
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    SEP = "-" * 40
    
    server_params = StdioServerParameters(
        command="python",
        args=[mcp_server_path],
    )
    
    print(f"{YELLOW}{SEP}")
    print(f"⚙️ EXECUTION PHASE: Running tool '{tool_name}'")
    print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
    print(f"{SEP}{RESET}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call the specific tool with the provided arguments
            print(f"{BLUE}📡 Sending request to MCP server...{RESET}")
            result = await session.call_tool(tool_name, arguments)
            
            print(f"{GREEN}✅ Tool execution complete{RESET}")
            
            # Format result preview for cleaner output
            result_preview = str(result)
            if len(result_preview) > 150:
                result_preview = result_preview[:147] + "..."
                
            print(f"{BLUE}📊 Result: {result_preview}{RESET}")
            print(f"{SEP}")
            
            return result



async def query_claude(prompt: str, tool_info: List[Dict], previous_messages=None):
    """
    Send a query to Claude and process the response.
    
    Args:
        prompt: User's query
        tool_info: Information about available tools
        previous_messages: Previous messages for maintaining context
        
    Returns:
        Claude's response, potentially after executing tools
    """
    # ANSI color codes for better log visibility
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    PURPLE = "\033[95m"
    RESET = "\033[0m"
    SEP = "=" * 40
    
    if previous_messages is None:
        previous_messages = []
    
    print(f"{PURPLE}{SEP}")
    print("🧠 REASONING PHASE: Processing query with Model")
    print(f"🔤 Query: \"{prompt}\"")
    print(f"{SEP}{RESET}")
    
    # Format tool information for Claude
    tool_descriptions = "\n\n".join([
        f"Tool: {tool['name']}\nDescription: {tool['description']}\nSchema: {json.dumps(tool['schema'], indent=2)}"
        for tool in tool_info
    ])
    
    # Build the system prompt
    system_prompt = f"""You are an AI assistant with access to specialized tools through
      MCP (Model Context Protocol). Available tools:{tool_descriptions}
      When you need to use a tool, respond with a JSON object in the following format:
        {{
            "tool": "tool_name",
            "arguments": {{
                "arg1": "value1",
                "arg2": "value2"
            }}
        }}

        Do not include any other text when using a tool, just the JSON object.
        For regular responses, simply respond normally.
        """
    
    # Filter out system messages from previous messages
    filtered_messages = [msg for msg in previous_messages if msg["role"] != "system"]
    
    # Build the messages for the conversation (WITHOUT system message)
    messages = filtered_messages.copy()
    
    # Add the current user query
    messages.append({"role": "user", "content": prompt})
    
    print(f"{BLUE}📡 Sending request to OpenAI API...{RESET}")
    
    # Send the request to openai model with system as a top-level parameter
    response = await client.chat.completions.create(
        model="Qwen/Qwen3-8B",  # 注意：Qwen 官方兼容名称（需和网关匹配）
        max_tokens=4000,
        messages=[  # system prompt 需合并到 messages 列表中（OpenAI 标准格式）
            {"role": "system", "content": system_prompt},
            *messages  # 合并用户/助手消息
        ]
    )
    
    # Get model's response
    print(f"{BLUE}📡 Received response from OpenAI API{response}{RESET}")
    model_response = response.choices[0].message.content
    print(f"{GREEN}✅ Received response from Model{RESET}")
    
    # Try to extract and parse JSON from the response
    try:
        # Look for JSON pattern in the response
        import re
        json_match = re.search(r'(\{[\s\S]*\})', model_response)
        
        if json_match:
            json_str = json_match.group(1)
            print(f"{YELLOW}🔍 Tool usage detected in response{RESET}")
            print(f"{BLUE}📦 Extracted JSON: {json_str}{RESET}")
            
            tool_request = json.loads(json_str)
            
            if "tool" in tool_request and "arguments" in tool_request:
                tool_name = tool_request["tool"]
                arguments = tool_request["arguments"]
                
                print(f"{YELLOW}🔧 Model wants to use tool: {tool_name}{RESET}")
                
                # Execute the tool using our MCP client
                tool_result = await execute_tool(tool_name, arguments)
                
                # Convert tool result to string if needed
                if not isinstance(tool_result, str):
                    tool_result = str(tool_result)
                
                # Update messages with the tool request and result
                messages.append({"role": "assistant", "content": model_response})
                messages.append({"role": "user", "content": f"Tool result: {tool_result}"})
                
                print(f"{PURPLE}🔄 Getting Model's interpretation of the tool result...{RESET}")
                
                # Get Model's interpretation of the tool result
                final_response = await client.chat.completions.create(
                    model="Qwen/Qwen3-8B",  # 注意：Qwen 官方兼容名称（需和网关匹配）
                    max_tokens=4000,
                    messages=[  # system prompt 需合并到 messages 列表中（OpenAI 标准格式）
                        {"role": "system", "content": system_prompt},
                        *messages  # 合并用户/助手消息
                    ]
                )
                
                print(f"{GREEN}✅ Final response ready{RESET}")
                print(f"{SEP}")
                
                return final_response.choices[0].message.content, messages
        
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        print(f"{YELLOW}⚠️ No tool usage detected in response: {str(e)}{RESET}")
    
    print(f"{GREEN}✅ Response ready{RESET}")
    print(f"{SEP}")
    
    return model_response, messages


# Test the tool discovery function
# 核心修正：用 asyncio.run() 执行异步函数（全局作用域唯一合法方式）
if __name__ == "__main__":  # 推荐加这个，避免导入时执行
    try:
        # Run a single query using the tools from your MCP server
        query = "What is the current price of Bitcoin?"
        print(f"Sending query: {query}")
        tools = asyncio.run(discover_tools())
        response, messages = asyncio.run(query_claude(query, tools))
        print(f"\nAssistant's response:\n{response}")
    except Exception as e:
        print(f"\033[91m❌ Error: {e}\033[0m")