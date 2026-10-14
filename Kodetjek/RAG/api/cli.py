"""Kommandolinjen til RAG-laget.

Kør fra Kodetjek-mappen:
    python -m RAG.api.cli "Hvad er acceptkriterierne for download af faktura?" --fake
    python -m RAG.api.cli "Hvad er acceptkriterierne for download af faktura?"
"""
import argparse

import settings
from LLM.application.llm_service import LLMService
from RAG.application.ingest_service import IngestService
from RAG.application.query_service import QueryService
from RAG.infrastructure.chunking.text_chunker import ParagraphChunker
from RAG.infrastructure.index.keyword_index import KeywordIndex
from RAG.infrastructure.loaders.xlsx_loader import XlsxLoader


def build_llm(fake: bool) -> LLMService:
    # Samme valg som i LLM-laget: falsk eller rigtig kok.
    if fake:
        from LLM.infrastructure.providers.fake_provider import FakeProvider
        provider = FakeProvider()
    else:
        from LLM.infrastructure.providers.anthropic_provider import AnthropicProvider
        provider = AnthropicProvider(model=settings.MODEL)
    return LLMService(provider, system=settings.LLM_SYSTEM_PROMPT)


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--fake", action="store_true", help="Use a fake model, no API key")
    args = parser.parse_args()

    # 2. Vælg delene. Det er det eneste sted i laget, hvor det sker.
    loader = XlsxLoader(settings.DATA_FOLDER)
    chunker = ParagraphChunker()
    index = KeywordIndex()

    # 3. Læg dokumenterne i indekset.
    count = IngestService(loader, chunker, index).run()
    print(f"Loaded {count} chunks from {settings.DATA_FOLDER.name}/\n")

    # 4. Stil spørgsmålet.
    query = QueryService(index, build_llm(args.fake), k=settings.TOP_K)
    answer = query.ask(args.question)

    # 5. Vis kilderne og svaret.
    print("Chunks found:")
    for result in answer.sources:
        print(f"  [{result.chunk.source}] (score {result.score:g}) {result.chunk.text}")
    if not answer.sources:
        print("  (none)")

    print(f"\nAnswer:\n{answer.text}")


if __name__ == "__main__":
    main()
