# Qazcode CDSS — Медицинский ИИ-ассистент

Система клинической поддержки принятия решений (CDSS) на основе LLM. Помогает врачам определять диагнозы на основе официальных клинических протоколов Республики Казахстан.

## Стек технологий

| Часть | Технологии |
|---|---|
| Фронтенд | React 19, TypeScript, Vite, Tailwind CSS v4, Bun |
| Бэкенд | Python 3.12, FastAPI, SQLite, Uvicorn |
| Модель | Qwen2.5-1.5B-Instruct (HuggingFace) |
| Деплой | Docker, Docker Compose |

---

## Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone <repo-url>
cd diai
```

### 2. Создай `.env` файл

```bash
cp .env.example .env
```

Заполни переменные в `.env`:

```env
MODEL_ID=Qwen/Qwen2.5-1.5B-Instruct
HF_TOKEN=hf_your_token_here
DATA_PATH=./data
MODEL_PATH=./qwen
CHAT_BOT_MODE=0
```

> `CHAT_BOT_MODE`: `0` = только локальная модель, `1` = авто-обновление, `2` = обновление с токеном

### 3. Запусти через Docker Compose

```bash
docker compose up
```

- Фронтенд: [http://localhost:8000](http://localhost:8000)
- Бэкенд API: [http://localhost:8080](http://localhost:8080)
- Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## Локальная разработка (без Docker)

### Бэкенд

```bash
# Установи зависимости
pip install fastapi uvicorn

# Запусти мок-сервер (без модели, для тестирования)
uvicorn src.mock_server:app --host 127.0.0.1 --port 8001 --reload

# Или настоящий бэкенд (требует скачанную модель)
uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

### Фронтенд

```bash
cd frontend
bun install
bun run dev
```

Фронтенд запустится на [http://localhost:5173](http://localhost:5173).

---

## API

### `GET /api/chats`
Список чатов пользователя.

**Query:** `user_id=string`

**Response:**
```json
{ "chats": [{ "chat_id": "...", "chat_name": "...", "updated_at": "..." }] }
```

---

### `GET /api/chat_messages`
История сообщений чата (курсорная пагинация).

**Query:** `chat_id`, `limit`, `before_id` (опционально)

**Response:**
```json
{ "messages": [...], "has_more": true, "min_message_id": 42 }
```

---

### `POST /api/chat_message`
Отправить сообщение и получить ответ модели.

**Body:**
```json
{ "user_id": "...", "chat_id": "...", "text": "..." }
```

**Response:**
```json
{
  "message_id": 123,
  "role": "assistant",
  "text": "...",
  "answer_type": 0,
  "diagnosis": [
    {
      "id": "1",
      "diagnosis": "Пневмония",
      "icd_10": "J18.9",
      "confidence": 0.85,
      "explanation": "...",
      "protocol_title": "Клинический протокол МЗ РК"
    }
  ]
}
```

> `answer_type: 1` — уточняющий вопрос (`diagnosis: null`)  
> `answer_type: 0` — финальный диагноз (`diagnosis: [...]`)

---

## Структура проекта

```
diai/
├── frontend/          # React-приложение
│   └── src/
│       ├── api/       # HTTP-запросы к бэкенду
│       ├── features/  # Компоненты: чат, диагноз
│       └── types/     # TypeScript-типы
├── src/               # Python-бэкенд
│   ├── api/           # FastAPI роутеры и схемы
│   ├── llm/           # Модель, ретривал, ре-ранкинг
│   ├── services/      # Бизнес-логика, SQLite-хранилище
│   └── utils/         # Логгер, конфиги
├── data/              # Корпус протоколов и база данных
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── pyproject.toml
```

---

## Подготовка корпуса протоколов

```bash
# 1. Нормализация текста
python src/llm/corpus/parser.py data/protocols_corpus.jsonl data/processed/protocols_corpus_reduced.jsonl

# 2. Индексация в SQLite FTS
python src/llm/retrieval.py \
  data/processed/protocols_corpus_reduced.jsonl \
  data/processed/chunks \
  data/processed/index.sqlite
```

---

> ИИ может ошибаться. Всегда сверяйте диагнозы с официальными клиническими протоколами.
