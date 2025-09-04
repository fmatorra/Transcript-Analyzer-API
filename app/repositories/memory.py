
from typing import Dict, Optional
from threading import RLock
from app.domain.models import TranscriptAnalysis


class InMemoryTranscriptRepository:
    """Thread-safe in-memory storage for transcript analyses."""
    def __init__(self) -> None:
        self._store: Dict[str, TranscriptAnalysis] = {}
        self._lock = RLock()


    def save(self, analysis: TranscriptAnalysis) -> None:
        with self._lock:
            self._store[analysis.id] = analysis


    def get(self, analysis_id: str) -> Optional[TranscriptAnalysis]:
        with self._lock:
            return self._store.get(analysis_id)