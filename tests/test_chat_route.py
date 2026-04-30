from fastapi.testclient import TestClient

from app.main import app


def test_chat_route_returns_service_payload(monkeypatch) -> None:
    async def fake_handle_message(message: str, session_id: str | None = None):
        return {
            "message": f"Echo: {message}",
            "session_id": session_id or "session-1",
            "tool_events": [],
        }

    monkeypatch.setattr("app.api.routes.chat.chat_service.handle_message", fake_handle_message)
    client = TestClient(app)

    response = client.post("/api/v1/chat", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.json()["message"] == "Echo: Hello"


def test_chat_route_validates_payload() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/chat", json={"message": ""})

    assert response.status_code == 422