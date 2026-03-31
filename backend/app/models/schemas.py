from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ReferenceItem(BaseModel):
    raw: str
    title: str | None = None
    url: str | None = None
    verified: bool = False
    source: str | None = None
    match_score: float | None = None
    message: str | None = None


class SectionPlan(BaseModel):
    name: str
    objective: str
    key_points: list[str] = Field(default_factory=list)


class DraftSection(BaseModel):
    name: str
    content: str
    citations: list[str] = Field(default_factory=list)
    status: Literal["generated", "reviewed"] = "generated"


class EvaluationMetrics(BaseModel):
    readability_score: float
    citation_accuracy: float
    structure_completeness: float
    estimated_quality: float


class DraftDocument(BaseModel):
    id: str | None = None
    topic: str
    outline: str
    references: list[ReferenceItem] = Field(default_factory=list)
    sections: list[DraftSection] = Field(default_factory=list)
    markdown: str
    latex: str
    metrics: EvaluationMetrics
    status_steps: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GenerateDraftRequest(BaseModel):
    topic: str = Field(min_length=3)
    outline: str = Field(min_length=3)
    references: str = ""
    provider: Literal["mock", "openai", "gemini"] | None = None


class GenerateSectionRequest(GenerateDraftRequest):
    section_name: str = Field(min_length=2)


class VerifyCitationsRequest(BaseModel):
    topic: str = ""
    references: list[ReferenceItem]


class ExportRequest(BaseModel):
    topic: str
    sections: list[DraftSection]
    references: list[ReferenceItem] = Field(default_factory=list)


class UploadPdfResponse(BaseModel):
    extracted_references: list[str]


class DraftResponse(BaseModel):
    document: DraftDocument
    section_names: list[str] = Field(default_factory=list)


class CitationVerificationResponse(BaseModel):
    references: list[ReferenceItem] = Field(default_factory=list)
    citation_accuracy: float
