"""OT-søgningen: slår op i de dokumenter, OT-holdet laver, fx signallisten og PDF'er for anlægget.

Hvorfor et værktøj for sig?
OT's dokumenter er en anden kilde end krav og testcases, og ikke alle roller må se dem.
Et eget indeks betyder, at tusindvis af signaler ikke drukner kravene i søgningen, og omvendt.
"""
import re

from MCP.domain.models import ToolSpec
from RAG.domain.ports import SearchIndex

# Hvor mange tegn et resultat højst viser. En PDF-side kan være lang, så der vises et udsnit omkring fundet.
SNIPPET = 600

# Hvor mange dokumenter en ordret søgning højst returnerer.
EXACT_MAX = 20


class OtDocumentSearchTool:

    spec = ToolSpec(
        name="search_ot_documents",
        description=(
            "Searches the documents made by the OT team: the plant's signal list (one entry per signal with its name "
            "in the old Melody/Symphony and new 800xA systems, a Danish description, unit, range and source) "
            "and PDF documents (one entry per page). "
            "The data is in Danish: search with signal codes like MKF20AP001A or short Danish keywords like kølevandspumpe. "
            "Set exact to true to find only the documents that contain the query word for word, "
            "e.g. when the user asks which document says \"BERAN backup\". "
            "Each result starts with the file and the sheet or page it comes from."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
                "exact": {"type": "boolean", "description": "True to match the query word for word"},
            },
            "required": ["query"],
        },
    )

    def __init__(self, index: SearchIndex, k: int = 5):
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        # 16f: SØG I OT-DOKUMENTER: Søger i OT-indekset fra trin 8.
        query = arguments["query"].strip().strip('"“”')
        if arguments.get("exact"):
            # Ordret: kun de afsnit, hvor hele teksten står, uanset store og små bogstaver og linjeskift.
            # Hvorfor ikke bare ordsøgningen? Den finder også sider med "backup" alene og sorterer kun efter antal fælles ord.
            phrase = normalize(query)
            results = [r for r in self.index.search(query, k=100_000) if phrase in normalize(r.chunk.text)][:EXACT_MAX]
            if not results:
                return f'No OT document contains "{query}" word for word. Say so; do not guess.'
        else:
            results = self.index.search(query, self.k)
            if not results:
                return "Nothing found in the OT documents. Try a signal code or other Danish words; do not guess."
        return "\n\n".join(f"[{r.chunk.source}] {snippet(r.chunk.text, query)}" for r in results)


def normalize(text: str) -> str:
    """Små bogstaver og ét mellemrum mellem ordene, så linjeskift og dobbelte mellemrum ikke spiller ind."""
    return " ".join(text.lower().split())


def snippet(text: str, query: str) -> str:
    """Hele afsnittet, hvis det er kort. Ellers et udsnit omkring det første sted, søgningen rammer."""
    if len(text) <= SNIPPET:
        return text
    lower = text.lower()
    hits = [lower.find(w) for w in [query.lower()] + re.findall(r"\w+", query.lower())]
    start = max(0, min([h for h in hits if h >= 0], default=0) - SNIPPET // 3)
    return ("…" if start else "") + text[start:start + SNIPPET] + "…"
