"""Læser OT's PDF-dokumenter: alle .pdf-filer i en mappe.

Hver side bliver ét dokument med kilden "fil.pdf › page 3", så et svar kan pege på den side, hvor teksten står.
Hvorfor pr. side? En PDF kan være hundrede sider. Én side er lille nok til at søge i
og præcis nok til, at man kan slå op i dokumentet bagefter.
"""
from pathlib import Path

from pypdf import PdfReader

from RAG.domain.models import Document


class PdfLoader:

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def load(self) -> list[Document]:
        documents = []
        for file in sorted(self.folder.glob("*.pdf")):
            for number, page in enumerate(PdfReader(file).pages, start=1):
                # Hvorfor samle teksten på én linje?
                # ParagraphChunker deler ved tomme linjer, og en side skal være ét afsnit.
                # Linjeskift midt i en sætning ville også dele ord som "BERAN backup" over to linjer.
                text = " ".join((page.extract_text() or "").split())
                if text:
                    documents.append(Document(source=f"{file.name} › page {number}", text=text))
        return documents
