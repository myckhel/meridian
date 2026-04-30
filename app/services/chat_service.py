class ChatService:
    async def handle_message(self, _: str, session_id: str | None = None) -> dict[str, str | None]:
        return {
            "message": "Chat orchestration is not implemented yet.",
            "session_id": session_id,
        }