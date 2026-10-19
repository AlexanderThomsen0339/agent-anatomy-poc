"""Deler et dokument op i afsnit ved tomme linjer."""
from RAG.domain.models import Chunk, Document


class ParagraphChunker:

    def split(self, document: Document) -> list[Chunk]:
        # 7: DEL OP: Hver user story og hver testcase bliver ét afsnit (en chunk).
        chunks = []
        for paragraph in document.text.split("\n\n"):
            text = paragraph.strip()

            # Spring tomme afsnit og rene overskrifter over. De indeholder ikke svar.
            if not text or text.startswith("#"):
                continue

            chunks.append(Chunk(source=document.source, text=text, position=len(chunks)))
        return chunks
