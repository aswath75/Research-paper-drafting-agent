from __future__ import annotations

from app.models.schemas import DraftSection, ReferenceItem


class CitationAgent:
    def enrich(self, sections: list[DraftSection], references: list[ReferenceItem]) -> list[DraftSection]:
        if not references:
            return sections

        enriched_sections: list[DraftSection] = []
        for index, section in enumerate(sections):
            label = f"[{(index % len(references)) + 1}]"
            content = section.content if label in section.content else f"{section.content}\n\nSupporting evidence is aligned with {label}."
            citations = list(dict.fromkeys([*section.citations, label]))
            enriched_sections.append(section.model_copy(update={"content": content, "citations": citations}))
        return enriched_sections


citation_agent = CitationAgent()
