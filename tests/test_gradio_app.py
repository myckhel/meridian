from unittest.mock import Mock

import httpx

from app.ui.gradio_app import _normalize_history, _respond_via_local_service, reset_chat, respond, submit_message


def test_normalize_history_filters_invalid_entries() -> None:
    normalized_history = _normalize_history(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "tool", "content": "ignored"},
            {"role": "user", "content": ["ignored"]},
            ("tuple", "ignored"),
        ]
    )

    assert normalized_history == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]


def test_respond_returns_message_and_session_id(monkeypatch) -> None:
    response = Mock()
    response.json.return_value = {
        "message": "Inventory checked.",
        "session_id": "session-123",
        "tool_events": [
            {
                "tool_name": "search_products",
                "status": "completed",
                "summary": "search_products({\"query\": \"keyboard\"}) in 0.02s -> Found 2 keyboards.",
            }
        ],
    }
    response.raise_for_status.return_value = None

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: response)

    message, session_id = respond("Show me keyboards", [], None)

    assert message == "Inventory checked."
    assert session_id == "session-123"


def test_local_fallback_does_not_append_tool_activity(monkeypatch) -> None:
    class StubEvent:
        def model_dump(self) -> dict[str, str]:
            return {
                "tool_name": "search_products",
                "status": "completed",
                "summary": "search_products({\"query\": \"keyboard\"}) in 0.02s -> Found 2 keyboards.",
            }

    class StubPayload:
        message = "Inventory checked."
        session_id = "session-999"
        tool_events = [StubEvent()]

    async def fake_handle_message(message: str, session_id: str) -> StubPayload:
        return StubPayload()

    monkeypatch.setattr(
        "app.ui.gradio_app.chat_service.handle_message",
        fake_handle_message,
    )

    message, session_id = _respond_via_local_service("Show me keyboards", "session-999")

    assert message == "Inventory checked."
    assert session_id == "session-999"


def test_submit_message_updates_history_and_session(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.ui.gradio_app.respond",
        lambda message, history, session_id: (f"Handled: {message}", "session-456"),
    )

    cleared_message, updated_history, updated_session_id = submit_message(
        " Show me keyboards ",
        [{"role": "assistant", "content": "How can I help?"}],
        None,
    )

    assert cleared_message == ""
    assert updated_session_id == "session-456"
    assert updated_history == [
        {"role": "assistant", "content": "How can I help?"},
        {"role": "user", "content": "Show me keyboards"},
        {"role": "assistant", "content": "Handled: Show me keyboards"},
    ]


def test_respond_falls_back_to_local_service_when_backend_is_unreachable(monkeypatch) -> None:
    def raise_connect_error(*args, **kwargs):
        raise httpx.ConnectError("backend unavailable")

    monkeypatch.setattr(httpx, "post", raise_connect_error)
    monkeypatch.setattr(
        "app.ui.gradio_app._respond_via_local_service",
        lambda message, session_id: (f"Local: {message}", session_id),
    )

    message, returned_session_id = respond("Show me keyboards", [], "session-789")

    assert message == "Local: Show me keyboards"
    assert returned_session_id == "session-789"


def test_reset_chat_clears_history_and_rotates_session() -> None:
    cleared_message, updated_history, updated_session_id = reset_chat()

    assert cleared_message == ""
    assert updated_history == []
    assert isinstance(updated_session_id, str)
    assert updated_session_id