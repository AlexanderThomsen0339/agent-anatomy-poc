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
        # PDF'er uden tekst, fx skannede sider. Dem kan søgningen ikke finde noget i, så de vises ved start.
        self.files_without_text: list[str] = []

    def load(self) -> list[Document]:
        documents = []
        # Hvorfor også undermapper og .PDF med store bogstaver? Dokumenter bliver ofte lagt ind i den mappestruktur, de kom med.
        files = sorted(f for f in self.folder.rglob("*") if f.is_file() and f.suffix.lower() == ".pdf")
        for file in files:
            name = file.relative_to(self.folder).as_posix()
            before = len(documents)
            try:
                for number, page in enumerate(PdfReader(file).pages, start=1):
                    # Hvorfor samle teksten på én linje?
                    # ParagraphChunker deler ved tomme linjer, og en side skal være ét afsnit.
                    # Linjeskift midt i en sætning ville også dele ord som "BERAN backup" over to linjer.
                    text = " ".join((page.extract_text() or "").split())
                    if text:
                        documents.append(Document(source=f"{name} › page {number}", text=text))
            except Exception as e:
                # En ødelagt eller krypteret PDF må ikke stoppe resten. Den vises ved start i stedet.
                self.files_without_text.append(f"{name} ({type(e).__name__})")
                continue
            if len(documents) == before:
                self.files_without_text.append(name)
        return documents
