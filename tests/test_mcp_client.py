import httpx
import pytest

from app.mcp.client import MCPClient, MCPToolExecutionError


@pytest.mark.asyncio
async def test_get_tools_returns_typed_tools() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read().decode()
        if '"method":"initialize"' in payload:
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": "1",
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "serverInfo": {"name": "meridian-test", "version": "1.0.0"},
                    },
                },
            )

        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "2",
                "result": {
                    "tools": [
                        {
                            "name": "search_products",
                            "description": "Search products",
                            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
                            "outputSchema": {"type": "object"},
                        }
                    ]
                },
            },
        )

    client = MCPClient(
        base_url="https://example.test/mcp",
        transport=httpx.MockTransport(handler),
    )

    tools = await client.get_tools()

    assert len(tools) == 1
    assert tools[0].name == "search_products"
    assert tools[0].input_schema["properties"]["query"]["type"] == "string"


@pytest.mark.asyncio
async def test_call_tool_raises_when_server_reports_tool_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read().decode()
        if '"method":"initialize"' in payload:
            return httpx.Response(
                200,
                json={
                    "jsonrpc": "2.0",
                    "id": "1",
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "serverInfo": {"name": "meridian-test", "version": "1.0.0"},
                    },
                },
            )

        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "2",
                "result": {
                    "content": [{"type": "text", "text": "Unknown tool"}],
                    "isError": True,
                },
            },
        )

    client = MCPClient(
        base_url="https://example.test/mcp",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(MCPToolExecutionError, match="Unknown tool"):
        await client.call_tool("missing_tool", {})