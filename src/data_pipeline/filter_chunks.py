import json
from pathlib import Path

INPUT = Path("data/chunked_corpus.json")
OUTPUT = Path("data/diagnostic_corpus.json")

# что МЫ ХОТИМ
GOOD_KEYWORDS = [
    "жалоб",
    "симптом",
    "анамнез",
    "объектив",
    "клиническ",
    "проявлен",
    "боль",
    "температур",
    "слабост",
    "одышк",
    "тошнот",
    "рвот",
    "высып",
    "кашел",
    "кровотеч",
    "головокруж",
    "потеря сознания"
]

# что МЫ НЕ ХОТИМ
BAD_KEYWORDS = [
    "операцион",
    "оборудован",
    "катетер",
    "вмешательств",
    "анестези",
    "приказ",
    "санитар",
    "оснащени",
    "кабинет",
    "рентген",
    "ангиограф",
    "методика",
    "подготовка пациента",
    "требования к оснащению",
]

def is_diagnostic(text: str):
    t = text.lower()

    good = any(k in t for k in GOOD_KEYWORDS)
    bad = any(k in t for k in BAD_KEYWORDS)

    return good and not bad


def main():
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)

    filtered = []

    for chunk in data:
        if is_diagnostic(chunk["text"]):
            filtered.append(chunk)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print("Original chunks:", len(data))
    print("Diagnostic chunks:", len(filtered))


if __name__ == "__main__":
    main()