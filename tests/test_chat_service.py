from types import SimpleNamespace

import pytest
from pydantic import AliasChoices

from app.core.config import Settings
from app.schemas.chat import ToolExecutionEvent
from app.schemas.mcp import MCPTool, MCPToolCallResult
from app.services.chat_service import ChatService
from agents import FunctionTool


class StubMCPClient:
    async def get_tools(self) -> list[MCPTool]:
        return [
            MCPTool.model_validate(
                {
                    "name": "search_products",
                    "description": "Search the catalog.",
                    "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
                    "outputSchema": {"type": "object"},
                }
            )
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> MCPToolCallResult:
        assert tool_name == "search_products"
        assert arguments == {"query": "keyboard", "pin": "1234"}
        return MCPToolCallResult.model_validate(
            {
                "content": [{"type": "text", "text": "Found 2 keyboards."}],
                "isError": False,
            }
        )


@pytest.mark.asyncio
async def test_handle_message_returns_chat_response_and_session_id() -> None:
    service = ChatService(
        settings=Settings(openai_api_key="test-key"),
        mcp_client=StubMCPClient(),
    )

    async def fake_run_agent(agent, agent_input):
        assert "Need a keyboard" in agent_input
        return SimpleNamespace(final_output="Here are two keyboard options.")

    service._run_agent = fake_run_agent  # type: ignore[method-assign]

    response = await service.handle_message("Need a keyboard")

    assert response.message == "Here are two keyboard options."
    assert response.session_id is not None
    assert response.tool_events == []


@pytest.mark.asyncio
async def test_invoke_tool_records_redacted_event() -> None:
    service = ChatService(
        settings=Settings(openai_api_key="test-key"),
        mcp_client=StubMCPClient(),
    )
    tool_events: list[ToolExecutionEvent] = []

    result = await service._invoke_tool(
        tool_name="search_products",
        arguments={"query": "keyboard", "pin": "1234"},
        tool_events=tool_events,
    )

    assert result == "Found 2 keyboards."
    assert len(tool_events) == 1
    assert tool_events[0].status == "completed"
    assert "[REDACTED]" in tool_events[0].summary


def test_dynamic_mcp_tools_disable_strict_schema() -> None:
    service = ChatService(
        settings=Settings(openai_api_key="test-key"),
        mcp_client=StubMCPClient(),
    )
    mcp_tool = MCPTool.model_validate(
        {
            "name": "create_order",
            "description": "Create an order.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sku": {"type": "string"},
                                "quantity": {"type": "integer"},
                            },
                        },
                    },
                },
            },
            "outputSchema": {"type": "object"},
        }
    )

    tool = service._tool_to_function_tool(mcp_tool, [])

    assert isinstance(tool, FunctionTool)
    assert tool.strict_json_schema is False


def test_settings_accept_openai_api_base_url_alias() -> None:
    settings = Settings.model_validate(
        {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_API_BASE_URL": "https://openrouter.ai/api/v1",
        }
    )

    assert settings.openai_base_url == "https://openrouter.ai/api/v1"