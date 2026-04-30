from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx

from app.schemas.mcp import MCPInitializeResult, MCPTool, MCPToolCallResult


class MCPClientError(Exception):
    pass


class MCPTransportError(MCPClientError):
    pass


class MCPProtocolError(MCPClientError):
    pass


class MCPToolExecutionError(MCPClientError):
    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(message)
        self.tool_name = tool_name


class MCPClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.transport = transport
        self._initialized = False
        self._tools_cache: list[MCPTool] | None = None

    async def initialize(self) -> MCPInitializeResult:
        payload = await self._send_request(
            method="initialize",
            params={
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "meridian-api", "version": "0.1.0"},
            },
        )
        result = MCPInitializeResult.model_validate(payload)
        self._initialized = True
        return result

    async def get_tools(self, refresh: bool = False) -> list[MCPTool]:
        await self._ensure_initialized()
        if self._tools_cache is not None and not refresh:
            return self._tools_cache

        payload = await self._send_request(method="tools/list", params={})
        tools = [MCPTool.model_validate(item) for item in payload.get("tools", [])]
        self._tools_cache = tools
        return tools

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPToolCallResult:
        await self._ensure_initialized()
        payload = await self._send_request(
            method="tools/call",
            params={"name": tool_name, "arguments": arguments},
        )
        result = MCPToolCallResult.model_validate(payload)
        if result.is_error:
            raise MCPToolExecutionError(tool_name=tool_name, message=result.primary_text or "Tool execution failed.")
        return result

    async def _ensure_initialized(self) -> None:
        if not self._initialized:
            await self.initialize()

    async def _send_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": method,
            "params": params,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                transport=self.transport,
                headers={
                    "accept": "application/json, text/event-stream",
                    "content-type": "application/json",
                },
            ) as client:
                response = await client.post(self.base_url, json=request_payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MCPTransportError("Unable to reach the MCP server.") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise MCPProtocolError("The MCP server returned invalid JSON.") from exc

        error = payload.get("error")
        if error:
            message = error.get("message", "MCP request failed.")
            raise MCPProtocolError(message)

        result = payload.get("result")
        if not isinstance(result, dict):
            raise MCPProtocolError("The MCP server returned an unexpected payload.")

        return result