from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def extract_references_from_pdf(file_bytes: bytes) -> list[str]:
    reader = PdfReader(BytesIO(file_bytes))
    text = "\n".join(filter(None, (page.extract_text() for page in reader.pages)))
    if not text.strip():
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    collected: list[str] = []
    capture = False
    for line in lines:
        lower = line.lower()
        if "references" in lower or "bibliography" in lower:
            capture = True
            continue
        if capture:
            if len(collected) >= 15:
                break
            collected.append(line)
    return collected
