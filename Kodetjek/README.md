# Kodetjek

A developer asks whether their code solves a user story. An agent looks up the requirements, reads the code and answers with a verdict per acceptance criterion, pointing to `file:line`.

Built on four of the layers from the repo root (RAG, MCP, Skills, Agent), with the same ports & adapters structure. The root layers are untouched.

## Flow

```
"Does our code solve US-001?"
  │
  ▼
Agent (Gemini) ── load_skill("code-review")    Skills  → answer format
                ├ search_requirements(query)   MCP → RAG keyword index over RAG/data/*.xlsx
                ├ list_code_files()            MCP → CODE_FOLDER
                └ read_code_file(path)         MCP → CODE_FOLDER
  │
  ▼
Solved / Partly solved / Not solved, one line per criterion with file:line
```

## Setup

Python 3.10+. Run every command from the `Kodetjek/` folder.

```bash
pip install -r requirements.txt
```

1. Point `CODE_FOLDER` in `settings.py` at the code to check.
2. Put a Gemini key from Google AI Studio in `local_secrets.py` (ignored by git):
   ```python
   GEMINI_API_KEY = "your-key"
   ```
   Or set the `GEMINI_API_KEY` environment variable.

## Run

```bash
python -m Agent.api.web
```

Open http://localhost:8000 and ask e.g. "Does our code solve US-005 Download faktura?". Include the title: the same US id exists in several sheets.

## Layout

| Path | Contents |
|---|---|
| `settings.py` | All configuration: Gemini model and thinking level, data folder, `CODE_FOLDER`, system prompt, `MAX_STEPS`. |
| `Agent/` | `AgentService` loop, `GeminiBrain`, and the demo page `api/web.py`. |
| `MCP/` | The three tools. `list_code_files` follows the repo's `.gitignore`. `read_code_file` refuses paths outside `CODE_FOLDER`. |
| `RAG/` | `XlsxLoader` (one chunk per user story and test case) and `KeywordIndex`. |
| `Skills/` | `code-review`: how the answer is written. |
| `RAG/data/` | User stories and test cases for Mit Aalborg Forsyning (Danish). |

## Limitations

- **Keyword search only.** It matches whole words, and the requirements are in Danish, so the agent searches with ids and Danish words.
- **File listing size.** `list_code_files` returns every file name, which costs tokens on every step in a large solution.
- **Free Gemini tier.** It is slow, and Google may use the data sent, which includes the code being checked.
