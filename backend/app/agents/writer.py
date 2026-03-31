from __future__ import annotations

from app.models.schemas import DraftSection, ReferenceItem, SectionPlan
from app.services.llm_service import llm_service


class WriterAgent:
    async def write_section(
        self,
        topic: str,
        section_plan: SectionPlan,
        references: list[ReferenceItem],
        provider: str | None = None,
    ) -> DraftSection:
        prompt = (
            "Create a JSON object with keys `content` and `citations`.\n"
            "Write academically, 2-4 paragraphs, and cite references using bracketed labels like [1].\n"
            f"Topic: {topic}\n"
            f"Section: {section_plan.model_dump_json()}\n"
            f"References: {[ref.title or ref.raw for ref in references]}"
        )
        response = await llm_service.generate_json(prompt, provider)
        if response.get("content"):
            return DraftSection(
                name=section_plan.name,
                content=response["content"],
                citations=response.get("citations", []),
            )
        return self._fallback_write(topic, section_plan, references)

    def _fallback_write(
        self,
        topic: str,
        section_plan: SectionPlan,
        references: list[ReferenceItem],
    ) -> DraftSection:
        citation_labels = [f"[{index + 1}]" for index, _ in enumerate(references[:3])]
        citations_text = " ".join(citation_labels) if citation_labels else "[No external citations supplied]"
        bullet_points = " ".join(section_plan.key_points[:3])
        content = (
            f"{section_plan.name} frames the discussion around {topic.lower()} with a concise academic voice. "
            f"It focuses on {section_plan.objective.lower()} {citations_text}\n\n"
            f"This section develops the following priorities: {bullet_points} "
            "It is drafted to remain easy to refine section-by-section during iterative review."
        )
        return DraftSection(name=section_plan.name, content=content, citations=citation_labels)


writer_agent = WriterAgent()
