"""Dokumentsøgningen: slår op i bibliotekets dokumenter fra lag 2.

Det er RAG lavet om til et værktøj. Nu er det ikke koden, der altid søger først,
men LLM'en, der selv vælger, om og hvad der skal søges efter (agentisk RAG).
"""
from MCP.domain.models import ToolSpec
from RAG.domain.ports import SearchIndex


class DocsSearchTool:

    spec = ToolSpec(
        name="search_docs",
        description=(
            "Søger i bibliotekets egne dokumenter: åbningstider, lån, lånerkort, "
            "personale, ferie, onboarding og IT. Brug korte søgeord."
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
        # Vi får indekset fra lag 2 udefra, allerede fyldt med dokumenter.
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        results = self.index.search(arguments["query"], self.k)
        if not results:
            return "Ingen resultater."
        return "\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)
