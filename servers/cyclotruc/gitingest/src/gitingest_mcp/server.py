import json
from gitingest import ingest
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("gitingest")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="ingest",
            description="Turns any Git repository into a prompt-friendly text ingest for LLMs. Useful for when you need to access git repositories summary, directory structure and files content. Input should be a git repository url. Output is a JSON object containing: the repository summary (summary): repository name, files analyzed, estimated tokens; the directory structure (tree); the files content (content).",  # noqa: E501
            inputSchema={
              "type": "object",
              "required": ["url"],
              "properties": {"url": {"type": "string"}}
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
    if name != "ingest":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    url = arguments.get("url")

    if url is None:
        raise ValueError("Missing 'url' in arguments")

    summary, tree, content = ingest(url)

    return [types.TextContent(type="text", text=json.dumps({
        "summary": summary,
        "tree": tree,
        "content": content
    }))]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gitingest",
                server_version="0.1.2",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
