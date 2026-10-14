"""LLMService: den eneste måde, resten af systemet taler med modellen på."""
import logging

from LLM.domain.models import Message, Response
from LLM.domain.ports import LLMProvider

log = logging.getLogger(__name__)


class LLMService:

    def __init__(self, provider: LLMProvider, system: str = ""):
        # Vi får "kokken" udefra. Servicen er ligeglad med, hvem det er.
        self.provider = provider
        self.system = system

    def ask(self, question: str) -> Response:
        """Ét spørgsmål ind, ét svar ud."""
        message = Message(role="user", content=question)
        return self.chat([message])

    def chat(self, messages: list[Message]) -> Response:
        """Send en hel samtale. Modellen husker intet selv, så alt skal med."""
        if not messages:
            raise ValueError("There must be at least one message.")

        response = self.provider.complete(self.system, messages)

        log.info("model=%s tokens=%s", response.model, response.input_tokens + response.output_tokens)
        return response

    def stream(self, question: str):
        """Samme som ask(), men svaret kommer i små bidder."""
        message = Message(role="user", content=question)
        return self.provider.stream(self.system, [message])