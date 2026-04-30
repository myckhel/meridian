from typing import Literal

from pydantic import BaseModel, Field


class ToolExecutionEvent(BaseModel):
    tool_name: str
    status: Literal["completed", "failed"]
    summary: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    session_id: str | None = None
    tool_events: list[ToolExecutionEvent] = Field(default_factory=list)