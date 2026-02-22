from typing import Optional
from ..api.schemas.chat_response import ChatResponse
from ..llm.chat_llm import ChatBot


class ChatService:
    def __init__(self, model_path: str, hf_model_id: str, hf_token: str = None, mode: int = 1):
        """
        model_path: local folder with model
        hf_model_id: HuggingFace model ID
        hf_token: optional token for private/authorized download
        mode: 0=offline_only, 1=auto_update, 2=token_update
        """
        self.bot = ChatBot(
            model_path=model_path,
            hf_model_id=hf_model_id,
            hf_token=hf_token,
            mode=mode
        )

    def _build_prompt(self, user_text: str) -> str:
        return (
            "Ты медицинский ассистент.\n"
            "Если информации недостаточно — задай уточняющий вопрос.\n"
            "Если симптомов достаточно — укажи вероятный диагноз.\n\n"
            f"Симптомы пользователя: {user_text}\n"
        )

    def process_message(self, user_id: str, chat_id: str, text: str) -> ChatResponse:
        prompt = self._build_prompt(text)
        raw_response = self.bot.generate_response(prompt)
        diagnosis_code = self._extract_diagnosis_code(raw_response)

        return ChatResponse(
            answer_type=0 if diagnosis_code else 1,
            text=raw_response,
            diagnosis=diagnosis_code
        )

    def _extract_diagnosis_code(self, text: str) -> Optional[str]:
        """Простейшая проверка для извлечения кода МКБ из текста."""
        import re
        match = re.search(r"\b[A-Z]\d{2}\b", text)
        return match.group(0) if match else None