import json
import re
from pathlib import Path

# ========= PATHS =========
INPUT = Path("data/processed_corpus.json")
OUTPUT = Path("data/chunked_corpus.json")

# ========= MEDICAL HEADERS =========
# Разделы протоколов, где реально есть клиника
SECTION_HEADERS = [
    "Жалобы",
    "Клиническая картина",
    "Симптомы",
    "Диагностические критерии",
    "Анамнез",
    "Объективные данные",
]

# ---------------------------------------------------------
# 1. Очистка текста
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)              # лишние пробелы
    text = re.sub(r'\[[0-9\-–, ]+\]', '', text)   # ссылки [1-5]
    text = re.sub(r'http\S+', '', text)           # ссылки
    text = text.replace("  ", " ")
    return text.strip()

# ---------------------------------------------------------
# 2. Выделение клинических разделов
# ---------------------------------------------------------

def extract_medical_sections(text: str):
    """
    Вырезаем ТОЛЬКО диагностическую часть протокола
    """

    # начало клиники
    START_MARKERS = [
        "Жалобы",
        "Клиническая картина",
        "Симптомы",
        "Диагностические критерии",
        "Анамнез",
        "Объективные данные",
    ]

    # где клиника заканчивается
    END_MARKERS = [
        "Лабораторные исследования",
        "Инструментальные исследования",
        "Лечение",
        "Тактика лечения",
        "Госпитализация",
        "Показания для госпитализации",
        "Список литературы",
        "Организационные аспекты",
    ]

    lower = text.lower()

    start_pos = None
    for m in START_MARKERS:
        i = lower.find(m.lower())
        if i != -1:
            start_pos = i
            break

    if start_pos is None:
        return []

    end_pos = len(text)
    for m in END_MARKERS:
        i = lower.find(m.lower(), start_pos)
        if i != -1:
            end_pos = i
            break

    clinical_part = text[start_pos:end_pos]

    # теперь режем на куски
    return [clinical_part]

# ---------------------------------------------------------
# 3. Семантический chunking (САМОЕ ВАЖНОЕ)
# ---------------------------------------------------------
def chunk_text(text: str):
    """
    Правильный медицинский chunking:

    1 chunk = 2–4 предложений симптоматики

    Почему:
    FAISS ищет смысл, а не документы.
    Нам нужны компактные описания заболеваний.
    """

    # делим на предложения
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()

        # отбрасываем мусор
        if len(sentence) < 40:
            continue

        # если чанк стал слишком большим — закрываем
        if len(current) + len(sentence) > 350:
            if len(current) > 120:
                chunks.append(current.strip())
            current = sentence
        else:
            current += " " + sentence

    if len(current) > 120:
        chunks.append(current.strip())

    return chunks

# ---------------------------------------------------------
# 4. Основной pipeline
# ---------------------------------------------------------
def main():

    if not INPUT.exists():
        print("ERROR: processed_corpus.json not found")
        return

    with open(INPUT, encoding="utf-8") as f:
        protocols = json.load(f)

    chunked = []
    chunk_id = 0

    for protocol in protocols:

        text = clean_text(protocol["text"])
        sections = extract_medical_sections(text)

        for section in sections:

            small_chunks = chunk_text(section)

            for piece in small_chunks:
                chunked.append({
                    "chunk_id": chunk_id,
                    "protocol_id": protocol["protocol_id"],
                    "title": protocol["title"],
                    "icd_codes": protocol["icd_codes"],
                    "text": piece
                })
                chunk_id += 1

    # сохранение
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(chunked, f, ensure_ascii=False, indent=2)

    print("===================================")
    print("Protocols processed:", len(protocols))
    print("Total chunks:", len(chunked))
    print("Saved to:", OUTPUT)
    print("===================================")


if __name__ == "__main__":
    main()