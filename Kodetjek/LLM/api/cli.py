"""Kommandolinjen til LLM-laget.

Kør fra projektets rod:
    python -m LLM.api.cli "Hvad er en LLM?"
    python -m LLM.api.cli "Hvad er en LLM?" --stream
    python -m LLM.api.cli "Hvad er en LLM?" --fake
"""
import argparse

import settings

from LLM.application.llm_service import LLMService
from LLM.infrastructure.providers.anthropic_provider import AnthropicProvider
from LLM.infrastructure.providers.fake_provider import FakeProvider


def build_service(fake: bool) -> LLMService:
    # Her vælger vi kokken. Det er det eneste sted i laget, hvor det sker.
    if fake:
        provider = FakeProvider()
    else:
        provider = AnthropicProvider(model=settings.MODEL)

    return LLMService(provider, system=settings.LLM_SYSTEM_PROMPT)


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--stream", action="store_true", help="Vis svaret mens det skrives")
    parser.add_argument("--fake", action="store_true", help="Brug falsk model, ingen API-nøgle")
    args = parser.parse_args()

    # 2. Byg servicen.
    service = build_service(args.fake)

    # 3. Spørg og vis svaret.
    if args.stream:
        for chunk in service.stream(args.question):
            print(chunk, end="", flush=True)
        print()
    else:
        response = service.ask(args.question)
        print(response.text)


if __name__ == "__main__":
    main()