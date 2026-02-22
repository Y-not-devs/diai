import json
from pathlib import Path

DATA_PATH = Path("data/corpus/protocols_corpus.jsonl")
OUTPUT_PATH = Path("data/raw_protocols.json")

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def main():
    protocols = load_jsonl(DATA_PATH)

    print(f"Loaded protocols: {len(protocols)}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(protocols, f, ensure_ascii=False, indent=2)

    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()