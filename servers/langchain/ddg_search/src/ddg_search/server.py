import asyncio
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun

server = Server("ddg_search")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name=DuckDuckGoSearchRun().name,
            description=DuckDuckGoSearchRun().description,
            inputSchema={
              "type": "object",
              "required": ["query"],
              "properties": {"query": {"type": "string"}}
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
    if not arguments: raise ValueError("Missing arguments")
    if name != DuckDuckGoSearchRun().name: raise ValueError(f"Unknown tool: {name}")
    
    ddg_search_run = DuckDuckGoSearchRun()
    result = await asyncio.to_thread(ddg_search_run.run, arguments)
      
    return [types.TextContent(type="text", text=str(result))]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ddg_search",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
