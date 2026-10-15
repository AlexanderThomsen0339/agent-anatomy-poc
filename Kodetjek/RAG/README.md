# RAG

**What it is:** the requirements store. RAG (Retrieval-Augmented Generation) means finding the right text and giving it to the model, instead of relying on what the model remembers.

**What it does:** at startup it reads the xlsx files in `data/`, splits them into one piece per user story or test case, and puts them in a keyword index (flow steps 5–8). For each question it returns the best matches when `search_requirements` asks (step 16b).

**Why it's there:** Gemini has never seen Mit Aalborg Forsyning's user stories. Without RAG it would invent acceptance criteria. With RAG, every verdict is checked against the real requirements.

RAG doesn't know about the agent or MCP. It is reached only through the `SearchIndex` port, which `search_requirements` in MCP calls.

| Folder | Contents | Why |
|---|---|---|
| `domain/` | `Document`, `Chunk`, `SearchResult` and the ports `DocumentLoader`, `Chunker`, `SearchIndex` | The rest of the code depends on these, not on Excel or keyword search. |
| `application/` | `IngestService.run()`: load, split, index | The steps stay the same whatever the source or index. |
| `infrastructure/` | `XlsxLoader`, `ParagraphChunker`, `KeywordIndex` | Each can be replaced alone: another file format, or vector search instead of keywords. |
| `data/` | The xlsx files with user stories and test cases | The source of truth for the requirements. |

The search matches whole words, and the requirements are in Danish, so the agent is told to search with ids and Danish words.
