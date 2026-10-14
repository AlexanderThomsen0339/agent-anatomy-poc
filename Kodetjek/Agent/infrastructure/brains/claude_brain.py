"""Den rigtige hjerne: Claude med værktøjer (tool use).

Det er den eneste fil i Agent-laget, der kender til Anthropic.
Den oversætter mellem agentens historik og det format, Claude forventer.
"""
import anthropic

from Agent.domain.models import Action, Decision, History, Observation
from MCP.domain.models import ToolSpec


class ClaudeBrain:

    def __init__(self, model: str = "claude-sonnet-5-5", max_tokens: int = 2048):
        # SDK'en finder selv API-nøglen i miljøvariablen ANTHROPIC_API_KEY.
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        # 1. Oversæt ind: spørgsmål + historik + værktøjer -> Claudes format.
        result = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=self._to_messages(question, history),
            tools=[
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in tools
            ],
        )

        # 2. Oversæt ud: Claudes svar -> en Decision.
        text = "".join(block.text for block in result.content if block.type == "text")
        actions = [
            Action(id=block.id, tool=block.name, arguments=block.input)
            for block in result.content
            if block.type == "tool_use"
        ]
        return Decision(text=text, actions=actions)

    @staticmethod
    def _to_messages(question: str, history: History) -> list[dict]:
        messages = [{"role": "user", "content": question}]

        for item in history:
            if isinstance(item, Decision):
                # Det, hjernen sagde og bad om, bliver til en besked fra "assistant".
                content = []
                if item.text:
                    content.append({"type": "text", "text": item.text})
                for action in item.actions:
                    content.append(
                        {"type": "tool_use", "id": action.id, "name": action.tool, "input": action.arguments}
                    )
                messages.append({"role": "assistant", "content": content})
            else:
                # Resultaterne bliver til en besked fra "user", parret med handlingerne via id.
                observations: list[Observation] = item
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": o.action_id,
                            "content": o.content,
                            "is_error": o.is_error,
                        }
                        for o in observations
                    ],
                })

        return messages
