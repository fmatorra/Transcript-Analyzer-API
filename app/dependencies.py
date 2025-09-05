
from functools import lru_cache
from app.repositories.memory import InMemoryTranscriptRepository
from app.services.analyzer import TranscriptAnalyzerService
from app.configurations import settings

@lru_cache(maxsize=1)
def get_repository() -> InMemoryTranscriptRepository:
    # Single in-memory repo instance for the process lifetime
    return InMemoryTranscriptRepository()


@lru_cache(maxsize=1)
def get_llm_adapter():
    """
    Instantiate the provided OpenAI adapter that conforms to app/ports/llm.py.
    """
    try:
        from app.adapters.openai import OpenAIAdapter
        return OpenAIAdapter(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
        )
    except Exception as exc:
        # Bubble a clear, actionable message
        raise RuntimeError(
            "Failed to instantiate OpenAI adapter. "
            "Check that app/adapters/openai.py exposes `OpenAIAdapter` and that "
            "OPENAI_API_KEY / OPENAI_MODEL are set."
        ) from exc


@lru_cache(maxsize=1)
def get_analyzer_service() -> TranscriptAnalyzerService:
    return TranscriptAnalyzerService(get_llm_adapter())