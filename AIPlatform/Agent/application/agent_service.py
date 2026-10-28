"""AgentService: løkken, der lader hjernen tænke og hænderne handle."""
from typing import Callable

from Agent.domain.models import Action, AgentRun, Decision, History, Observation, Step
from Agent.domain.ports import AgentBrain
from MCP.application.tool_service import ToolService
from MCP.domain.models import ToolCall


class AgentService:

    def __init__(
        self,
        brain: AgentBrain,
        tools: ToolService,
        system: str,
        max_steps: int = 8,
        accept: Callable[[str, list[Step]], bool] | None = None,
        reminder: str = "",
    ):
        # Vi får hjernen og værktøjerne udefra.
        self.brain = brain
        self.tools = tools
        self.system = system
        self.max_steps = max_steps
        # Hvorfor accept og reminder?
        # Kan svaret ikke bruges (accept siger nej), får agenten én chance mere med reminder sat på opgaven.
        # Det hjælper en lille model, der glemmer formatet. Uden accept er løkken som før.
        self.accept = accept
        self.reminder = reminder

    def run(self, question: str, on_step: Callable[[list[Step]], None] | None = None, first: list[Action] = ()) -> AgentRun:
        """Løs opgaven. on_step kaldes efter hvert skridt, så man kan følge med.

        first er værktøjskald, koden laver, før modellen tænker første gang (fx søg kravene, læs de ændrede filer).
        Hvorfor? En lille model springer tit værktøjerne over og gætter. Kaldene står i historikken, som havde
        agenten selv bedt om dem, så modellen ser resultaterne, og siden viser dem som skridt og kilder.
        """
        # 12: AGENTEN KØRER: En løkke, der gentages, indtil Gemini har et svar (højst MAX_STEPS gange).
        history: History = []
        steps: list[Step] = []
        reminded = False
        if first:
            decision = Decision(text="", actions=list(first))
            history.append(decision)
            observations, new_steps = self._act(decision)
            history.append(observations)
            steps.extend(new_steps)
            if on_step:
                on_step(new_steps)

        for _ in range(self.max_steps):
            # 13: TÆNK: Gemini ser spørgsmålet, alt hidtil og værktøjerne og beslutter, hvad der skal ske.
            # Fortsæt i Agent/infrastructure/brains/gemini_brain.py.
            decision = self.brain.decide(self.system, question, history, self.tools.list_tools())
            history.append(decision)

            # 14: FÆRDIG? Beder Gemini ikke om flere værktøjer, er teksten svaret. Hop til trin 19.
            if decision.is_final:
                if self.accept and not reminded and not self.accept(decision.text, steps):
                    # Svaret kan ikke bruges. Det fjernes, og agenten prøver igen med påmindelsen og alt, den har set.
                    history.pop()
                    question += self.reminder
                    reminded = True
                    continue
                # 19: SVAR: Løkken slutter. Tilbage til do_GET() i Agent/api/web.py (trin 20).
                return AgentRun(decision.text, steps)

            # 15: HANDL: Hvert værktøj, Gemini bad om, kaldes. Fortsæt i MCP/application/tool_service.py.
            observations, new_steps = self._act(decision)

            # 17: SE: Resultaterne lægges i historikken, så Gemini ser dem i næste runde.
            history.append(observations)
            steps.extend(new_steps)
            # 18: VIS SKRIDT: Fortæl web-siden, hvad der lige skete. Derefter tilbage til trin 13.
            if on_step:
                on_step(new_steps)

        # Grænsen for antal skridt beskytter mod en agent, der kører i ring.
        return AgentRun("I did not finish within the step limit.", steps, finished=False)

    def _act(self, decision: Decision) -> tuple[list[Observation], list[Step]]:
        """Kalder hvert værktøj i beslutningen og parrer resultatet med handlingen."""
        observations = []
        new_steps = []
        for action in decision.actions:
            result = self.tools.call(ToolCall(action.tool, action.arguments))
            observation = Observation(action.id, result.content, result.is_error)
            observations.append(observation)
            new_steps.append(Step(action, observation))
        return observations, new_steps
