"""Oversigten over alle testprotokoller: hver user story og hver testcase med titel, fordelt på område og ark.

Hvorfor et værktøj ved siden af søgningen?
Søgningen giver de få bedste træf. "Hvilke tests er der?" skal have dem alle, ellers mangler listen nogen.
"""
import re
from collections import defaultdict

from MCP.domain.models import ToolSpec
from RAG.domain.models import Document

# Første linje i en blok, der er en user story eller en testcase, fx "US-ID: US-001" eller "TC-016: Ingen regninger".
BLOCK = re.compile(r"^(US-ID: |US-|TC-)", re.IGNORECASE)


def outline(documents: list[Document]) -> str:
    """Én linje pr. user story og testcase, under sit område og ark."""
    areas: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for document in documents:
        sheet = document.source.split(" › ")[-1]
        for block in document.text.split("\n\n"):
            lines = block.split("\n")
            area = lines[0].removeprefix("Område: ") if lines[0].startswith("Område: ") else "?"
            body = lines[1:] if lines[0].startswith("Område: ") else lines
            if not body or not BLOCK.match(body[0]):
                continue
            if body[0].startswith("US-ID: "):
                title = next((l.removeprefix("Titel: ") for l in body if l.startswith("Titel: ")), "")
                areas[area]["User stories"].append(f"{body[0].removeprefix('US-ID: ')} {title}")
            elif body[0].upper().startswith("TC-"):
                areas[area][sheet].append(body[0])
    out = []
    for area, sheets in areas.items():
        out.append(f"## {area}")
        for sheet, items in sheets.items():
            out.append(f"{sheet}: " + "; ".join(items))
    return "\n".join(out)


class RequirementsListTool:

    spec = ToolSpec(
        name="list_requirements",
        description=(
            "Lists every user story and test case in the test protocols for Mit Aalborg Forsyning, "
            "with id and title, grouped by area (Regninger, Profil, Overblik) and sheet. "
            "Use it to answer which tests or user stories there are. Use search_requirements for the details of one."
        ),
        input_schema={"type": "object", "properties": {}},
    )

    def __init__(self, documents: list[Document]):
        # Oversigten laves én gang ved start ud fra de samme dokumenter, som søgningen indlæser.
        self.text = outline(documents) or "No test protocols found."

    def run(self, arguments: dict) -> str:
        return self.text
