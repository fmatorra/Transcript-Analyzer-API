
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4
from datetime import datetime, timezone


@dataclass(frozen=True)
class TranscriptAnalysis:
    id: str
    summary: str
    next_actions: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def new(summary: str, next_actions: List[str]) -> "TranscriptAnalysis":
        return TranscriptAnalysis(id=str(uuid4()), summary=summary, next_actions=next_actions)