"""Simpel søgning: et afsnit scorer ét point for hvert ord, det deler med spørgsmålet.

Ingen internet, ingen API-nøgle, ingen ekstra pakker.
Senere kan en embedding_index.py ligge ved siden af og søge på betydning i stedet.
"""
import re

from RAG.domain.models import Chunk, SearchResult

# Små ord, der står i næsten alle sætninger og derfor ikke siger noget om emnet.
STOP_WORDS = {
    "og", "i", "at", "er", "en", "et", "den", "det", "de", "til", "på", "med",
    "for", "som", "har", "man", "hos", "os", "vi", "jeg", "du", "hvor", "hvem",
    "hvad", "hvordan", "skal", "kan", "om", "af", "mange", "der", "ikke",
    # Engelske småord, fordi spørgsmålene stilles på engelsk.
    "the", "a", "an", "is", "are", "does", "do", "our", "we", "my", "it", "of", "to", "in", "and", "or", "what", "how",
}


def words(text: str) -> set[str]:
    """Gør teksten til et sæt af små bogstaver uden stopord."""
    return {w for w in re.findall(r"\w+", text.lower()) if w not in STOP_WORDS}


class KeywordIndex:

    def __init__(self):
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        # 8: GEM I INDEKS: Afsnittene gemmes bare i en liste i hukommelsen.
        self.chunks.extend(chunks)

    def search(self, query: str, k: int) -> list[SearchResult]:
        # 16b: SØG: Hvert afsnit får ét point pr. ord, det deler med søgningen.
        query_words = words(query)

        results = []
        for chunk in self.chunks:
            score = len(query_words & words(chunk.text))
            if score > 0:
                results.append(SearchResult(chunk=chunk, score=score))

        # Bedste resultater først, og kun de k bedste.
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]
