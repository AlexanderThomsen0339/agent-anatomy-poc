"""Kravsøgningen: slår op i user stories og testcases fra lag 2.

Det er RAG lavet om til et værktøj. Nu er det ikke koden, der altid søger først,
men LLM'en, der selv vælger, om og hvad der skal søges efter (agentisk RAG).
"""
from MCP.domain.models import ToolSpec
from RAG.domain.ports import SearchIndex


class RequirementsSearchTool:

    spec = ToolSpec(
        name="search_requirements",
        description=(
            "Søger i user stories, acceptkriterier og testcases for Mit Aalborg Forsyning "
            "(Mit Overblik, Regninger og Min Profil). Brug korte søgeord eller id'er som US-002 og TC-011."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Hvad der skal søges efter"},
            },
            "required": ["query"],
        },
    )

    def __init__(self, index: SearchIndex, k: int = 3):
        # Vi får indekset fra lag 2 udefra, allerede fyldt med user stories og testcases.
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        results = self.index.search(arguments["query"], self.k)
        if not results:
            return "Ingen resultater."
        return "\n\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)
