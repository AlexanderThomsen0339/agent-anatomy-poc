"""IngestService: læser dokumenterne og lægger dem i indekset."""
from RAG.domain.ports import Chunker, DocumentLoader, SearchIndex


class IngestService:

    def __init__(self, loader: DocumentLoader, chunker: Chunker, index: SearchIndex):
        # Vi får alle tre dele udefra. Servicen er ligeglad med, hvilke det er.
        self.loader = loader
        self.chunker = chunker
        self.index = index

    def run(self) -> int:
        """Indlæs → del op → læg i indeks. Returnerer antal afsnit."""
        # 5: INDLÆS KRAV: Tre trin efter hinanden.

        # 6: LÆS XLSX: Fortsæt i RAG/infrastructure/loaders/xlsx_loader.py.
        documents = self.loader.load()

        # 7: DEL OP: Fortsæt i RAG/infrastructure/chunking/text_chunker.py.
        chunks = []
        for document in documents:
            chunks.extend(self.chunker.split(document))

        # 8: GEM I INDEKS: Fortsæt i RAG/infrastructure/index/keyword_index.py. Tilbage til MCP/api/build.py.
        self.index.add(chunks)
        return len(chunks)
