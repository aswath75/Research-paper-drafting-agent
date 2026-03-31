from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from app.core.config import settings
from app.models.schemas import ReferenceItem


class CitationVerificationService:
    async def verify(self, references: list[ReferenceItem]) -> list[ReferenceItem]:
        async with httpx.AsyncClient(timeout=10) as client:
            verified_items: list[ReferenceItem] = []
            for item in references:
                verified_items.append(await self._verify_single(item, client))
            return verified_items

    async def _verify_single(self, reference: ReferenceItem, client: httpx.AsyncClient) -> ReferenceItem:
        query = reference.title or reference.raw
        if not query.strip():
            return reference.model_copy(update={"message": "Reference is empty."})

        url = f"{settings.crossref_base_url}?query.title={quote_plus(query)}&rows=1"
        try:
            response = await client.get(url, headers={"User-Agent": "research-drafter/1.0"})
            response.raise_for_status()
            items = response.json().get("message", {}).get("items", [])
            if not items:
                return reference.model_copy(
                    update={"verified": False, "source": "Crossref", "message": "No citation match found."}
                )

            match = items[0]
            title_list = match.get("title") or []
            title = title_list[0] if title_list else query
            score = float(match.get("score") or 0.0)
            doi = match.get("DOI")
            return reference.model_copy(
                update={
                    "verified": score > 20,
                    "source": "Crossref",
                    "title": title,
                    "url": f"https://doi.org/{doi}" if doi else reference.url,
                    "match_score": score,
                    "message": "Verified against Crossref." if score > 20 else "Low-confidence citation match.",
                }
            )
        except httpx.HTTPError:
            return reference.model_copy(
                update={"verified": False, "source": "Crossref", "message": "Verification service unavailable."}
            )


citation_verification_service = CitationVerificationService()
