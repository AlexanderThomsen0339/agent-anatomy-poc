"""Kravspec-søgningen: slår op i forretningens krav (KRAV-ids).

Hvorfor et værktøj ved siden af search_requirements?
Testcases siger, hvad testholdet tjekker. Kravspec siger, hvad forretningen har bestilt.
Det er to forskellige kilder, så agenten skal kunne se, hvilken et svar kommer fra,
og opdage, når en user story slet ikke har et krav.
"""
import re

from MCP.domain.models import ToolSpec
from RAG.domain.ports import SearchIndex


class SpecificationSearchTool:

    spec = ToolSpec(
        name="search_specification",
        description=(
            "Searches the business requirements specification (kravspec) for Mit Aalborg Forsyning. "
            "Each requirement has an id like KRAV-REG-03 and lists the user stories and test cases it covers. "
            "The data is in Danish: search with ids like KRAV-REG-03 or US-005, or short Danish keywords. "
            "If nothing is found, the user story has no documented business requirement."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
            },
            "required": ["query"],
        },
    )

    def __init__(self, index: SearchIndex, k: int = 3):
        # Et indeks kun med kravspec, så krav ikke drukner mellem testcases.
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        # 16e: SØG I KRAVSPEC: Søger i kravspec-indekset fra trin 8.
        query = arguments["query"]

        # Hvorfor et filter på user story-id?
        # Ordsøgning finder "US" i alle krav, så US-099 ville give krav, der intet har med den at gøre.
        # Spørges der på et id, returneres i stedet præcis de krav, hvis "Dækker"-linje nævner det.
        story_ids = {s.upper() for s in re.findall(r"\bUS-\d+\b", query, re.IGNORECASE)}
        if story_ids:
            results = [r for r in self.index.search(query, k=1000) if story_ids & covered_stories(r.chunk.text)]
        else:
            results = self.index.search(query, self.k)

        if not results:
            return "No requirement found in the specification. Report it as not documented; do not guess."
        return "\n\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)


def covered_stories(text: str) -> set[str]:
    """De user story-ids, som et krav dækker, læst fra linjen "Dækker:"."""
    for line in text.splitlines():
        if line.startswith("Dækker:"):
            return {s.upper() for s in re.findall(r"\bUS-\d+\b", line, re.IGNORECASE)}
    return set()
