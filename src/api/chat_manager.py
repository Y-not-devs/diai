from fastapi import APIRouter
from src.config import get_settings
from src.api.schemas.chat_request import ChatRequest
from src.api.schemas.chat_response import ChatResponse
from src.services.chat_service import ChatService
from pathlib import Path

chat_router = APIRouter()
settings = get_settings()

MODEL_PATH = Path(settings.DATA_PATH) / "models" / Path(settings.MODEL_PATH)
MODEL_PATH.mkdir(parents=True, exist_ok=True)

chat_service = ChatService(
    model_path=str(MODEL_PATH),
    hf_model_id=settings.MODEL_ID,
    hf_token=settings.HF_TOKEN,
    mode=settings.CHAT_BOT_MODE
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