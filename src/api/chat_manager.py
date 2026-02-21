from fastapi import APIRouter
from pydantic import BaseModel
from config import get_settings
from api.schemas.chat_request import ChatRequest
from api.schemas.chat_response import ChatResponse
from services.chat_service import ChatService

chat_router = APIRouter()

settings = get_settings()

chat_service = ChatService(
    model_id=settings.MODEL_ID,
    hf_token=settings.HF_TOKEN
)

@chat_router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Эндпоинт для приема сообщений пользователя.
    Возвращает JSON с answer_type, text и (опционально) diagnosis.
    """
    return chat_service.process_message(
        user_id=req.user_id,
        chat_id=req.chat_id,
        text=req.text
    )