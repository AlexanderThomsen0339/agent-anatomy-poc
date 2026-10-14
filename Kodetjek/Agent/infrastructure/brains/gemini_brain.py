"""En anden rigtig hjerne: Googles Gemini med værktøjer (function calling).

Samme rolle som ClaudeBrain, bare med en anden model bag. Det er den eneste fil
i Agent-laget, der kender til Google. Resten af laget mærker ikke forskel.
"""
from google import genai
from google.genai import types

from Agent.domain.models import Action, Decision, History, Observation
from MCP.domain.models import ToolSpec


class GeminiBrain:

    def __init__(self, model: str):
        # SDK'en finder selv API-nøglen i miljøvariablen GEMINI_API_KEY.
        self.client = genai.Client()
        self.model = model

        # Hvorfor gemme Geminis egne svar?
        # Gemini sender en signatur med sine værktøjskald, som skal sendes uændret tilbage.
        # Vi kan ikke bygge den op igen ud fra en Decision, så vi gemmer originalen.
        self.raw: dict[int, types.Content] = {}

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        # 1. Oversæt ind: spørgsmål + historik + værktøjer -> Geminis format.
        result = self.client.models.generate_content(
            model=self.model,
            contents=self._to_contents(question, history),
            config=types.GenerateContentConfig(
                system_instruction=system,
                tools=[types.Tool(function_declarations=[
                    types.FunctionDeclaration(
                        name=t.name,
                        description=t.description,
                        parameters_json_schema=t.input_schema,
                    )
                    for t in tools
                ])],
                # Agent-laget kalder selv værktøjerne, så SDK'en må ikke gøre det.
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )

        # 2. Oversæt ud: Geminis svar -> en Decision.
        content = result.candidates[0].content
        parts = content.parts or []
        text = "".join(p.text for p in parts if p.text and not p.thought)
        step = sum(1 for item in history if isinstance(item, Decision))
        actions = [
            # Gemini giver ikke altid kaldene et id, så vi laver selv et.
            Action(id=p.function_call.id or f"{step}-{i}", tool=p.function_call.name, arguments=dict(p.function_call.args or {}))
            for i, p in enumerate(parts)
            if p.function_call
        ]
        decision = Decision(text=text, actions=actions)
        self.raw[id(decision)] = content
        return decision

    def _to_contents(self, question: str, history: History) -> list[types.Content]:
        contents = [types.Content(role="user", parts=[types.Part(text=question)])]
        names: dict[str, str] = {}

        for item in history:
            if isinstance(item, Decision):
                for action in item.actions:
                    names[action.id] = action.tool
                contents.append(self.raw[id(item)])
            else:
                # Resultaterne sendes tilbage med værktøjets navn, som Gemini parrer dem med.
                observations: list[Observation] = item
                contents.append(types.Content(role="user", parts=[
                    types.Part.from_function_response(
                        name=names[o.action_id],
                        response={"error": o.content} if o.is_error else {"result": o.content},
                    )
                    for o in observations
                ]))

        return contents
