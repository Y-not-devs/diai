from pydantic import BaseModel
from typing import Optional
from src.api.schemas.diagnosis_result import DiagnosisResult


class ChatResponse(BaseModel):
    answer_type: int
    text: str
    diagnosis: Optional[list[DiagnosisResult]] = None