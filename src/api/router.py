from fastapi import APIRouter
from chat_manager import router as chat_router

router = APIRouter(prefix="/api")

router.include_router(chat_router, prefix="/chat", tags=["chat"])
