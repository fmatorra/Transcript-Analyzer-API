# Transcript Analyzer API

Analyze plain-text transcripts with an LLM and get back a concise summary plus a list of next actions.

This service follows clean/hexagonal architecture: clear ports/adapters, domain models, an application service, and an in-memory repository.

---

## ✨ Live API (Swagger UI)

**Production Docs:** [Swagger UI](https://sd-5035863-l.dattaweb.com/api8010/docs)

### How to use “Try it out”:

1. Open the Swagger URL above.
2. Expand `GET /v1/analyze`.
3. Click **Try it out**.
4. Enter a transcript (plain text).
5. Click **Execute** to see the response.

Use `GET /v1/analyses/{analysis_id}` to retrieve a previous result by ID.

> Note: The deployed URL is behind a reverse proxy with the `/api8010` prefix. Locally, use `http://127.0.0.1:8000/docs` (no prefix).

---

## 🧱 Project Layout

```
app/
├── adapters/
│   └── openai.py            # OpenAI adapter implementing the LLM port
├── api/
│   └── routes.py            # FastAPI routes (endpoints)
├── domain/
│   └── models.py            # Domain entities (e.g., TranscriptAnalysis)
├── repositories/
│   └── memory.py            # Thread-safe in-memory repository
├── schemas/
│   └── api.py               # Pydantic request/response schemas
├── services/
│   └── analyzer.py          # Application service orchestrating analysis flow
├── ports/
│   └── llm.py               # LLM Port (interface)
├── configurations.py        # Settings loader (OpenAI key/model from .env)
├── dependencies.py          # DI helpers
├── prompts.py               # System/User prompts
└── main.py                  # FastAPI app factory & CORS setup
tests/
└── ...                      # Pytest tests
```

---

## 🚀 Quickstart

### 1) Environment Setup

**Using Conda (recommended)**

```bash
conda create -n transcript-analyzer python=3.12
conda activate transcript-analyzer
```

**Using Poetry**

```bash
pip install poetry
poetry install
```

**Or with pip**

```bash
pip install -r requirements.txt
# or minimal:
pip install fastapi uvicorn pydantic pydantic-settings openai pytest pytest-cov
```

### 2) Environment Variables

Create a `.env` file at the root:

```env
OPENAI_API_KEY=sk-xxxx_your_key_here
OPENAI_MODEL=gpt-4o-mini-2024-07-18
```

### 3) Run the API

```bash
# with Poetry
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# or plain
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open Swagger locally: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔌 Endpoints

All endpoints are prefixed with `/v1`.

### Analyze (GET)

```
GET /v1/analyze?transcript=...
```

**Response:**

```json
{
  "id": "uuid",
  "summary": "Short summary",
  "next_actions": ["Action 1", "Action 2"]
}
```

**400:** when transcript is empty

### Get by ID

```
GET /v1/analyses/{analysis_id}
```

- **200:** Returns the saved analysis
- **404:** Unknown `analysis_id`

### Batch Analyze (Async)

```
POST /v1/analyze/batch
```

**Body:**

```json
{
  "transcripts": [
    "First transcript...",
    "Second transcript..."
  ]
}
```

**200:** List of analyses  
**400:** When input list is empty or only blank items

---

## 🧪 Testing

```bash
# Basic
pytest

# Verbose
pytest -v

# Coverage
pytest --cov
```

Make sure `.env` and virtual environment are active before running tests.

---

## 🧠 How it Works

- `ports/llm.py`: defines the interface.
- `adapters/openai.py`: implements OpenAI LLM adapter with structured output.
- `services/analyzer.py`: orchestrates validation, prompt building, calling LLM, formatting results.
- `repositories/memory.py`: stores results in a thread-safe map.
- `api/routes.py`: handles HTTP concerns.

Clean architecture ensures testability and separation of concerns.

---

## 🧰 cURL Examples

**Base URL (Local):** `http://127.0.0.1:8000`

### Analyze (GET)

```bash
curl -G "http://127.0.0.1:8000/v1/analyze"   --data-urlencode "transcript=We discussed migrating the database; Alice owns the rollout; ETA Friday."
```

### Analyze (POST)

```bash
curl -X POST "http://127.0.0.1:8000/v1/analyze"   -H "Content-Type: application/json"   -d '{"transcript": "We discussed migrating the database; Alice owns the rollout; ETA Friday."}'
```

### Get by ID

```bash
curl "http://127.0.0.1:8000/v1/analyses/<PASTE_ID_HERE>"
```

### Batch

```bash
curl -X POST "http://127.0.0.1:8000/v1/analyze/batch"   -H "Content-Type: application/json"   -d '{"transcripts": ["First transcript...", "Second transcript..."]}'
```

> For production, use: `https://sd-5035863-l.dattaweb.com/api8010` as base URL.

---

## 🧯 Troubleshooting

- **OpenAI adapter errors**  
  Ensure `.env` is correct and `app/configurations.py` is reading it.

- **Model not available**  
  Use a model accessible by your OpenAI account.

- **Empty transcript → 400**  
  Send non-empty text in the query/body.

- **Reverse proxy issues**  
  Use correct base URL with prefix when behind reverse proxy (`/api8010`).

---

## 📝 Notes

- In-memory storage only. Restarting clears data.
- Uses OpenAI structured outputs: `{ summary: str, next_actions: List[str] }`
- Keep an eye on OpenAI API usage (costs apply).

---

## 🧭 License

**Internal project** — use per your organization’s policies.