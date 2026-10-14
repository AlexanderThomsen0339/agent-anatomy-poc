"""Legetøjskokken: svarer altid det samme, uden internet og uden API-nøgle.

Bruges til at prøve resten af systemet af, uden at det koster noget.
"""
from LLM.domain.models import Message, Response


class FakeProvider:

    def __init__(self, answer: str = "This is a fake answer."):
        self.answer = answer

    def complete(self, system: str, messages: list[Message]) -> Response:
        return Response(
            text=self.answer,
            model="fake",
            input_tokens=len(messages[-1].content.split()),
            output_tokens=len(self.answer.split()),
            stop_reason="end_turn",
        )

    def stream(self, system: str, messages: list[Message]):
        for word in self.answer.split():
            yield word + " "