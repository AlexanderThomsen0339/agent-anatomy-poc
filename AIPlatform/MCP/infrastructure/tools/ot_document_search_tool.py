"""OT-søgningen: slår op i de dokumenter, OT-holdet laver, fx signallisten for anlægget.

Hvorfor et værktøj for sig?
OT's dokumenter er en anden kilde end krav og testcases, og de bruges af Vedligehold, ikke af IT.
Et eget indeks betyder, at tusindvis af signaler ikke drukner kravene i søgningen, og omvendt.
"""
from MCP.domain.models import ToolSpec
from RAG.domain.ports import SearchIndex


class OtDocumentSearchTool:

    spec = ToolSpec(
        name="search_ot_documents",
        description=(
            "Searches the documents made by the OT team, such as the plant's signal list: "
            "one entry per signal with its name in the old (Melody/Symphony) and new (800xA) systems, "
            "a Danish description (Langtext), unit, range and source. "
            "The data is in Danish: search with signal codes like MKF20AP001A or short Danish keywords like kølevandspumpe. "
            "Each result starts with the file and sheet it comes from."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
            },
            "required": ["query"],
        },
    )

    def __init__(self, index: SearchIndex, k: int = 5):
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        # 16f: SØG I OT-DOKUMENTER: Søger i OT-indekset fra trin 8.
        results = self.index.search(arguments["query"], self.k)
        if not results:
            return "Nothing found in the OT documents. Try a signal code or other Danish words; do not guess."
        return "\n\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)
