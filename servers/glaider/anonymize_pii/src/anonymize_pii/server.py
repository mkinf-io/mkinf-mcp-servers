import os
import json
import mcp.server.stdio
import mcp.types as types
import requests
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("anonymize_pii")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="anonymize",
            description="A wrapper around glaider anonymization API. Useful for when you need to anonymize personally identifiable information (PII) in text data before processing it with AI models or storing it. The service automatically detects and anonymizes sensitive information such as personal names, locations, organizations, email addresses, IP addresses, access tokens, API keys, credit card numbers, and more. Input should be a prompt. Output is a JSON object containing the anonymized prompt (anonymized_text) and the key value anonymized entities (entities).",  # noqa: E501
            inputSchema={
                "type": "object",
                "required": ["prompt"],
                "properties": {"prompt": {"type": "string"}},
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
    if name != "anonymize":
        raise ValueError(f"Unknown tool: {name}")
    if not arguments:
        raise ValueError("Missing arguments")

    prompt = arguments.get("prompt")
    if prompt is None:
        raise ValueError("Missing 'prompt' in arguments")

    glaider_api_key = os.getenv("GLAIDER_API_KEY")
    if glaider_api_key is None:
        raise ValueError("Missing 'GLAIDER_API_KEY' in env")

    response = requests.post(
        "https://api.glaider.it/v1/anonymize-pii",
        headers={"Authorization": glaider_api_key, "Content-Type": "application/json"},
        json={"prompt": prompt},
    )
    response.raise_for_status()
    result = response.json()

    return [types.TextContent(type="text", text=json.dumps(result))]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="anonymize_pii",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
