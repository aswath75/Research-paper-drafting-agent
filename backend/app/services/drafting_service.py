from __future__ import annotations

from app.agents.citation import citation_agent
from app.agents.planner import planner_agent
from app.agents.reviewer import reviewer_agent
from app.agents.writer import writer_agent
from app.db.mongo import mongo_repository
from app.models.schemas import (
    DraftDocument,
    DraftResponse,
    DraftSection,
    GenerateDraftRequest,
    GenerateSectionRequest,
    ReferenceItem,
)
from app.services.citation_service import citation_verification_service
from app.services.export_service import build_latex, build_markdown


class DraftingService:
    def parse_references(self, raw_references: str) -> list[ReferenceItem]:
        parsed: list[ReferenceItem] = []
        for line in raw_references.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            parsed.append(
                ReferenceItem(
                    raw=cleaned,
                    url=cleaned if cleaned.startswith(("http://", "https://")) else None,
                )
            )
        return parsed

    async def generate_full_draft(self, payload: GenerateDraftRequest) -> DraftResponse:
        references = self.parse_references(payload.references)
        plan = await planner_agent.plan(payload.topic, payload.outline, payload.provider)

        sections: list[DraftSection] = []
        for section_plan in plan:
            sections.append(await writer_agent.write_section(payload.topic, section_plan, references, payload.provider))

        sections = citation_agent.enrich(sections, references)
        verified_references = await citation_verification_service.verify(references) if references else references
        reviewed_sections, metrics = reviewer_agent.review(sections, verified_references)
        markdown = build_markdown(payload.topic, reviewed_sections, verified_references)
        latex = build_latex(payload.topic, reviewed_sections, verified_references)

        document = DraftDocument(
            topic=payload.topic,
            outline=payload.outline,
            references=verified_references,
            sections=reviewed_sections,
            markdown=markdown,
            latex=latex,
            metrics=metrics,
            status_steps=["Planning", "Writing", "Reviewing", "Citation Checking"],
        )
        inserted_id = await mongo_repository.save_draft(document.model_dump(mode="json"))
        saved_document = document.model_copy(update={"id": inserted_id})
        return DraftResponse(document=saved_document, section_names=[section.name for section in reviewed_sections])

    async def generate_section(self, payload: GenerateSectionRequest) -> DraftSection:
        references = self.parse_references(payload.references)
        fallback_outline = payload.outline or payload.section_name
        section_plan = (await planner_agent.plan(payload.topic, fallback_outline, payload.provider))[0]
        if section_plan.name.lower() != payload.section_name.lower():
            section_plan = section_plan.model_copy(update={"name": payload.section_name})
        generated_section = await writer_agent.write_section(payload.topic, section_plan, references, payload.provider)
        enriched_section = citation_agent.enrich([generated_section], references)[0]
        reviewed_sections, _ = reviewer_agent.review([enriched_section], references)
        return reviewed_sections[0]

    async def verify_citations(self, references: list[ReferenceItem]) -> list[ReferenceItem]:
        return await citation_verification_service.verify(references)


drafting_service = DraftingService()
