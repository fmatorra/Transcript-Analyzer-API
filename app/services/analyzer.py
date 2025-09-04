
import asyncio
from typing import Any, List, TYPE_CHECKING
from app.domain.models import TranscriptAnalysis
from app import prompts

# Import your port types only for type checking to avoid runtime errors if names differ
if TYPE_CHECKING: # adjust these names to match app/ports/llm.py
    from app.ports.llm import LLMPort # e.g., Protocol with a structured output call

class TranscriptAnalyzerService:
    def __init__(self, llm_adapter: Any): # runtime-agnostic; keep strict typing in TYPE_CHECKING above
        self._llm = llm_adapter


    async def analyze(self, transcript: str) -> TranscriptAnalysis:
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")

        # Call the provided OpenAI adapter with structured output to get summary + actions
        summary, actions = await self._call_llm_structured_output(transcript)
        analysis = TranscriptAnalysis.new(summary=summary, next_actions=actions)
        return analysis


    async def analyze_many(self, transcripts: List[str]) -> List[TranscriptAnalysis]:
        tasks = [self.analyze(t) for t in transcripts]
        return await asyncio.gather(*tasks)

    async def _call_llm_structured_output(self, transcript: str) -> tuple[str, List[str]]:
        """
        Integrates with the provided OpenAI adapter port using structured output.


        The adapter (per the task hints) accepts: system prompt, user prompt, a DTO
        definition (Pydantic model/type), and returns an instance populated per the DTO.


        >>> TODO: Replace the callable + argument names below to match *exactly* your app/ports/llm.py.
        We attempt a couple of common method names to reduce friction, while keeping
        the code explicit and easy to align.
        """

        from pydantic import BaseModel
        from typing import List as _List


        # Define the LLM structured output DTO locally to decouple layers
        class TranscriptAnalysisLLM(BaseModel):
            summary: str
            next_actions: _List[str]

        # Choose prompts from your repo (app/prompts.py). Adjust names if needed.
        try:
            system_prompt = prompts.SYSTEM_PROMPT # e.g., provided in your repo
        except AttributeError:
            system_prompt = "You are an assistant that summarizes transcripts and extracts next actions."

        try:
            user_prompt_tmpl = prompts.USER_PROMPT # may be a template string; assume it includes a {transcript}
        except AttributeError:
            user_prompt_tmpl = "Analyze the following transcript and return a short summary and 3-7 next actions.\n\nTranscript:\n{transcript}"

        user_prompt = user_prompt_tmpl.format(transcript=transcript)

        # Try a few conventional method names on the adapter. Align one to your port.
        candidates = [
            ("structured_output", dict(system_prompt=system_prompt, user_prompt=user_prompt, dto=TranscriptAnalysisLLM)),
            ("analyze", dict(system_prompt=system_prompt, user_prompt=user_prompt, dto=TranscriptAnalysisLLM)),
            ("run", dict(system_prompt=system_prompt, user_prompt=user_prompt, dto=TranscriptAnalysisLLM)),
            ("call", dict(system_prompt=system_prompt, user_prompt=user_prompt, dto=TranscriptAnalysisLLM)),
        ]

        result = None
        for name, kwargs in candidates:
            if hasattr(self._llm, name):
                maybe = getattr(self._llm, name)
                result = maybe(**kwargs)
                break
        
        # If the adapter returns a coroutine (async), await it; otherwise use it directly
        if asyncio.iscoroutine(result):
            result = await result


        if result is None:
            raise RuntimeError(
            "Could not call LLM adapter. Ensure app/ports/llm.py method name and signature are wired in services/analyzer.py"
            )


        # Validate type and extract
        if hasattr(result, "summary") and hasattr(result, "next_actions"):
            return result.summary, list(result.next_actions) # type: ignore[attr-defined]


        # If the adapter returns a dict-like
        if isinstance(result, dict):
            return result.get("summary", ""), list(result.get("next_actions", []))

        raise RuntimeError("Unexpected LLM adapter return type; expected DTO with 'summary' and 'next_actions'.")