"""Den rigtige kok: taler med Claude gennem Anthropic's SDK.

Det er den eneste fil i LLM-laget, der kender til Anthropic.
"""
import anthropic

from LLM.domain.models import Message, Response


class AnthropicProvider:

    def __init__(self, model: str = "claude-sonnet-5-5", max_tokens: int = 1024):
        # SDK'en finder selv API-nøglen i miljøvariablen ANTHROPIC_API_KEY.
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, system: str, messages: list[Message]) -> Response:
        # 1. Oversæt ind: vores Message -> det format, Anthropic forventer.
        result = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=self._to_anthropic(messages),
        )

        # 2. Oversæt ud: Anthropic's svar -> vores Response.
        text = "".join(block.text for block in result.content if block.type == "text")
        return Response(
            text=text,
            model=result.model,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            stop_reason=result.stop_reason,
        )

    def stream(self, system: str, messages: list[Message]):
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=self._to_anthropic(messages),
        ) as stream:
            for text in stream.text_stream:
                yield text

    @staticmethod
    def _to_anthropic(messages: list[Message]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]