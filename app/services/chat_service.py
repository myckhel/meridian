from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Any
from uuid import uuid4

from agents import Agent, FunctionTool, Runner, set_default_openai_client, set_tracing_disabled
from agents.run_context import RunContextWrapper
from openai import AsyncOpenAI, AuthenticationError

from app.core.config import Settings, get_settings
from app.mcp.client import MCPClient, MCPClientError, MCPToolExecutionError
from app.schemas.chat import ChatResponse, ToolExecutionEvent
from app.schemas.mcp import MCPTool
from app.services.exceptions import ChatConfigurationError, UpstreamServiceError


@dataclass
class ConversationTurn:
    user_message: str
    assistant_message: str


class ChatService:
    def __init__(self, settings: Settings | None = None, mcp_client: MCPClient | None = None) -> None:
        self.settings = settings or get_settings()
        self.mcp_client = mcp_client or MCPClient(
            base_url=self.settings.mcp_server_url,
            timeout=self.settings.mcp_request_timeout,
        )
        self._session_history: dict[str, list[ConversationTurn]] = {}

    async def handle_message(self, message: str, session_id: str | None = None) -> ChatResponse:
        if not self.settings.openai_api_key:
            raise ChatConfigurationError("OPENAI_API_KEY is not configured.")

        self._configure_model_client()

        current_session_id = session_id or str(uuid4())
        tool_events: list[ToolExecutionEvent] = []

        try:
            tools = await self.mcp_client.get_tools()
            agent = self._build_agent(tools=tools, tool_events=tool_events)
            result = await self._run_agent(
                agent=agent,
                agent_input=self._build_agent_input(message=message, session_id=current_session_id),
            )
        except AuthenticationError as exc:
            raise ChatConfigurationError(
                "Model provider authentication failed. Check OPENAI_API_KEY and OPENAI_BASE_URL or OPENAI_API_BASE_URL."
            ) from exc
        except MCPClientError as exc:
            raise UpstreamServiceError("The MCP server is unavailable right now.") from exc
        except Exception as exc:  # pragma: no cover - SDK failures are integration-level concerns.
            raise UpstreamServiceError("The assistant could not complete this request.") from exc

        assistant_message = self._coerce_output(result.final_output)
        self._append_history(current_session_id, message, assistant_message)
        return ChatResponse(
            message=assistant_message,
            session_id=current_session_id,
            tool_events=tool_events,
        )

    async def _run_agent(self, agent: Agent[Any], agent_input: str) -> Any:
        return await Runner.run(
            agent,
            agent_input,
            max_turns=self.settings.openai_agent_max_turns,
        )

    def _build_agent(self, tools: list[MCPTool], tool_events: list[ToolExecutionEvent]) -> Agent[Any]:
        return Agent(
            name="Meridian Support Assistant",
            model=self.settings.openai_model,
            instructions=self._build_instructions(tools),
            tools=[self._tool_to_function_tool(tool, tool_events) for tool in tools],
        )

    def _build_instructions(self, tools: list[MCPTool]) -> str:
        tool_names = ", ".join(tool.name for tool in tools)
        return (
            "You are Meridian Electronics' customer support assistant. "
            "Use the provided tools whenever the user asks about products, customers, authentication, or orders. "
            "Do not invent inventory, prices, order history, customer records, or order confirmations. "
            "If a request requires missing information such as SKU, customer ID, email, or PIN, ask a concise follow-up question. "
            "Treat order history and order placement as sensitive workflows and verify identity with verify_customer_pin when the user has not already provided enough information in the current request. "
            "After using tools, answer clearly in plain language and mention any blockers. "
            f"Available tools: {tool_names}."
        )

    def _tool_to_function_tool(
        self,
        tool: MCPTool,
        tool_events: list[ToolExecutionEvent],
    ) -> FunctionTool:
        async def invoke_tool(_: RunContextWrapper[Any], arguments_json: str) -> str:
            arguments = json.loads(arguments_json) if arguments_json else {}
            return await self._invoke_tool(tool.name, arguments, tool_events)

        return FunctionTool(
            name=tool.name,
            description=tool.description.strip(),
            params_json_schema=tool.input_schema,
            on_invoke_tool=invoke_tool,
            strict_json_schema=False,
        )

    async def _invoke_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        tool_events: list[ToolExecutionEvent],
    ) -> str:
        started_at = perf_counter()
        safe_arguments = self._redact_arguments(arguments)

        try:
            result = await self.mcp_client.call_tool(tool_name, arguments)
        except MCPToolExecutionError as exc:
            summary = self._build_tool_summary(
                tool_name=tool_name,
                arguments=safe_arguments,
                result_text=str(exc),
                elapsed_seconds=perf_counter() - started_at,
            )
            tool_events.append(ToolExecutionEvent(tool_name=tool_name, status="failed", summary=summary))
            return str(exc)

        summary = self._build_tool_summary(
            tool_name=tool_name,
            arguments=safe_arguments,
            result_text=result.primary_text,
            elapsed_seconds=perf_counter() - started_at,
        )
        tool_events.append(ToolExecutionEvent(tool_name=tool_name, status="completed", summary=summary))
        return result.primary_text or "The tool completed without returning text."

    def _build_agent_input(self, message: str, session_id: str) -> str:
        history = self._session_history.get(session_id, [])
        if not history:
            return message

        recent_turns = history[-self.settings.session_memory_turns :]
        conversation = ["Conversation so far:"]
        for turn in recent_turns:
            conversation.append(f"User: {turn.user_message}")
            conversation.append(f"Assistant: {turn.assistant_message}")
        conversation.append(f"User: {message}")
        return "\n".join(conversation)

    def _append_history(self, session_id: str, user_message: str, assistant_message: str) -> None:
        history = self._session_history.setdefault(session_id, [])
        history.append(ConversationTurn(user_message=user_message, assistant_message=assistant_message))
        if len(history) > self.settings.session_memory_turns:
            del history[:-self.settings.session_memory_turns]

    def _redact_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        redacted_keys = {"password", "pin", "secret", "token"}
        safe_arguments: dict[str, Any] = {}
        for key, value in arguments.items():
            if key.lower() in redacted_keys:
                safe_arguments[key] = "[REDACTED]"
                continue
            safe_arguments[key] = value
        return safe_arguments

    def _build_tool_summary(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result_text: str,
        elapsed_seconds: float,
    ) -> str:
        argument_text = json.dumps(arguments, ensure_ascii=True, sort_keys=True)
        preview = result_text.strip().replace("\n", " ")[:180] or "No text returned."
        return f"{tool_name}({argument_text}) in {elapsed_seconds:.2f}s -> {preview}"

    def _coerce_output(self, output: Any) -> str:
        if isinstance(output, str):
            return output.strip()
        return str(output).strip()

    def _configure_model_client(self) -> None:
        os.environ.setdefault("OPENAI_API_KEY", self.settings.openai_api_key or "")
        if self.settings.openai_base_url:
            os.environ["OPENAI_BASE_URL"] = self.settings.openai_base_url

        client = AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
        )
        set_default_openai_client(client, use_for_tracing=False)
        set_tracing_disabled(bool(self.settings.openai_base_url))