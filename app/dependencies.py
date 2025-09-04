
from functools import lru_cache
from app.repositories.memory import InMemoryTranscriptRepository
from app.services.analyzer import TranscriptAnalyzerService


@lru_cache(maxsize=1)
def get_repository() -> InMemoryTranscriptRepository:
    # Single in-memory repo instance for the process lifetime
    return InMemoryTranscriptRepository()


@lru_cache(maxsize=1)
def get_llm_adapter():
    """Instantiate the provided OpenAI adapter that conforms to app/ports/llm.py.


    Adjust the class import below to match the concrete adapter implementation.
    """
    try:
        from app.adapters.openai import OpenAIAdapter # <-- align to your adapter class name
        return OpenAIAdapter()
    except Exception as exc: # ImportError or constructor errors
        raise RuntimeError(
        "Failed to instantiate OpenAI adapter. Ensure app/adapters/openai.py exposes `OpenAIAdapter`."
        ) from exc


@lru_cache(maxsize=1)
def get_analyzer_service() -> TranscriptAnalyzerService:
    return TranscriptAnalyzerService(get_llm_adapter())