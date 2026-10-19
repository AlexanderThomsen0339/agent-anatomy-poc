"""AnswerWriter: laver agentens vurdering om til et svar til den, der spørger."""
import re
from typing import Callable

from Agent.domain.models import Assessment, Finding
from Agent.domain.ports import AgentBrain

STATUSES = ("MET", "NOT_MET", "CANT_TELL", "RISK")


def parse_assessment(text: str) -> Assessment | None:
    """Læser vurderingen, som skillen code-review beder agenten skrive: én linje pr. krav.

    Hvorfor linjer med | og ikke JSON?
    En lille model laver oftere fejl i JSON end i en simpel linje, og linjerne kan læses af et menneske.
    """
    findings = []
    for line in text.splitlines():
        parts = [p.strip(" `*") for p in line.strip(" -*").split("|")]
        if parts and parts[0].upper() in STATUSES:
            parts += [""] * (5 - len(parts))
            findings.append(Finding(parts[0].upper(), *parts[1:5]))
    if not any(f.status != "RISK" for f in findings):
        return None
    return Assessment(findings, no_spec=bool(re.search(r"^\s*NO_SPEC\b", text, re.MULTILINE)))


class AnswerWriter:

    def __init__(self, brain: AgentBrain, instructions_for: Callable[[str], str]):
        # instructions_for henter skillen audience-<rolle>. Den kommer udefra fra Skills-laget.
        self.brain = brain
        self.instructions_for = instructions_for

    def write(self, question: str, assessment: Assessment, role: str) -> str:
        # 20b: SKRIV SVARET: Gemini får kun vurderingen og rollens skill, ingen værktøjer.
        # Den kan derfor ikke vurdere koden igen, kun skrive om. Dommen sættes på af koden.
        findings = "\n".join(
            f"{f.status} | {f.ids} | {f.requirement} | {f.code} | {f.where}" for f in assessment.findings
        )
        prompt = (
            f"The question was: {question}\n\n"
            f"The verdict, already written above your text: {assessment.verdict}\n\n"
            f"The assessment (status | ids | requirement | what the code does | where):\n{findings}"
        )
        system = (
            self.instructions_for(role)
            + "\n\nOnly use the assessment you are given. Never add, remove or change a status, an id or a file:line."
        )
        text = self.brain.decide(system, prompt, [], []).text.strip()
        return assessment.verdict + "\n\n" + text
