import re
from typing import Optional
from src.api.schemas.chat_response import ChatResponse
from src.api.schemas.diagnosis_result import DiagnosisResult
from src.llm.chat_llm import ChatBot
from src.services import user_data


class ChatService:
    def __init__(self, model_path: str, hf_model_id: str, hf_token: Optional[str] = None, mode: int = 1):
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
        user_data.init_db()

    def _build_prompt(self, user_text: str) -> str:
        return (
            "Ты медицинский ассистент.\n"
            "Если информации недостаточно — задай уточняющий вопрос.\n"
            "Если симптомов достаточно — укажи вероятный диагноз.\n\n"
            f"Симптомы пользователя: {user_text}\n"
        )

    def process_message(self, user_id: str, chat_id: str, text: str) -> ChatResponse:
        # Ensure the chat exists in DB; use first 60 chars of text as name
        chat_name = text[:60].strip() or "Новый чат"
        user_data.create_or_update_chat(chat_id, user_id, chat_name)

        # Save user message
        user_data.save_message(chat_id, "user", text, None, None)

        # Generate response
        prompt = self._build_prompt(text)
        raw_response = self.bot.generate_response(prompt)
        diagnosis_list = self._extract_diagnosis(raw_response)
        answer_type = 0 if diagnosis_list else 1

        # Save assistant message
        diag_dicts = [d.model_dump() for d in diagnosis_list] if diagnosis_list else None
        user_data.save_message(chat_id, "assistant", raw_response, answer_type, diag_dicts)

        return ChatResponse(
            answer_type=answer_type,
            text=raw_response,
            diagnosis=diagnosis_list or None,
        )

    def get_chats(self, user_id: str) -> list[dict]:
        return user_data.get_chats(user_id)

    def get_messages(
        self, chat_id: str, limit: int, before_id: Optional[int] = None
    ) -> tuple[list[dict], bool, Optional[int]]:
        return user_data.get_messages(chat_id, limit, before_id)

    def _extract_diagnosis(self, text: str) -> list[DiagnosisResult]:
        """Extract MKB-10 code from model output and wrap as DiagnosisResult."""
        match = re.search(r"\b[A-Z]\d{2}\b", text)
        if not match:
            return []
        code = match.group(0)
        return [
            DiagnosisResult(
                id="1",
                diagnosis="Требует уточнения",
                icd_10=code,
                confidence=0.6,
                explanation="Код МКБ-10 обнаружен в ответе модели.",
                protocol_title="—",
            )
        ]