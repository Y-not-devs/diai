from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from src.config import get_settings
from src.api.schemas.chat_request import ChatRequest
from src.api.schemas.chat_response import ChatResponse
from src.api.schemas.diagnosis_result import DiagnosisResult
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


# ─── Response schemas ────────────────────────────────────────────────────────

class ChatSummary(BaseModel):
    chat_id: str
    chat_name: str
    updated_at: Optional[str] = None


class ChatsResponse(BaseModel):
    chats: list[ChatSummary]


class ChatMessageOut(BaseModel):
    message_id: int
    role: str
    text: str
    created_at: Optional[str] = None
    answer_type: Optional[int] = None
    diagnosis: Optional[list[DiagnosisResult]] = None


class ChatMessagesResponse(BaseModel):
    messages: list[ChatMessageOut]
    has_more: bool
    min_message_id: Optional[int] = None


# ─── Endpoints ───────────────────────────────────────────────────────────────

@chat_router.get("/chats", response_model=ChatsResponse)
def get_chats(user_id: str = Query(...)):
    """Список чатов пользователя."""
    chats = chat_service.get_chats(user_id)
    return ChatsResponse(chats=[ChatSummary(**c) for c in chats])


@chat_router.get("/chat_messages", response_model=ChatMessagesResponse)
def get_chat_messages(
    chat_id: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
    before_id: Optional[int] = Query(None),
):
    """История сообщений чата с курсорной пагинацией."""
    messages, has_more, min_id = chat_service.get_messages(chat_id, limit, before_id)
    return ChatMessagesResponse(
        messages=[ChatMessageOut(**m) for m in messages],
        has_more=has_more,
        min_message_id=min_id,
    )


@chat_router.post("/chat_message", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Отправка сообщения пользователя.
    Возвращает JSON с answer_type, text и (опционально) diagnosis.
    """
    return chat_service.process_message(
        user_id=req.user_id,
        chat_id=req.chat_id,
        text=req.text
    )