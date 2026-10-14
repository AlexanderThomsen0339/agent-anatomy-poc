"""Lærlingen: følger et fast manuskript, uden internet og uden API-nøgle.

Den tænker ikke selv. Den spiller bare de beslutninger, den har fået,
én ad gangen. Men værktøjerne, den beder om, bliver kaldt for alvor,
så man kan se hele løkken køre: tænk, handl, se, gentag.
"""
from Agent.domain.models import Action, Decision, History
from MCP.domain.models import ToolSpec


class ScriptedBrain:

    def __init__(self, script: list[Decision]):
        self.script = script

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        # Hver beslutning i historikken er et skridt, vi allerede har spillet.
        step = sum(1 for item in history if isinstance(item, Decision))
        if step < len(self.script):
            return self.script[step]
        return Decision("Manuskriptet er slut.")


# Demo-manuskriptet: en rykker til en låner.
# Det bruger alle fire lag nedenunder: en skill (lag 4) via værktøjer (lag 3),
# en søgning i dokumenterne (lag 2), og i den rigtige version tænker lag 1.
DEMO_QUESTION = "Skriv en rykker til Sara Jensen. Hendes lån af 'Kaptajn Klo' er 12 dage over tiden."

DEMO_SCRIPT = [
    Decision(
        "Det er en rykker, så jeg henter først vores skill til rykkere.",
        [Action("1", "load_skill", {"name": "rykker"})],
    ),
    Decision(
        "Skillen siger, at jeg skal slå reglerne op og ikke gætte.",
        [Action("2", "search_docs", {"query": "afleveres bog sent koster dag"})],
    ),
    Decision(
        "Det koster 5 kr. pr. dag. Jeg regner gebyret ud for 12 dage.",
        [Action("3", "calculate", {"a": 12, "b": 5, "operation": "multiply"})],
    ),
    Decision(
        "Hej Sara Jensen,\n"
        "Dit lån af 'Kaptajn Klo' er nu 12 dage over tiden, og gebyret er 60 kr. (5 kr. pr. dag).\n"
        "Du kan aflevere bogen døgnet rundt i postkassen ved hoveddøren.\n"
        "Venlig hilsen, Biblioteket Anatomi"
    ),
]
