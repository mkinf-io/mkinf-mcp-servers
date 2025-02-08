import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from langchain_community.tools.bing_search import BingSearchRun, BingSearchResults
from langchain_community.utilities.bing_search import BingSearchAPIWrapper

server = Server("bing_search")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name=BingSearchRun.name,
            description=BingSearchRun.description,
            inputSchema={
              "type": "object",
              "required": ["query"],
              "properties": {"query": {"type": "string"}}
            },
        ),
        types.Tool(
            name=BingSearchResults.name,
            description=BingSearchResults.description,
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
    if name == BingSearchRun.name:
      result = BingSearchRun(BingSearchAPIWrapper()).run(arguments)
    elif name == BingSearchResults.name:
      result = BingSearchResults(BingSearchAPIWrapper()).run(arguments)
    else:
      raise ValueError(f"Unknown tool: {name}")
    return [types.TextContent(type="text", text=result)]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bing_search",
                server_version="1.36.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
