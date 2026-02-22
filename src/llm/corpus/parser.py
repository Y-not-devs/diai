"""Reduce large protocol JSON text to only the clinically useful parts.

This module keeps key diagnostic/treatment sections and drops administrative
content like abbreviations, evidence scales, author lists, and references.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

# Headings are often like "I. ...", "II. ...", "1.2 ...", "2.1 ...".
_HEADING_INJECT_RE = re.compile(
    r"(?<!\n)(\b(?:[IVXLC]{1,5}\.\s+|\d+(?:\.\d+)*[.)]\s+)[A-Z\u0410-\u042f\u0401])"
)
_HEADING_LINE_RE = re.compile(
    r"^(?:[IVXLC]{1,5}\.\s+|\d+(?:\.\d+)*[.)]\s+)[A-Z\u0410-\u042f\u0401]",
    re.IGNORECASE,
)

_KEEP_PATTERNS = [
    r"\bdefinition\b",
    r"\bclassification\b",
    r"\bdiagnos",
    r"\bcriteria\b",
    r"\bdifferential\b",
    r"\bclinical\b",
    r"\bsymptom",
    r"\bcomplaint",
    r"\banamnes",
    r"\btreatment\b",
    r"\btherapy\b",
    r"\bmanagement\b",
    r"\balgorithm\b",
    r"\blaborator",
    r"\binstrument",
    r"\btest",
    r"\bcomplication",
    r"\bprognos",
    r"\bprevention\b",
    r"\bindication",
    r"\bcontraindication",
    # Russian roots (escaped to keep file ASCII)
    r"\u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438",  # определени
    r"\u043a\u043b\u0430\u0441\u0441\u0438\u0444\u0438\u043a\u0430\u0446",  # классификац
    r"\u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442",  # диагност
    r"\u043a\u0440\u0438\u0442\u0435\u0440",  # критер
    r"\u0434\u0438\u0444\u0444\u0435\u0440\u0435\u043d\u0446",  # дифференц
    r"\u043a\u043b\u0438\u043d\u0438\u0447\u0435\u0441\u043a",  # клиническ
    r"\u0441\u0438\u043c\u043f\u0442\u043e\u043c",  # симптом
    r"\u0436\u0430\u043b\u043e\u0431",  # жалоб
    r"\u0430\u043d\u0430\u043c\u043d\u0435\u0437",  # анамнез
    r"\u043b\u0435\u0447\u0435\u043d\u0438",  # лечени
    r"\u0442\u0430\u043a\u0442\u0438\u043a",  # тактик
    r"\u0442\u0435\u0440\u0430\u043f\u0438",  # терапи
    r"\u0432\u0435\u0434\u0435\u043d\u0438",  # ведени
    r"\u0430\u043b\u0433\u043e\u0440\u0438\u0442\u043c",  # алгоритм
    r"\u043b\u0430\u0431\u043e\u0440\u0430\u0442\u043e\u0440",  # лаборатор
    r"\u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442",  # инструмент
    r"\u0438\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d",  # исследован
    r"\u043e\u0441\u043b\u043e\u0436\u043d",  # осложн
    r"\u043f\u0440\u043e\u0433\u043d\u043e\u0437",  # прогноз
    r"\u043f\u0440\u043e\u0444\u0438\u043b\u0430\u043a\u0442\u0438\u043a",  # профилактик
    r"\u043f\u043e\u043a\u0430\u0437\u0430\u043d",  # показан
    r"\u043f\u0440\u043e\u0442\u0438\u0432\u043e\u043f\u043e\u043a\u0430\u0437",  # противопоказ
]

_DROP_PATTERNS = [
    r"\babbrev",
    r"\bacronym",
    r"\busers?\b",
    r"\bcategory\b",
    r"\bevidence\b",
    r"\borganization",
    r"\bauthor",
    r"\breviewer",
    r"\breference",
    r"\bbibliograph",
    r"\bliterature",
    r"\bappendix",
    r"\bdevelopers?",
    # Russian roots (escaped to keep file ASCII)
    r"\u0441\u043e\u043a\u0440\u0430\u0449\u0435\u043d\u0438",  # сокращени
    r"\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b",  # пользовател
    r"\u043a\u0430\u0442\u0435\u0433\u043e\u0440",  # категори
    r"\u0448\u043a\u0430\u043b\u0430",  # шкала
    r"\u0434\u043e\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044c\u043d",  # доказательн
    r"\u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u043e\u043d",  # организацион
    r"\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a",  # разработчик
    r"\u0440\u0435\u0446\u0435\u043d\u0437\u0435\u043d\u0442",  # рецензент
    r"\u043b\u0438\u0442\u0435\u0440\u0430\u0442\u0443\u0440",  # литератур
    r"\u0441\u043f\u0438\u0441\u043e\u043a\s+\u043b\u0438\u0442\u0435\u0440\u0430\u0442\u0443\u0440",  # список литературы
    r"\u0434\u0430\u0442\u0430\s+\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a",  # дата разработки
    r"\u043c\u043a\u0431",  # мкб
    r"\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438",  # приложение
]

_KEEP_RE = re.compile("|".join(_KEEP_PATTERNS), re.IGNORECASE)
_DROP_RE = re.compile("|".join(_DROP_PATTERNS), re.IGNORECASE)

_BULLET_RE = re.compile(
    r"[\u2022\u2023\u25e6\u2043\u2219\u00b7\u2024\u25cf\u25a0\u25a1\u25aa\u25ab\u25a2]"
)
_REF_RE = re.compile(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]")
_CONTROL_RE = re.compile(r"[\u0000-\u0008\u000b-\u001f\u007f-\u009f]")
_NB_RE = re.compile(r"\bNB[.!]?\b", re.IGNORECASE)
_MOJIBAKE_CHARS = set("ЃЌЋЏЎЍђѓќљџї")


def _text_quality(text: str) -> int:
    controls = sum(1 for ch in text if "\u0080" <= ch <= "\u009f")
    cyr = sum(1 for ch in text if "\u0400" <= ch <= "\u04ff")
    mojibake = sum(1 for ch in text if ch in _MOJIBAKE_CHARS)
    return cyr - controls * 5 - mojibake * 2


def _looks_mojibake(text: str) -> bool:
    if not text:
        return False
    mojibake = sum(1 for ch in text if ch in _MOJIBAKE_CHARS)
    cyr = sum(1 for ch in text if "\u0400" <= ch <= "\u04ff")
    if mojibake == 0:
        return False
    return cyr > 0 and (mojibake / max(cyr, 1)) > 0.02


def _maybe_fix_mojibake(text: str) -> str:
    if not _looks_mojibake(text):
        return text
    try:
        candidate = text.encode("cp1251").decode("utf-8")
    except Exception:
        return text
    return candidate if _text_quality(candidate) >= _text_quality(text) else text


def _normalize_text(text: str) -> str:
    text = _maybe_fix_mojibake(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("–", "-").replace("—", "-")
    text = _HEADING_INJECT_RE.sub(r"\n\1", text)
    text = _BULLET_RE.sub(" - ", text)
    text = _NB_RE.sub("", text)
    text = _REF_RE.sub("", text)
    text = _CONTROL_RE.sub(" ", text)
    return text


def _split_heading_line(line: str) -> tuple[str, str]:
    match = re.match(
        r"^((?:[IVXLC]{1,5}\.|\\d+(?:\\.\\d+)*[.)])\\s+)(.+)$", line
    )
    if not match:
        return line, ""

    prefix = match.group(1)
    rest = match.group(2).strip()
    if ":" in rest:
        title, body = rest.split(":", 1)
        return f"{prefix}{title.strip()}:", body.strip()

    dash_match = re.match(r"^(.{0,80}?)(?:\\s+[-\\u2013\\u2014]\\s+)(.+)$", rest)
    if dash_match:
        title = dash_match.group(1).strip()
        body = dash_match.group(2).strip()
        return f"{prefix}{title}", body

    return line, ""


def _split_sections(text: str) -> list[tuple[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections: list[tuple[str, str]] = []
    current_title = ""
    current_body: list[str] = []
    for line in lines:
        if _HEADING_LINE_RE.match(line):
            if current_title or current_body:
                sections.append((current_title, " ".join(current_body)))
            title, inline_body = _split_heading_line(line)
            current_title = title
            current_body = [inline_body] if inline_body else []
        else:
            current_body.append(line)
    if current_title or current_body:
        sections.append((current_title, " ".join(current_body)))
    return sections


def _is_relevant(title: str, body: str) -> bool:
    if title and _DROP_RE.search(title):
        return False
    if title and _KEEP_RE.search(title):
        return True
    if body and _KEEP_RE.search(body):
        return True
    return False


def _cleanup_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,;:!?])([^\s])", r"\1 \2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text.rfind(".", 0, max_chars)
    if cut < max_chars // 2:
        cut = text.rfind(" ", 0, max_chars)
    if cut <= 0:
        return text[:max_chars].rstrip()
    return text[:cut + 1].rstrip()


def reduce_text(text: str, *, max_chars: int = 4000) -> str:
    """Return a shortened version of protocol text."""
    if not text:
        return ""
    normalized = _normalize_text(text)
    sections = _split_sections(normalized)

    kept: list[str] = []
    for title, body in sections:
        if _is_relevant(title, body):
            if title and body:
                kept.append(f"{title}\n{body}")
            else:
                kept.append(title or body)

    if kept:
        reduced = "\n\n".join(chunk.strip() for chunk in kept if chunk.strip())
    else:
        reduced = normalized

    reduced = _cleanup_text(reduced)
    reduced = reduced.lower()
    return _truncate_text(reduced, max_chars)


def reduce_record(
    record: dict,
    *,
    max_chars: int = 4000,
    keep_fields: Iterable[str] | None = None,
) -> dict:
    """Reduce a single protocol record dict."""
    if keep_fields is None:
        keep_fields = ("protocol_id", "source_file", "title", "icd_codes", "text")
    reduced: dict = {}
    for key in keep_fields:
        if key in record:
            value = record[key]
            if isinstance(value, str):
                value = _maybe_fix_mojibake(value)
                value = _CONTROL_RE.sub(" ", value)
                value = re.sub(r"[ \t]+", " ", value).strip()
            reduced[key] = value
    if "text" in reduced:
        reduced["text"] = reduce_text(str(reduced["text"]), max_chars=max_chars)
    return reduced


def _open_text_file(path: Path):
    encodings = ("utf-8", "utf-8-sig", "cp1251")
    for enc in encodings:
        try:
            handle = path.open("r", encoding=enc)
            handle.read(1)
            handle.seek(0)
            return handle
        except UnicodeDecodeError:
            try:
                handle.close()
            except Exception:
                pass
    return path.open("r", encoding="utf-8", errors="replace")


def _iter_records(path: Path) -> Iterable[dict]:
    with _open_text_file(path) as handle:
        # Peek the first non-space char to decide JSON vs JSONL.
        first_char = ""
        while True:
            ch = handle.read(1)
            if not ch:
                break
            if not ch.isspace():
                first_char = ch
                break
        handle.seek(0)
        if first_char == "[":
            data = json.load(handle)
            if isinstance(data, list):
                for item in data:
                    yield item
            else:
                yield data
        else:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


def reduce_corpus_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    max_chars: int = 4000,
    keep_fields: Iterable[str] | None = None,
) -> None:
    """Read JSON/JSONL corpus, write reduced JSONL file."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as out:
        for record in _iter_records(input_path):
            reduced = reduce_record(record, max_chars=max_chars, keep_fields=keep_fields)
            out.write(json.dumps(reduced, ensure_ascii=False))
            out.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reduce protocol corpus JSON/JSONL into compact JSONL."
    )
    parser.add_argument("input", help="Path to input JSON or JSONL file.")
    parser.add_argument("output", help="Path to output JSONL file.")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=4000,
        help="Max characters kept in reduced text (default: 4000).",
    )
    args = parser.parse_args()
    reduce_corpus_file(args.input, args.output, max_chars=args.max_chars)


if __name__ == "__main__":
    main()
