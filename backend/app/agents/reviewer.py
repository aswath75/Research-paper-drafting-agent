from __future__ import annotations

import re

from app.models.schemas import DraftSection, EvaluationMetrics, ReferenceItem


class ReviewerAgent:
    def review(self, sections: list[DraftSection], references: list[ReferenceItem]) -> tuple[list[DraftSection], EvaluationMetrics]:
        reviewed_sections = [
            section.model_copy(
                update={
                    "content": self._polish(section.content),
                    "status": "reviewed",
                }
            )
            for section in sections
        ]
        citation_accuracy = self._citation_accuracy(reviewed_sections, references)
        completeness = 100.0 if reviewed_sections else 0.0
        readability = self._readability(reviewed_sections)
        quality = round((readability * 0.35) + (citation_accuracy * 0.35) + (completeness * 0.30), 1)
        metrics = EvaluationMetrics(
            readability_score=readability,
            citation_accuracy=citation_accuracy,
            structure_completeness=completeness,
            estimated_quality=quality,
        )
        return reviewed_sections, metrics

    def _polish(self, content: str) -> str:
        polished = re.sub(r"\s+", " ", content).strip()
        return polished.replace(" .", ".")

    def _citation_accuracy(self, sections: list[DraftSection], references: list[ReferenceItem]) -> float:
        if not references:
            return 55.0
        valid_labels = {f"[{index + 1}]" for index, _ in enumerate(references)}
        cited_labels = [label for section in sections for label in section.citations]
        if not cited_labels:
            return 40.0
        accurate = sum(1 for label in cited_labels if label in valid_labels)
        return round((accurate / len(cited_labels)) * 100, 1)

    def _readability(self, sections: list[DraftSection]) -> float:
        text = " ".join(section.content for section in sections)
        word_count = len(text.split())
        sentence_count = max(text.count("."), 1)
        average_sentence_length = word_count / sentence_count
        return round(max(45.0, min(95.0, 100 - average_sentence_length)), 1)


reviewer_agent = ReviewerAgent()
