"""AgentService: løkken, der lader hjernen tænke og hænderne handle."""
from typing import Callable

from Agent.domain.models import AgentRun, Decision, History, Observation, Step
from Agent.domain.ports import AgentBrain
from MCP.application.tool_service import ToolService
from MCP.domain.models import ToolCall


class AgentService:

    def __init__(self, brain: AgentBrain, tools: ToolService, system: str, max_steps: int = 8):
        # Vi får hjernen og værktøjerne udefra.
        self.brain = brain
        self.tools = tools
        self.system = system
        self.max_steps = max_steps

    def run(self, question: str, on_step: Callable[[Decision, list[Step]], None] | None = None) -> AgentRun:
        """Løs opgaven. on_step kaldes efter hvert skridt, så man kan følge med."""
        history: History = []
        steps: list[Step] = []

        for _ in range(self.max_steps):
            # 1. Tænk: hjernen ser spørgsmålet, alt hidtil og værktøjerne.
            decision = self.brain.decide(self.system, question, history, self.tools.list_tools())
            history.append(decision)

            # 2. Færdig? Så er teksten svaret.
            if decision.is_final:
                return AgentRun(decision.text, steps)

            # 3. Handl: udfør hver handling med værktøjerne fra lag 3.
            observations = []
            new_steps = []
            for action in decision.actions:
                result = self.tools.call(ToolCall(action.tool, action.arguments))
                observation = Observation(action.id, result.content, result.is_error)
                observations.append(observation)
                new_steps.append(Step(action, observation))

            # 4. Se: resultaterne kommer med i næste runde.
            history.append(observations)
            steps.extend(new_steps)
            if on_step:
                on_step(decision, new_steps)

        # Grænsen for antal skridt beskytter mod en agent, der kører i ring.
        return AgentRun("Jeg nåede ikke at blive færdig inden for grænsen.", steps, finished=False)
