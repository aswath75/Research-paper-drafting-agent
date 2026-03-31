from __future__ import annotations

from app.models.schemas import SectionPlan
from app.services.llm_service import llm_service


class PlannerAgent:
    async def plan(self, topic: str, outline: str, provider: str | None = None) -> list[SectionPlan]:
        prompt = (
            "Create a JSON object with key `sections` containing academic paper sections.\n"
            "Each section needs `name`, `objective`, and `key_points`.\n"
            f"Topic: {topic}\nOutline:\n{outline}"
        )
        response = await llm_service.generate_json(prompt, provider)
        sections = response.get("sections") if response else None
        if sections:
            return [SectionPlan(**section) for section in sections]
        return self._fallback_plan(outline)

    def _fallback_plan(self, outline: str) -> list[SectionPlan]:
        raw_sections = [line.strip("-* \t") for line in outline.splitlines() if line.strip()]
        if not raw_sections:
            raw_sections = ["Abstract", "Introduction", "Methodology", "Results", "Discussion", "Conclusion"]
        return [
            SectionPlan(
                name=section,
                objective=f"Develop the {section.lower()} for the paper with a clear academic tone.",
                key_points=[f"Address the core goal of {section}.", "Use evidence-backed arguments.", "Keep citations explicit."],
            )
            for section in raw_sections
        ]


planner_agent = PlannerAgent()
