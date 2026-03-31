from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import (
    CitationVerificationResponse,
    DraftResponse,
    ExportRequest,
    GenerateDraftRequest,
    GenerateSectionRequest,
    UploadPdfResponse,
    VerifyCitationsRequest,
)
from app.services.drafting_service import drafting_service
from app.services.export_service import build_latex, build_markdown
from app.services.pdf_service import extract_references_from_pdf


router = APIRouter()


@router.post("/generate-full", response_model=DraftResponse)
async def generate_full(payload: GenerateDraftRequest):
    try:
        return await drafting_service.generate_full_draft(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to generate draft: {exc}") from exc


@router.post("/generate-section")
async def generate_section(payload: GenerateSectionRequest):
    try:
        return await drafting_service.generate_section(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to generate section: {exc}") from exc


@router.post("/verify-citations", response_model=CitationVerificationResponse)
async def verify_citations(payload: VerifyCitationsRequest):
    try:
        verified = await drafting_service.verify_citations(payload.references)
        accuracy = round(
            (sum(1 for item in verified if item.verified) / len(verified)) * 100, 1
        ) if verified else 0.0
        return CitationVerificationResponse(references=verified, citation_accuracy=accuracy)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Citation verification failed: {exc}") from exc


@router.post("/export-md")
async def export_markdown(payload: ExportRequest):
    return {"content": build_markdown(payload.topic, payload.sections, payload.references)}


@router.post("/export-latex")
async def export_latex(payload: ExportRequest):
    return {"content": build_latex(payload.topic, payload.sections, payload.references)}


@router.post("/upload-pdf", response_model=UploadPdfResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")
    try:
        extracted = extract_references_from_pdf(await file.read())
        return UploadPdfResponse(extracted_references=extracted)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not extract references from PDF: {exc}") from exc
