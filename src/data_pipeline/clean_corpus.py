import json
import re
from pathlib import Path

INPUT = Path("data/raw_protocols.json")
OUTPUT = Path("data/processed_corpus.json")

def clean_text(text: str) -> str:
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"Одобрен.*?года", "", text)
    text = re.sub(r"Протокол №\d+", "", text)
    return text.strip()

def main():
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)

    processed = []

    for item in data:
        cleaned = clean_text(item["text"])

        processed.append({
            "protocol_id": item["protocol_id"],
            "title": item["title"],
            "icd_codes": item["icd_codes"],
            "text": cleaned
        })

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    print("Processed:", len(processed))

if __name__ == "__main__":
    main()