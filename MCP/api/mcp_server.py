"""MCP-serveren: åbner værktøjerne op for enhver MCP-klient.

Det er standardstikket i væggen. Claude Desktop, en IDE eller agent-laget
kan sætte sig i det og bruge alle værktøjerne uden at kende koden bag.

Kræver: pip install "mcp>=2"
Kør fra projektets rod:
    python -m MCP.api.mcp_server

Serveren taler over stdin/stdout, så den venter bare stille på en klient.
"""
import asyncio

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from MCP.api.build import build_service
from MCP.config import settings
from MCP.domain.models import ToolCall

service = build_service()


async def list_tools(ctx, params) -> types.ListToolsResult:
    # Oversæt vores mærkater (ToolSpec) til MCP's format.
    tools = [
        types.Tool(name=spec.name, description=spec.description, input_schema=spec.input_schema)
        for spec in service.list_tools()
    ]
    return types.ListToolsResult(tools=tools)


async def call_tool(ctx, params) -> types.CallToolResult:
    # Oversæt MCP's kald til vores ToolCall, og vores ToolResult tilbage igen.
    result = service.call(ToolCall(params.name, params.arguments or {}))
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=result.content)],
        is_error=result.is_error,
    )


server = Server(settings.SERVER_NAME, on_list_tools=list_tools, on_call_tool=call_tool)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
