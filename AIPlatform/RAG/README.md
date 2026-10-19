# RAG

**What it is:** the requirements store. RAG (Retrieval-Augmented Generation) means finding the right text and giving it to the model, instead of relying on what the model remembers.

**What it does:** at startup it reads the xlsx files in `data/`, splits them into one piece per user story or test case, and puts them in a keyword index (flow steps 5–8). It does the same for the business requirements in `data/kravspec/`, one piece per KRAV id, into a second index. For each question it returns the best matches when `search_requirements` (step 16b) or `search_specification` (step 16e) asks.

**Why it's there:** Gemini has never seen Mit Aalborg Forsyning's user stories. Without RAG it would invent acceptance criteria. With RAG, every verdict is checked against the real requirements.

RAG doesn't know about the agent or MCP. It is reached only through the `SearchIndex` port, which `search_requirements` and `search_specification` in MCP call.

| Folder | Contents | Why |
|---|---|---|
| `domain/` | `Document`, `Chunk`, `SearchResult` and the ports `DocumentLoader`, `Chunker`, `SearchIndex` | The rest of the code depends on these, not on Excel or keyword search. |
| `application/` | `IngestService.run()`: load, split, index | The steps stay the same whatever the source or index. |
| `infrastructure/` | `XlsxLoader`, `XlsxTableLoader`, `PdfLoader`, `MarkdownLoader`, `ParagraphChunker`, `KeywordIndex` | Each can be replaced alone: another file format, or vector search instead of keywords. |
| `data/` | The xlsx files with user stories and test cases | What the test team checks. |
| `data/ot/` | The OT team's documents as xlsx and PDF, such as the signal list. `XlsxTableLoader` reads each sheet as a table, one piece per row, and `PdfLoader` makes one piece per PDF page (`file.pdf › page 3`). Spreadsheets and PDFs get an index each, so 20,000 signal rows can't push the PDF pages out of the results. At start the console shows how many rows and pages were read, and which PDFs had no text. Scanned PDFs without text can't be read. The files are kept out of git because they describe a real plant | What maintenance looks up. |
| `data/kravspec/` | One `.md` file per area with the business requirements: an id (KRAV-REG-03), the requirement, why, which user stories and test cases it covers (`Dækker:`), and who owns it | What the business ordered. Without it, the agent can only check the code against the tests, not against what was asked for. |

The search matches whole words, and the requirements are in Danish, so the agent is told to search with ids and Danish words.
