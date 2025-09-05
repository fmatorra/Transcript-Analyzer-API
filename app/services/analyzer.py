import asyncio
from typing import Any, List
from pydantic import BaseModel
from app.domain.models import TranscriptAnalysis
from app import prompts

class TranscriptAnalyzerService:
    def __init__(self, llm_adapter: Any):
        self._llm = llm_adapter

    async def analyze(self, transcript: str) -> TranscriptAnalysis:
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")
        summary, actions = await self._call_llm_structured_output(transcript)
        return TranscriptAnalysis.new(summary=summary, next_actions=actions)

    async def analyze_many(self, transcripts: List[str]) -> List[TranscriptAnalysis]:
        tasks = [self.analyze(t) for t in transcripts]
        return await asyncio.gather(*tasks)

    async def _call_llm_structured_output(self, transcript: str) -> tuple[str, List[str]]:
        # DTO the adapter will fill using structured output
        class TranscriptAnalysisLLM(BaseModel):
            summary: str
            next_actions: List[str]

        # Prompts
        system_prompt = getattr(
            prompts, "SYSTEM_PROMPT",
            "You summarize transcripts and extract concrete next actions."
        )
        user_prompt_tmpl = getattr(
            prompts, "USER_PROMPT",
            "Analyze the following transcript. Return a concise summary and 3–7 actionable next steps.\n\nTranscript:\n{transcript}"
        )
        user_prompt = user_prompt_tmpl.format(transcript=transcript)

        # Prefer async if your adapter exposes it
        if hasattr(self._llm, "run_completion_async"):
            result = await self._llm.run_completion_async(system_prompt, user_prompt, TranscriptAnalysisLLM)  # type: ignore[attr-defined]
        else:
            # Call sync method without blocking the event loop
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._llm.run_completion(system_prompt, user_prompt, TranscriptAnalysisLLM),
            )

        # Normalize result
        if isinstance(result, TranscriptAnalysisLLM):
            return result.summary, list(result.next_actions)
        if isinstance(result, dict):
            return result.get("summary", ""), list(result.get("next_actions", []))
        return getattr(result, "summary", ""), list(getattr(result, "next_actions", []))