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
            "Searches user stories, acceptance criteria and test cases for Mit Aalborg Forsyning "
            "(Mit Overblik, Regninger and Min Profil). The data is in Danish: use ids like US-002 and TC-011, "
            "or short Danish keywords."
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
        # Vi får indekset fra lag 2 udefra, allerede fyldt med user stories og testcases.
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        # 16b: SØG I KRAV: Søger i indekset fra trin 8. Fortsæt i RAG/infrastructure/index/keyword_index.py.
        results = self.index.search(arguments["query"], self.k)
        if not results:
            return "No results."
        return "\n\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)
