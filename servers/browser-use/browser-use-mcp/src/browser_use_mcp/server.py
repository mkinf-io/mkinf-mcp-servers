import traceback
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from pydantic import SecretStr
from enum import Enum
from environs import env


server = Server("gitingest")

class ServerTools(str, Enum):
  RUN_TASK = "run_task"

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name=ServerTools.RUN_TASK.value,
            description="Executes a specified task within a browser session. Returns the actions performed during the session.",  # noqa: E501
            inputSchema={
              "type": "object",
              "required": ["task"],
              "properties": {
                "task": {"type": "string"},
                "max_steps": {"type": "number"},
              }
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name != ServerTools.RUN_TASK.value: raise ValueError(f"Unknown tool: {name}")
    # LLM
    llm_model = env.str("LLM_MODEL", "gpt-4o-mini")
    llm_api_key = env.str("LLM_API_KEY")
    headless = env.bool("HEADLESS", True)
    if not llm_api_key: raise ValueError("Missing LLM API key")
    
    # Arguments
    if not arguments: raise ValueError("Missing arguments")
    max_steps = int(arguments.get("max_steps", 10))
    task = arguments.get("task")
    if not task: raise ValueError("Missing task")

    try:
        browser = Browser(config=BrowserConfig(headless=headless))
        model = ChatOpenAI(model=llm_model, api_key=SecretStr(llm_api_key), temperature=0.7)
        agent = Agent(
            task=task,
            llm=model,
            browser=browser
        )
        await agent.run(max_steps=max_steps)
        await browser.close()
    except Exception as e:
        traceback.print_exc()
        print(e)
        raise ValueError(f"Error processing task: {str(e)}")

    return [types.TextContent(type="text", text=agent.history.model_dump_json())]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-use-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
