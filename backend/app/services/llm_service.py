from __future__ import annotations

import json
import re
from typing import Any

from google import genai
from openai import AsyncOpenAI

from app.core.config import settings


class LLMService:
    async def generate_json(self, prompt: str, provider: str | None = None) -> dict[str, Any]:
        selected_provider = provider or settings.llm_provider
        try:
            if selected_provider == "openai" and settings.openai_api_key:
                return await self._generate_openai_json(prompt)
            if selected_provider == "gemini" and settings.gemini_api_key:
                return await self._generate_gemini_json(prompt)
        except Exception:
            return {}
        return {}

    async def _generate_openai_json(self, prompt: str) -> dict[str, Any]:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": "Return strictly valid JSON matching the requested schema.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        text = response.output_text
        return self._parse_json_object(text)

    async def _generate_gemini_json(self, prompt: str) -> dict[str, Any]:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=f"Return strictly valid JSON.\n{prompt}",
        )
        text = response.text
        return self._parse_json_object(text)

    def _parse_json_object(self, text: str | None) -> dict[str, Any]:
        if not text:
            return {}

        stripped = text.strip()
        if not stripped:
            return {}

        candidates = [stripped]

        fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
        if fenced_match:
            candidates.insert(0, fenced_match.group(1).strip())

        first_brace = stripped.find("{")
        last_brace = stripped.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidates.append(stripped[first_brace : last_brace + 1])

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                continue

        return {}


llm_service = LLMService()
