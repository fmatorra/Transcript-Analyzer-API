
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="Transcript Analyzer API",
    version="1.0.0",
    description=(
    "Analyzes plain text transcripts using an LLM (via provided OpenAI adapter) and returns a summary and next actions."
    ),
    root_path="/api8010",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1")

@app.get("/health")
def health():
    return {"status": "ok"}