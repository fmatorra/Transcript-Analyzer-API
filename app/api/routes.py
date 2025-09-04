import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.api import AnalyzeQuery, AnalyzeBody, AnalysisResponse, ErrorResponse, BatchAnalyzeBody
from app.services.analyzer import TranscriptAnalyzerService
from app.repositories.memory import InMemoryTranscriptRepository
from app.dependencies import get_analyzer_service, get_repository

router = APIRouter()


@router.get("/analyze", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
async def analyze_transcript_get(
    query: AnalyzeQuery = Depends(),
    service: TranscriptAnalyzerService = Depends(get_analyzer_service),
    repo: InMemoryTranscriptRepository = Depends(get_repository),
):
    try:
        analysis = await service.analyze(query.transcript)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


    repo.save(analysis)
    return AnalysisResponse(id=analysis.id, summary=analysis.summary, next_actions=analysis.next_actions)




@router.post("/analyze", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
async def analyze_transcript_post(
    body: AnalyzeBody,
    service: TranscriptAnalyzerService = Depends(get_analyzer_service),
    repo: InMemoryTranscriptRepository = Depends(get_repository),
):
    try:
        analysis = await service.analyze(body.transcript)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    repo.save(analysis)
    return AnalysisResponse(id=analysis.id, summary=analysis.summary, next_actions=analysis.next_actions)


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse, responses={404: {"model": ErrorResponse}})
async def get_analysis_by_id(
    analysis_id: str,
    repo: InMemoryTranscriptRepository = Depends(get_repository),
):
    analysis = repo.get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return AnalysisResponse(id=analysis.id, summary=analysis.summary, next_actions=analysis.next_actions)


@router.post("/analyze/batch", response_model=list[AnalysisResponse], responses={400: {"model": ErrorResponse}})
async def analyze_batch(
    body: BatchAnalyzeBody,
    service: TranscriptAnalyzerService = Depends(get_analyzer_service),
    repo: InMemoryTranscriptRepository = Depends(get_repository),
):
    transcripts = [t for t in (body.transcripts or []) if t and t.strip()]
    if not transcripts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide at least one non-empty transcript")

    analyses = await service.analyze_many(transcripts)
    for a in analyses:
        repo.save(a)


    return [AnalysisResponse(id=a.id, summary=a.summary, next_actions=a.next_actions) for a in analyses]