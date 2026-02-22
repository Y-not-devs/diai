"""Chunking, indexing, and retrieval for protocol corpus."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    protocol_id: str
    title: str
    icd_codes: list[str]
    chunk_index: int
    text: str
    path: str


def _read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _split_paragraphs(text: str) -> list[str]:
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return parts if parts else [text.strip()]


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> list[str]:
    if not text:
        return []
    paragraphs = _split_paragraphs(text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len + 2 <= max_chars:
            current.append(para)
            current_len += para_len + 2
            continue

        if current:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0

        if para_len > max_chars:
            start = 0
            while start < para_len:
                end = min(start + max_chars, para_len)
                chunk = para[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = max(0, end - overlap)
            continue

        current.append(para)
        current_len = para_len

    if current:
        chunks.append("\n\n".join(current))

    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    with_overlap: list[str] = []
    for idx, chunk in enumerate(chunks):
        if idx == 0:
            with_overlap.append(chunk)
            continue
        prev = chunks[idx - 1]
        prefix = prev[-overlap:]
        merged = f"{prefix}\n{chunk}"
        with_overlap.append(merged)
    return with_overlap


def build_chunks(
    input_jsonl: Path,
    output_dir: Path,
    *,
    max_chars: int = 1200,
    overlap: int = 200,
) -> Iterable[Chunk]:
    output_dir.mkdir(parents=True, exist_ok=True)

    for record in _read_jsonl(input_jsonl):
        protocol_id = str(record.get("protocol_id", "")).strip()
        if not protocol_id:
            continue
        title = str(record.get("title", "")).strip()
        icd_codes = record.get("icd_codes") or []
        text = str(record.get("text", "")).strip()
        if not text:
            continue

        protocol_dir = output_dir / protocol_id
        protocol_dir.mkdir(parents=True, exist_ok=True)

        for idx, chunk in enumerate(chunk_text(text, max_chars=max_chars, overlap=overlap)):
            chunk_id = f"{protocol_id}__{idx:04d}"
            path = protocol_dir / f"{chunk_id}.json"
            payload = {
                "chunk_id": chunk_id,
                "protocol_id": protocol_id,
                "title": title,
                "icd_codes": icd_codes,
                "chunk_index": idx,
                "text": chunk,
            }
            with path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False)

            yield Chunk(
                chunk_id=chunk_id,
                protocol_id=protocol_id,
                title=title,
                icd_codes=icd_codes,
                chunk_index=idx,
                text=chunk,
                path=str(path),
            )


def build_index(db_path: Path, chunks: Iterable[Chunk]) -> None:
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute(
            """
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                protocol_id TEXT,
                title TEXT,
                icd_codes TEXT,
                chunk_index INTEGER,
                chunk_text TEXT,
                path TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE chunks_fts USING fts5(
                chunk_text,
                title,
                icd_codes,
                protocol_id,
                chunk_id,
                content='chunks',
                content_rowid='rowid'
            )
            """
        )

        for chunk in chunks:
            icd_codes = " ".join(chunk.icd_codes)
            conn.execute(
                """
                INSERT INTO chunks (
                    chunk_id, protocol_id, title, icd_codes, chunk_index, chunk_text, path
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.chunk_id,
                    chunk.protocol_id,
                    chunk.title,
                    icd_codes,
                    chunk.chunk_index,
                    chunk.text,
                    chunk.path,
                ),
            )

        conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES ('rebuild');")
        conn.commit()
    finally:
        conn.close()


def search_candidates(
    db_path: Path,
    query: str,
    *,
    top_k: int = 50,
    top_protocols: int = 5,
) -> list[dict]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
                chunk_id,
                protocol_id,
                title,
                icd_codes,
                chunk_text,
                bm25(chunks_fts) AS score
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (query, top_k),
        ).fetchall()

        grouped: dict[str, dict] = {}
        for row in rows:
            protocol_id = row["protocol_id"]
            entry = grouped.setdefault(
                protocol_id,
                {
                    "protocol_id": protocol_id,
                    "title": row["title"],
                    "icd_codes": row["icd_codes"].split() if row["icd_codes"] else [],
                    "score": 0.0,
                    "chunks": [],
                },
            )
            entry["score"] += float(row["score"])
            entry["chunks"].append(row["chunk_text"])

        ranked = sorted(grouped.values(), key=lambda x: x["score"])[:top_protocols]
        return ranked
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk corpus and build FTS index.")
    parser.add_argument("input_jsonl", help="Reduced corpus JSONL file.")
    parser.add_argument("output_dir", help="Directory for chunk files.")
    parser.add_argument("db_path", help="SQLite index path.")
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--overlap", type=int, default=200)
    args = parser.parse_args()

    input_jsonl = Path(args.input_jsonl)
    output_dir = Path(args.output_dir)
    db_path = Path(args.db_path)

    chunks = build_chunks(
        input_jsonl,
        output_dir,
        max_chars=args.max_chars,
        overlap=args.overlap,
    )
    build_index(db_path, chunks)


__all__ = ["Chunk", "build_chunks", "build_index", "search_candidates"]


if __name__ == "__main__":
    main()
