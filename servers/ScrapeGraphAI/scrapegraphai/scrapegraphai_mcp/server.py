import os
import asyncio
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from scrapegraphai.graphs import SmartScraperGraph

server = Server("scrapegraphai")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="run",
            description="Extract useful information from the webpages. Useful for when you need to scrape a website given an url and a prompt. Input should be a website url a prompt. Output is a JSON object containing the require data extracted from the website.",  # noqa: E501
            inputSchema={
              "type": "object",
              "required": ["prompt"],
              "properties": {
                "type": "object",
                "required": ["prompt", "url"],
                "properties": {
                  "url": {"type": "string"},
                  "prompt": {"type": "string"}
                }
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
    if name != "run": raise ValueError(f"Unknown tool: {name}")
    if not arguments: raise ValueError("Missing arguments")

    prompt = arguments.get("prompt")
    url = arguments.get("url")
    if prompt is None or url is None: raise ValueError("Missing 'prompt' or 'url' in arguments")

    scrapegraph_llm_api_key = os.getenv("SCRAPEGRAPH_LLM_API_KEY")
    if scrapegraph_llm_api_key is None: raise ValueError("Missing 'SCRAPEGRAPH_LLM_API_KEY' in env")
    scrapegraph_llm_model = os.getenv("SCRAPEGRAPH_LLM_MODEL")
    if scrapegraph_llm_api_key is None: raise ValueError("Missing 'SCRAPEGRAPH_LLM_MODEL' in env")

    # Create the SmartScraperGraph instance
    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config={
            "llm": {
                "api_key": scrapegraph_llm_api_key,
                "model": scrapegraph_llm_model,
            },
            "verbose": True,
            "headless": True,
        }
    )
    
    result = await asyncio.to_thread(smart_scraper_graph.run)

    return [types.TextContent(type="text", text=str(result))]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="scrapegraphai",
                server_version="1.36.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
