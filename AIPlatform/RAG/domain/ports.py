"""Porte for RAG-laget.

Hver port er en kontrakt for én ting, laget har brug for udefra.
Implementeringerne ligger i infrastructure/.
"""

# Hvorfor Protocol?
# En adapter skal bare have de rigtige metoder,
# den behøver ikke arve fra noget.
from typing import Protocol

from .models import Chunk, Document, SearchResult


# Hvorfor en port til indlæsning?
# I dag læser vi .md-filer fra en mappe. I morgen kan det være PDF'er,
# SharePoint eller en database. Resten af laget skal ikke mærke forskel.
class DocumentLoader(Protocol):
    def load(self) -> list[Document]:
        """Henter alle dokumenter."""
        ...


# Hvorfor en port til opdeling?
# Hvordan man bedst deler tekst op, afhænger af teksten: afsnit, overskrifter,
# et fast antal ord. Det er noget, man vil eksperimentere med uden at røre resten.
class Chunker(Protocol):
    def split(self, document: Document) -> list[Chunk]:
        """Deler ét dokument op i afsnit."""
        ...


# Hvorfor én port til både at tilføje og søge?
# Det er samme "kartotek": det, der lægges ind, er det, der søges i.
# Skiftes ordsøgning ud med søgning på betydning (embeddings), skiftes begge dele.
class SearchIndex(Protocol):
    def add(self, chunks: list[Chunk]) -> None:
        """Lægger afsnit i indekset."""
        ...

    def search(self, query: str, k: int) -> list[SearchResult]:
        """Finder de k afsnit, der passer bedst til forespørgslen."""
        ...
