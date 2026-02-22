import json


INPUT = "data/chunked_corpus.json"
OUTPUT = "data/diagnostic_corpus.json"

# ключевые медицинские признаки пациента
PATIENT_WORDS = [
    "боль","болит","болезненность","зуд","жжение",
    "температура","лихорадка","озноб",
    "слабость","утомляемость","головокружение",
    "одышка","кашель","тошнота","рвота",
    "сыпь","покраснение","отек","припухлость",
    "тахикардия","гипотония","гипертензия",
    "понос","диарея","запор","кровотечение"
]

# мусор (протокольные разделы)
BANNED = [
    "рекомендуется",
    "следует проводить",
    "операционная",
    "аппарат",
    "катетер",
    "анестезия",
    "тромбэктомия",
    "хирургичес",
    "оборудован",
    "приказ",
    "стандарт",
    "методика",
    "лечение",
    "терапия"
]

def is_diagnostic(text: str):
    t = text.lower()

    # есть ли симптомы
    has_symptom = any(w in t for w in PATIENT_WORDS)

    # есть ли протокольный мусор
    has_banned = any(w in t for w in BANNED)

    return has_symptom and not has_banned


def main():
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)

    filtered = [x for x in data if is_diagnostic(x["text"])]

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print("Original:", len(data))
    print("Diagnostic:", len(filtered))


if __name__ == "__main__":
    main()