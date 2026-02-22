from fastapi import APIRouter
from src.api.chat_manager import chat_router

router = APIRouter(prefix="/api")

router.include_router(chat_router, prefix="/chat", tags=["chat"])
