"""
Mock diagnostic server that returns random ICD-10 codes.

Usage:
    uv run uvicorn src.mock_server:app --host 127.0.0.1 --port 8000

Docker:
    docker build -t mock-server .
    docker run -p 8000:8000 mock-server

Runs on http://127.0.0.1:8000/diagnose
"""

import random
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🏥 Mock Diagnostic Server (FastAPI)")
    print("=" * 40)
    print("Endpoint: /diagnose")
    print("Method:   POST")
    print('Body:     {"symptoms": "..."}')
    print("Docs:     /docs")
    print("=" * 40)
    print("\nPress Ctrl+C to stop\n")
    yield


app = FastAPI(title="Mock Diagnostic Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock Data ---
MOCK_CHATS = [
    {"chat_id": "chat-1", "chat_name": "Головная боль", "updated_at": "2026-02-22T10:00:00Z"},
    {"chat_id": "chat-2", "chat_name": "Температура 38", "updated_at": "2026-02-21T09:00:00Z"},
]

MOCK_MESSAGES = {
    "chat-1": [
        {"message_id": 1, "role": "user", "text": "Болит голова уже 3 дня", "answer_type": None, "diagnosis": None, "created_at": "2026-02-22T10:00:00Z"},
        {"message_id": 2, "role": "assistant", "text": "Как давно началась боль и где именно локализуется?", "answer_type": 1, "diagnosis": None, "created_at": "2026-02-22T10:00:05Z"},
    ],
    "chat-2": [
        {"message_id": 3, "role": "user", "text": "Температура 38, кашель", "answer_type": None, "diagnosis": None, "created_at": "2026-02-21T09:00:00Z"},
        {"message_id": 4, "role": "assistant", "text": "На основании симптомов:", "answer_type": 0, "diagnosis": [
            {"id": "1", "diagnosis": "Пневмония", "icd_10": "J18.9", "confidence": 0.85, "explanation": "Высокая температура и кашель соответствуют пневмонии", "protocol_title": "Клинический протокол МЗ РК"},
        ], "created_at": "2026-02-21T09:00:10Z"},
    ],
}

ICD_CODES = [
    "A00.13",
    "A01.14",
    "A02.15",
    "A03.16",
    "A04.17",
    "A05.18",
    "A06",
    "A07.19",
    "A08",
    "A09.20",
    "B00",
    "B01.21",
    "B02.22",
    "B03",
    "B04.23",
    "B05.24",
    "J00",
    "J01.25",
    "J02",
    "J03.26",
    "J04",
    "J05",
    "J06",
    "K00",
    "K01",
    "K02",
    "K03",
    "K04",
    "K05",
    "L00",
    "L01",
    "L02",
    "L03",
    "L04",
    "M00",
    "M01",
    "M02",
    "M03",
    "N00",
    "N01",
    "N02",
    "N03",
]


class DiagnoseRequest(BaseModel):
    symptoms: Optional[str] = ""


class Diagnosis(BaseModel):
    rank: int
    diagnosis: str
    icd10_code: str
    explanation: str


class DiagnoseResponse(BaseModel):
    diagnoses: list[Diagnosis]


@app.post("/diagnose", response_model=DiagnoseResponse)
async def handle_diagnose(request: DiagnoseRequest) -> DiagnoseResponse:
    """Handle POST /diagnose requests with random diagnoses."""
    symptoms = request.symptoms or ""

    codes = random.sample(ICD_CODES, min(5, len(ICD_CODES)))
    diagnoses = []

    for rank, code in enumerate(codes, start=1):
        diagnoses.append(
            Diagnosis(
                rank=rank,
                diagnosis=f"Simulated diagnosis for {code}",
                icd10_code=code,
                explanation=f"Based on symptoms: {symptoms[:100]}..."
                if symptoms
                else "No symptoms provided",
            )
        )

    return DiagnoseResponse(diagnoses=diagnoses)

# --- Schemas ---
class ChatMessageRequest(BaseModel):
    user_id: str
    chat_id: str
    text: str

# --- Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/chats")
def get_chats(user_id: str):
    return {"chats": MOCK_CHATS}

@app.get("/api/chat_messages")
def get_chat_messages(chat_id: str, limit: int = 10, before_id: Optional[int] = None):
    messages = MOCK_MESSAGES.get(chat_id, [])
    if before_id:
        messages = [m for m in messages if m["message_id"] < before_id]
    messages = messages[-limit:]
    return {
        "messages": messages,
        "has_more": False,
        "min_message_id": messages[0]["message_id"] if messages else None,
    }

@app.post("/api/chat_message")
def send_message(body: ChatMessageRequest):
    if len(body.text) > 30:
        codes = random.sample(ICD_CODES, 2)
        return {
            "message_id": random.randint(100, 999),
            "role": "assistant",
            "text": "На основании описанных симптомов наиболее вероятны следующие диагнозы:",
            "answer_type": 0,
            "diagnosis": [
                {"id": str(i+1), "diagnosis": f"Диагноз {code}", "icd_10": code, "confidence": round(random.uniform(0.6, 0.95), 2), "explanation": f"Симптомы соответствуют коду {code}", "protocol_title": "Клинический протокол МЗ РК"}
                for i, code in enumerate(codes)
            ]
        }
    
    return {
        "message_id": random.randint(100, 999),
        "role": "assistant",
        "text": "Уточните, как давно появились симптомы и есть ли температура?",
        "answer_type": 1,
        "diagnosis": None,
    }