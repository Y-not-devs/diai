from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.logger import logger
from api.router import router
from src.llm.chat_llm import ChatBot
from config import get_settings

settings = get_settings()

chatbot: ChatBot = None

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.router.lifespan
    async def lifespan(app: FastAPI):
        global chatbot
        logger.info("Loading ChatBot model...")
        chatbot = ChatBot(model_id=settings.MODEL_ID, hf_token=settings.HF_TOKEN)
        logger.info("ChatBot is ready and always online")
        yield
        logger.info("Shutting down ChatBot...")

    return app

app = create_app()

@app.get("/health", tags=["health"])
def health() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})