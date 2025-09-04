
from typing import List, Optional
from pydantic import BaseModel, Field


class AnalyzeQuery(BaseModel):
    transcript: str = Field(..., description="Plain text transcript to analyze")


class AnalyzeBody(BaseModel):
    transcript: str = Field(..., description="Plain text transcript to analyze")


class BatchAnalyzeBody(BaseModel):
    transcripts: List[str] = Field(..., description="List of transcripts to analyze concurrently (async)")


class AnalysisResponse(BaseModel):
    id: str
    summary: str
    next_actions: List[str]


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None