"""LLM reranking for protocol candidates using Hugging Face Inference API."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Iterable

import httpx


@dataclass(frozen=True)
class Candidate:
    protocol_id: str
    title: str
    icd_codes: list[str]
    text: str


def _load_env() -> tuple[str, str]:
    token = os.getenv("HF_TOKEN", "").strip()
    model_id = os.getenv("MODEL_ID", "").strip()
    if not token or not model_id:
        raise RuntimeError("HF_TOKEN or MODEL_ID is missing from environment.")
    return token, model_id


def _candidate_snippet(text: str, limit: int = 800) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _build_prompt(complaint: str, candidates: Iterable[Candidate], top_n: int) -> str:
    items = []
    for idx, cand in enumerate(candidates, start=1):
        snippet = _candidate_snippet(cand.text)
        items.append(
            {
                "id": cand.protocol_id,
                "title": cand.title,
                "icd_codes": cand.icd_codes,
                "snippet": snippet,
            }
        )

    payload = {
        "complaint": complaint.strip(),
        "candidates": items,
        "top_n": top_n,
        "output_format": {
            "diagnoses": [
                {
                    "rank": 1,
                    "protocol_id": "string",
                    "reason": "short reason matching complaint",
                }
            ]
        },
    }

    return (
        "You are a medical protocol matcher. "
        "Given a patient's complaint and candidate protocol snippets, "
        "rank the most relevant protocols. "
        "Return ONLY valid JSON in the provided output_format.\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def rerank_protocols(
    complaint: str,
    candidates: Iterable[Candidate],
    *,
    top_n: int = 3,
    timeout_s: float = 60.0,
) -> dict:
    """Rerank candidates via Hugging Face Inference API."""
    token, model_id = _load_env()
    prompt = _build_prompt(complaint, candidates, top_n)
    url = f"https://api-inference.huggingface.co/models/{model_id}"

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.2,
            "return_full_text": False,
        },
    }

    with httpx.Client(timeout=timeout_s) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    generated = ""
    if isinstance(data, list) and data:
        generated = data[0].get("generated_text", "")
    elif isinstance(data, dict):
        generated = data.get("generated_text", "")

    if not generated:
        raise RuntimeError("Empty response from Hugging Face inference API.")

    match = re.search(r"\{.*\}", generated, re.DOTALL)
    if match:
        generated = match.group(0)

    return json.loads(generated)


__all__ = ["Candidate", "rerank_protocols"]
