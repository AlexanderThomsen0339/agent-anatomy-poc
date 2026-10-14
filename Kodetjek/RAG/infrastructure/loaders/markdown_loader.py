"""Læser alle .md-filer fra en mappe."""
from pathlib import Path

from RAG.domain.models import Document


class MarkdownLoader:

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def load(self) -> list[Document]:
        documents = []
        for file in sorted(self.folder.glob("*.md")):
            text = file.read_text(encoding="utf-8")
            documents.append(Document(source=file.name, text=text))
        return documents
