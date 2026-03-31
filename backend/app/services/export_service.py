from __future__ import annotations

import re

from app.models.schemas import DraftSection, ReferenceItem


def _sanitize_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def _normalize_section_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", "", name).strip()
    return cleaned or "Section"


def build_markdown(topic: str, sections: list[DraftSection], references: list[ReferenceItem]) -> str:
    section_text = "\n\n".join([f"## {section.name}\n\n{section.content}" for section in sections])
    reference_lines = "\n".join([f"- {ref.title or ref.raw}" for ref in references]) or "- No references provided"
    return f"# {topic}\n\n{section_text}\n\n## References\n\n{reference_lines}\n"


def build_latex(topic: str, sections: list[DraftSection], references: list[ReferenceItem]) -> str:
    latex_sections = "\n".join(
        [f"\\section{{{_normalize_section_name(section.name)}}}\n{_sanitize_latex(section.content)}" for section in sections]
    )
    bibliography = "\n".join(
        [f"\\bibitem{{ref{index + 1}}} {_sanitize_latex(ref.title or ref.raw)}" for index, ref in enumerate(references)]
    )
    return (
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\title{" + _sanitize_latex(topic) + "}\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        f"{latex_sections}\n"
        "\\begin{thebibliography}{99}\n"
        f"{bibliography}\n"
        "\\end{thebibliography}\n"
        "\\end{document}\n"
    )
