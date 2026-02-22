from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., example="123")
    chat_id: str = Field(..., example="456")
    text: str = Field(..., example="У меня болит грудь")