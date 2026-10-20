"""Læser kravspecifikationer fra alle .md-filer i en mappe.

Hver fil bliver ét dokument. Hvert krav står som sin egen blok adskilt af en tom linje,
så ParagraphChunker deler dem op med ét krav pr. afsnit, ligesom user stories i xlsx.
"""
from pathlib import Path

from RAG.domain.models import Document


class MarkdownLoader:

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def load(self) -> list[Document]:
        # 6b: LÆS KRAVSPEC: Hver .md-fil bliver til ét dokument.
        return [
            Document(source=file.name, text=file.read_text(encoding="utf-8"))
            for file in sorted(self.folder.glob("*.md"))
        ]
