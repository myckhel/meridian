from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.exceptions import ChatConfigurationError, UpstreamServiceError

router = APIRouter()
chat_service = ChatService()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        return await chat_service.handle_message(payload.message, payload.session_id)
    except ChatConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except UpstreamServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc