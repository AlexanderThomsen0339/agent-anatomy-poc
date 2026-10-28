"""Den rigtige hjerne: lokal Mistral gennem Ollama (tool use).

Det er den eneste fil i Agent-laget, der kender til Ollama/Mistral.
Resten af laget taler kun med porten AgentBrain.

Kræver Ollama kørende lokalt (ollama serve) med en Mistral-model hentet
(fx `ollama pull mistral:7b-instruct-v0.3-q4_K_M`).

Hvorfor Ollamas eget API (/api/chat) og ikke det OpenAI-kompatible?
Kun det eget API lader os sætte num_ctx, hvor meget tekst modellen må se.
Ollamas standard er 2.048-4.096 tokens, og systemprompten alene fylder ca. 4.000.
Er der ikke plads, smider Ollama det ældste væk, og det er reglerne.
"""
import json
import re
import urllib.request
import uuid

from Agent.domain.models import Action, Decision, History, Observation
from MCP.domain.models import ToolSpec


class MistralBrain:

    def __init__(self, model: str, base_url: str = "http://localhost:11434", context: int = 32768, temperature: float = 0.1):
        # Det gamle OpenAI-endpoint (.../v1) virker også som adresse: /v1 fjernes.
        self.url = base_url.rstrip("/").removesuffix("/v1") + "/api/chat"
        self.model = model
        # Lav temperatur: en lille model holder sig bedre til formatet, når den ikke "improviserer".
        self.options = {"num_ctx": context, "temperature": temperature}

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        body = {
            "model": self.model,
            "messages": self._to_messages(system, question, history),
            "stream": False,
            "options": self.options,
        }
        if tools:
            body["tools"] = [
                {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}}
                for t in tools
            ]
        request = urllib.request.Request(self.url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=600) as response:
            message = json.loads(response.read())["message"]

        text = message.get("content") or ""
        calls = [(c["function"]["name"], c["function"].get("arguments") or {}) for c in message.get("tool_calls") or []]
        if not calls and tools:
            # En lille model skriver tit værktøjskaldet som tekst i stedet for et rigtigt kald.
            calls = self._calls_in_text(text, {t.name for t in tools})
            if calls:
                text = ""
        actions = [
            Action(id=uuid.uuid4().hex[:8], tool=name, arguments=json.loads(args) if isinstance(args, str) else args)
            for name, args in calls
        ]
        return Decision(text=text, actions=actions)

    @staticmethod
    def _calls_in_text(text: str, names: set[str]) -> list[tuple[str, dict]]:
        """Værktøjskald skrevet som tekst, fx `[TOOL_CALLS] [{"name": "search_requirements", "arguments": {...}}]`."""
        raw = text.replace("[TOOL_CALLS]", "").strip().strip("`")
        raw = re.sub(r"^json\s*", "", raw)
        if not raw.startswith(("[", "{")):
            return []
        try:
            data = json.loads(raw)
        except ValueError:
            return []
        items = data if isinstance(data, list) else [data]
        calls = []
        for item in items:
            if isinstance(item, dict) and item.get("name") in names:
                calls.append((item["name"], item.get("arguments") or item.get("parameters") or {}))
        return calls

    @staticmethod
    def _to_messages(system: str, question: str, history: History) -> list[dict]:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
        # Ollama vil gerne vide, hvilket værktøj et resultat kommer fra.
        tool_of = {}

        for item in history:
            if isinstance(item, Decision):
                tool_of.update({a.id: a.tool for a in item.actions})
                entry = {"role": "assistant", "content": item.text or ""}
                if item.actions:
                    entry["tool_calls"] = [
                        {"function": {"name": action.tool, "arguments": action.arguments}} for action in item.actions
                    ]
                messages.append(entry)
            else:
                observations: list[Observation] = item
                for o in observations:
                    messages.append({"role": "tool", "content": o.content, "tool_name": tool_of.get(o.action_id, "")})

        return messages
