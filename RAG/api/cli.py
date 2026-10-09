"""Kommandolinjen til RAG-laget.

Kør fra projektets rod:
    python -m RAG.api.cli "Hvor mange feriedage har man?" --fake
    python -m RAG.api.cli "Hvor mange feriedage har man?"
"""
import argparse

from LLM.application.llm_service import LLMService
from RAG.application.ingest_service import IngestService
from RAG.application.query_service import QueryService
from RAG.config import settings
from RAG.infrastructure.chunking.text_chunker import ParagraphChunker
from RAG.infrastructure.index.keyword_index import KeywordIndex
from RAG.infrastructure.loaders.markdown_loader import MarkdownLoader


def build_llm(fake: bool) -> LLMService:
    # Samme valg som i LLM-laget: falsk eller rigtig kok.
    if fake:
        from LLM.infrastructure.providers.fake_provider import FakeProvider
        provider = FakeProvider()
    else:
        from LLM.infrastructure.providers.anthropic_provider import AnthropicProvider
        provider = AnthropicProvider()
    return LLMService(provider, system="Svar kort på dansk.")


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--fake", action="store_true", help="Brug falsk model, ingen API-nøgle")
    args = parser.parse_args()

    # 2. Vælg delene. Det er det eneste sted i laget, hvor det sker.
    loader = MarkdownLoader(settings.DOCS_FOLDER)
    chunker = ParagraphChunker()
    index = KeywordIndex()

    # 3. Læg dokumenterne i indekset.
    count = IngestService(loader, chunker, index).run()
    print(f"Indlæste {count} afsnit fra {settings.DOCS_FOLDER.name}/\n")

    # 4. Stil spørgsmålet.
    query = QueryService(index, build_llm(args.fake), k=settings.TOP_K)
    answer = query.ask(args.question)

    # 5. Vis kilderne og svaret.
    print("Fundne afsnit:")
    for result in answer.sources:
        print(f"  [{result.chunk.source}] (score {result.score:g}) {result.chunk.text}")
    if not answer.sources:
        print("  (ingen)")

    print(f"\nSvar:\n{answer.text}")


if __name__ == "__main__":
    main()
