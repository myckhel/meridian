from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def chat(payload: ChatRequest) -> ChatResponse:
    response = await chat_service.handle_message(payload.message, payload.session_id)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=response["message"])