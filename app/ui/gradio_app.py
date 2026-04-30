from __future__ import annotations

import asyncio
from uuid import uuid4

import gradio as gr
import httpx

from app.core.config import get_settings
from app.services.chat_service import ChatService


settings = get_settings()
chat_service = ChatService(settings=settings)


def _normalize_history(history: list[dict] | None) -> list[dict]:
    if not history:
        return []

    normalized_history: list[dict] = []
    for entry in history:
        if not isinstance(entry, dict):
            continue

        role = entry.get("role")
        content = entry.get("content")
        if role in {"user", "assistant", "system"} and isinstance(content, str):
            normalized_history.append({"role": role, "content": content})

    return normalized_history


def _respond_via_local_service(message: str, session_id: str) -> tuple[str, str]:
    payload = asyncio.run(chat_service.handle_message(message, session_id))
    return payload.message, payload.session_id or session_id


def respond(message: str, history: list[dict], session_id: str | None) -> tuple[str, str]:
    current_session_id = session_id or str(uuid4())

    try:
        response = httpx.post(
            settings.chat_api_url,
            json={"message": message, "session_id": current_session_id},
            timeout=settings.mcp_request_timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        detail = "The backend request failed."
        try:
            payload = exc.response.json()
            detail = payload.get("detail", detail)
        except ValueError:
            pass
        return f"Request failed: {detail}", current_session_id
    except httpx.HTTPError:
        try:
            return _respond_via_local_service(message, current_session_id)
        except Exception:
            return "Request failed: Unable to reach the FastAPI backend.", current_session_id

    return payload["message"], payload.get("session_id", current_session_id)


def submit_message(
    message: str,
    history: list[dict] | None,
    session_id: str | None,
) -> tuple[str, list[dict], str]:
    cleaned_message = message.strip()
    normalized_history = _normalize_history(history)
    current_session_id = session_id or str(uuid4())

    if not cleaned_message:
        return "", normalized_history, current_session_id

    answer, updated_session_id = respond(cleaned_message, normalized_history, current_session_id)
    updated_history = [
        *normalized_history,
        {"role": "user", "content": cleaned_message},
        {"role": "assistant", "content": answer},
    ]
    return "", updated_history, updated_session_id


def reset_chat() -> tuple[str, list[dict], str]:
    return "", [], str(uuid4())


with gr.Blocks(title="Meridian Support Demo") as demo:
    session_state = gr.State(value=str(uuid4()))
    gr.Markdown("# Meridian Support Demo")
    gr.Markdown("Chat with the Meridian Agent Support.")
    chatbot = gr.Chatbot(type="messages", label="Meridian Assistant")
    with gr.Row():
        message_input = gr.Textbox(
            label="Message",
            placeholder="Ask about inventory, orders, or support.",
            scale=8,
        )
        send_button = gr.Button("Send", variant="primary", scale=1)
    clear_button = gr.Button("Clear chat")

    event_inputs = [message_input, chatbot, session_state]
    event_outputs = [message_input, chatbot, session_state]

    message_input.submit(
        submit_message,
        inputs=event_inputs,
        outputs=event_outputs,
    )
    send_button.click(
        submit_message,
        inputs=event_inputs,
        outputs=event_outputs,
    )
    clear_button.click(
        reset_chat,
        outputs=event_outputs,
    )


if __name__ == "__main__":
    demo.launch(server_name=settings.gradio_server_name, server_port=settings.gradio_server_port)