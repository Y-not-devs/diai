from pydantic import BaseModel


class DiagnosisResult(BaseModel):
    id: str
    diagnosis: str
    icd_10: str
    confidence: float
    explanation: str
    protocol_title: str