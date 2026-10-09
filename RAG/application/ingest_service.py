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
        documents = self.loader.load()

        chunks = []
        for document in documents:
            chunks.extend(self.chunker.split(document))

        self.index.add(chunks)
        return len(chunks)
