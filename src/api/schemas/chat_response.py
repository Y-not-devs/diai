from pydantic import BaseModel
from typing import Optional


class ChatResponse(BaseModel):
    answer_type: int
    text: str
    diagnosis: Optional[str] = None