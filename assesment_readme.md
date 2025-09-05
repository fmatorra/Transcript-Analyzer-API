Transcript Analyzer API

Analyze plain-text transcripts with an LLM and get back a concise summary plus a list of next actions.
This service follows clean/hexagonal architecture: clear ports/adapters, domain models, an application service, and an in-memory repository.

✨ Live API (Swagger UI)

Production docs: https://sd-5035863-l.dattaweb.com/api8010/docs

How to use “Try it out”

Open the Swagger URL above.

Expand GET /v1/analyze (or POST /v1/analyze).

Click Try it out.

Enter a transcript (plain text).

Click Execute and see the response (includes a unique id, the summary, and next_actions).

Use GET /v1/analyses/{analysis_id} to retrieve a previous result by id.

Note: The deployed URL is behind a reverse proxy with the /api8010 prefix. Locally, you’ll use http://127.0.0.1:8000/docs (no /api8010).

🧱 Project Layout (key parts)
app/
  adapters/
    openai.py           # OpenAI adapter implementing the LLM port
  api/
    routes.py           # FastAPI routes (endpoints)
  domain/
    models.py           # Domain entities (e.g., TranscriptAnalysis)
  repositories/
    memory.py           # Thread-safe in-memory repository
  schemas/
    api.py              # Pydantic request/response schemas
  services/
    analyzer.py         # Application service orchestrating analysis flow
  ports/
    llm.py              # LLM Port (interface)
  configurations.py     # Settings loader (OpenAI key/model from .env)
  dependencies.py       # DI helpers (singleton repo, adapter, service)
  prompts.py            # System/User prompts used by the adapter
app/main.py             # FastAPI app factory & CORS setup
tests/
  ...                   # Pytest tests (unit/integration)

🚀 Quickstart
1) Environment Setup

Conda (recommended)

conda create -n transcript-analyzer python=3.12
conda activate transcript-analyzer


Poetry

pip install poetry
poetry install


Alternatively, with pip:

pip install -r requirements.txt  # if present
# or minimal:
pip install fastapi uvicorn pydantic pydantic-settings openai pytest pytest-cov

2) Environment Variables

Create a .env at the project root:

# .env
OPENAI_API_KEY=sk-xxxx_your_key_here
OPENAI_MODEL=gpt-4o-mini-2024-07-18   # or any model your account supports with structured outputs


The adapter reads these via app/configurations.py.
Make sure the chosen model is available to your account.

3) Run the API
# with Poetry
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# or plain
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Open Swagger locally:
http://127.0.0.1:8000/docs

🔌 Endpoints

All endpoints are prefixed with /v1.

Analyze (GET)

GET /v1/analyze?transcript=...

Query: transcript (string, required)

200:

{
  "id": "c7f6d2e1-7f54-4e3a-9dc7-567c9d2a3a94",
  "summary": "Short, accurate recap of the discussion.",
  "next_actions": [
    "Schedule the migration dry run",
    "Assign QA owner for validation",
    "Prepare rollback plan"
  ]
}


400: when transcript is empty

Analyze (POST)

POST /v1/analyze

Body:

{ "transcript": "Plain text transcript here..." }


Responses: same as GET.

Get by ID

GET /v1/analyses/{analysis_id}

200: Returns the saved analysis

404: Unknown analysis_id

Batch Analyze (Async)

POST /v1/analyze/batch

Body:

{
  "transcripts": [
    "First transcript text...",
    "Second transcript text..."
  ]
}


200: List of analyses (each element same shape as single analyze response)

400: when the list is empty or only blank items

🧪 Testing
# Basic
pytest

# Verbose
pytest -v

# Coverage
pytest --cov


Ensure your virtual environment is active, dependencies are installed, and .env exists before running tests.

🧠 How it Works (Architecture in brief)

ports/llm.py defines the LLm interface:

def run_completion(system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel: ...


adapters/openai.py implements that interface using OpenAI’s structured outputs.
It also provides run_completion_async (used when available to keep the event loop responsive).

services/analyzer.py orchestrates the flow:

Validates input.

Builds prompts from app/prompts.py.

Calls the LLM adapter (run_completion_async or run_completion).

Wraps results into a domain model (TranscriptAnalysis).

Returns the domain model to the API layer.

repositories/memory.py stores analyses in a thread-safe in-memory map keyed by id.

api/routes.py exposes the HTTP endpoints and handles HTTP-level concerns (validation, status codes).

This separation makes it easy to unit-test (services with a fake adapter, repositories in isolation) and to swap adapters/repositories if needed.

🧰 cURL Examples

Local base URL: http://127.0.0.1:8000

Analyze (GET):

curl -G "http://127.0.0.1:8000/v1/analyze" \
  --data-urlencode "transcript=We discussed migrating the database; Alice owns the rollout; ETA Friday."


Analyze (POST):

curl -X POST "http://127.0.0.1:8000/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "We discussed migrating the database; Alice owns the rollout; ETA Friday."}'


Get by ID:

curl "http://127.0.0.1:8000/v1/analyses/<PASTE_ID_HERE>"


Batch:

curl -X POST "http://127.0.0.1:8000/v1/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{"transcripts": ["First transcript...", "Second transcript..."]}'


Production base URL: https://sd-5035863-l.dattaweb.com/api8010
(Adjust examples by prefixing /api8010 before /v1/....)

🧯 Troubleshooting

Failed to instantiate OpenAI adapter...
Ensure .env is present with valid OPENAI_API_KEY and OPENAI_MODEL, and that app/configurations.py is loading them.
Example fix in app/dependencies.py:

from app.configurations import settings
OpenAIAdapter(api_key=settings.openai_api_key, model=settings.openai_model)


OpenAI errors (model not found / permissions)
Use a model your account can access. Update OPENAI_MODEL accordingly.

Empty transcript → 400
Provide non-empty text in the query/body.

Behind reverse proxy
If serving under a path prefix (e.g., /api8010), ensure your reverse proxy forwards to the FastAPI app and that you access Swagger at {BASE_URL}/docs with the correct prefix.

📝 Notes

Storage is in memory by design (no DB). Restarting the server clears saved analyses.

The adapter uses OpenAI’s structured outputs, ensuring a stable JSON shape matching our DTO: { summary: str, next_actions: List[str> }.

Costs apply when calling OpenAI; keep an eye on usage.

🧭 License

Internal project. Use per your organization’s policies.
