# DiAi Corpus Pipeline

This repo prepares a large medical protocol corpus for fast keyword search and
optional LLM reranking.

## What each step does

1) **Reduce + normalize text**
- Input: `data/protocols_corpus.jsonl`
- Output: `data/processed/protocols_corpus_reduced.jsonl`
- Removes admin noise, cleans punctuation, normalizes encoding, lowercases text.

Command:
```bash
python src/llm/corpus/parser.py data/protocols_corpus.jsonl data/processed/protocols_corpus_reduced.jsonl
```

2) **Chunk + build SQLite FTS index**
- Output chunks: `data/processed/chunks/<protocol_id>/<protocol_id>__0000.json`
- Output index: `data/processed/index.sqlite`

Command:
```bash
python src/llm/retrieval.py data/processed/protocols_corpus_reduced.jsonl data/processed/chunks data/processed/index.sqlite
```

Options:
```bash
python src/llm/retrieval.py ... --max-chars 1200 --overlap 200
```

3) **Retrieve top candidates (no LLM yet)**
Use `search_candidates()` from `src/llm/retrieval.py` to get top-5 protocol
candidates by keyword match.

## Optional LLM rerank (not run locally)

`src/llm/rerank.py` can rerank top candidates using Hugging Face Inference API.
This is **not executed locally by default**.

Environment variables (in `.env`):
```
HF_TOKEN=...
MODEL_ID=Qwen/Qwen2.5-1.5B-Instruct
```

## Files

- `src/llm/corpus/parser.py` — reduce + normalize corpus text
- `src/llm/retrieval.py` — chunking + SQLite FTS index + retrieval
- `src/llm/rerank.py` — optional LLM rerank

## Notes

- Index search returns top-5 protocols, not final diagnosis.
- LLM rerank is optional and can be added later by another service.
