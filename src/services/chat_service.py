from typing import Optional
from api.schemas.chat_response import ChatResponse
from llm.chat_llm import ChatBot


class ChatService:
    def __init__(self, model_id: str, hf_token: str):
        self.bot = ChatBot(model_id=model_id, hf_token=hf_token)

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

        # Примитивная логика определения типа ответа
        diagnosis_code = self._extract_diagnosis_code(raw_response)

        if diagnosis_code:
            return ChatResponse(
                answer_type=0,
                text=raw_response,
                diagnosis=diagnosis_code
            )

        return ChatResponse(
            answer_type=1,
            text=raw_response,
            diagnosis=None
        )

    def _extract_diagnosis_code(self, text: str) -> Optional[str]:
        """
        Заглушка. Позже сюда вставишь поиск по corpus ICD.
        Сейчас просто ищем шаблон типа I10, J45 и т.п.
        """
        import re

        match = re.search(r"\b[A-Z]\d{2}\b", text)
        return match.group(0) if match else None