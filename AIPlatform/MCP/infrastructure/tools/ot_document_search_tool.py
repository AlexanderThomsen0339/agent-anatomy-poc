"""OT-søgningen: slår op i de dokumenter, OT-holdet laver, fx signallisten og PDF'er for anlægget.

Hvorfor et værktøj for sig?
OT's dokumenter er en anden kilde end krav og testcases, og ikke alle roller må se dem.
Et eget indeks betyder, at tusindvis af signaler ikke drukner kravene i søgningen, og omvendt.
"""
import re

from MCP.domain.models import ToolSpec
from RAG.domain.models import SearchResult
from RAG.domain.ports import SearchIndex

# Hvor mange tegn et resultat højst viser. En PDF-side kan være lang, så der vises et udsnit omkring fundet.
SNIPPET = 600

# Hvor mange dokumenter en ordret søgning højst returnerer fra hver slags.
EXACT_MAX = 20


class OtDocumentSearchTool:

    spec = ToolSpec(
        name="search_ot_documents",
        description=(
            "Searches the documents made by the OT team: PDF documents (one entry per page) such as procedures, "
            "manuals and reports, and the plant's signal list (one entry per signal with its name in the old "
            "Melody/Symphony and new 800xA systems, a Danish description, unit, range and source). "
            "Results come in two groups, PDF documents first, then the signal list, so a signal never hides a document. "
            "The data is in Danish: search with signal codes like MKF20AP001A or short Danish keywords like kølevandspumpe. "
            "Set exact to true to find only the documents that contain the query word for word, "
            "e.g. when the user asks which document says \"BERAN backup\". "
            "Each result starts with the file and the page or sheet it comes from."
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

    def __init__(self, pdfs: SearchIndex, tables: SearchIndex, k: int = 5):
        # Hvorfor to indeks? Se build_ot_service() i MCP/api/build.py.
        self.pdfs = pdfs
        self.tables = tables
        self.k = k

    def run(self, arguments: dict) -> str:
        # 16f: SØG I OT-DOKUMENTER: Søger i PDF'erne og i regnearkene for sig, så begge kommer med.
        query = arguments["query"].strip().strip('"“”')
        exact = bool(arguments.get("exact"))
        groups = [("PDF documents", self._search(self.pdfs, query, exact)), ("Signal list", self._search(self.tables, query, exact))]

        parts = [
            f"== {title} ==\n" + "\n\n".join(f"[{r.chunk.source}] {snippet(r.chunk.text, query)}" for r in results)
            for title, results in groups if results
        ]
        if not parts:
            if exact:
                return f'No OT document contains "{query}" word for word. Say so; do not guess.'
            return "Nothing found in the OT documents. Try a signal code or other Danish words; do not guess."
        return "\n\n".join(parts)

    def _search(self, index: SearchIndex, query: str, exact: bool) -> list[SearchResult]:
        if exact:
            # Ordret: kun de afsnit, hvor hele teksten står, uanset store og små bogstaver og linjeskift.
            # Hvorfor ikke bare ordsøgningen? Den finder også sider med "backup" alene og sorterer kun efter antal fælles ord.
            phrase = normalize(query)
            return [r for r in index.search(query, k=100_000) if phrase in normalize(r.chunk.text)][:EXACT_MAX]

        # Hvorfor sortere igen? Ordsøgningen giver samme point til en side, der nævner ordet én gang,
        # og en side, der handler om det. Her kommer de sider først, hvor søgeordene står flest gange.
        words = re.findall(r"\w+", query.lower())
        candidates = index.search(query, k=self.k * 10)
        candidates.sort(key=lambda r: (r.score, sum(normalize(r.chunk.text).count(w) for w in words)), reverse=True)
        return candidates[: self.k]


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
