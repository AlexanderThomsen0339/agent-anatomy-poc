"""Den rigtige hjerne: lokal Mistral gennem Ollama (tool use).

Det er den eneste fil i Agent-laget, der kender til Ollama/Mistral.
Resten af laget taler kun med porten AgentBrain.

Kræver Ollama kørende lokalt (ollama serve) med en Mistral-model hentet
(fx `ollama pull mistral:7b-instruct-v0.3-q4_K_M`). Ollama stiller et
OpenAI-kompatibelt endpoint op på http://localhost:11434/v1, så vi bruger
openai-SDK'et som klient i stedet for at tale rå HTTP.
"""
import json

from openai import OpenAI

from Agent.domain.models import Action, Decision, History, Observation
from MCP.domain.models import ToolSpec


class MistralBrain:

    def __init__(self, model: str, base_url: str = "http://localhost:11434/v1"):
        # Ollama kræver ingen rigtig nøgle, men SDK'et forlanger en streng.
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model = model

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        result = self.client.chat.completions.create(
            model=self.model,
            messages=self._to_messages(system, question, history),
            tools=[
                {
                    "type": "function",
                    "function": {"name": t.name, "description": t.description, "parameters": t.input_schema},
                }
                for t in tools
            ]
            if tools
            else None,
        )

        message = result.choices[0].message
        actions = [
            Action(id=tc.id, tool=tc.function.name, arguments=json.loads(tc.function.arguments))
            for tc in (message.tool_calls or [])
        ]
        return Decision(text=message.content or "", actions=actions)

    @staticmethod
    def _to_messages(system: str, question: str, history: History) -> list[dict]:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]

        for item in history:
            if isinstance(item, Decision):
                entry = {"role": "assistant", "content": item.text or None}
                if item.actions:
                    entry["tool_calls"] = [
                        {
                            "id": action.id,
                            "type": "function",
                            "function": {"name": action.tool, "arguments": json.dumps(action.arguments)},
                        }
                        for action in item.actions
                    ]
                messages.append(entry)
            else:
                observations: list[Observation] = item
                for o in observations:
                    messages.append({"role": "tool", "tool_call_id": o.action_id, "content": o.content})

        return messages
