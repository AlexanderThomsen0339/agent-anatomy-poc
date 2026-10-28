# AI Platform POC

A developer asks: *"Does our code solve this user story?"* An AI agent looks up the user story, its acceptance criteria and the business requirements, reads the developer's code, and assesses each requirement with a `file:line` reference. The answer is then written for whoever asks: a product person or IT.

The presentation of the POC for Kommunikation and IT is in [harness/Praesentation](harness/Praesentation/README.md). For a full architecture walkthrough, a demo script and a glossary — all tied to the `evaluation` skill's quality gates — see [harness/EVALUATION-GUIDE.md](harness/EVALUATION-GUIDE.md).

## Run the demo

Python 3.12+ (the page uses newer f-string syntax). Run everything from the repo root.

```bash
pip install -r requirements.txt
```

1. The agent thinks with a local Mistral model through [Ollama](https://ollama.com):
   ```bash
   ollama pull mistral:7b-instruct-v0.3-q4_K_M
   ollama serve
   ```
   `settings.py` points at Ollama's default address (`http://localhost:11434`); no API key is needed.
2. The code to check comes from the Azure DevOps repo in `CODE_REPO` in `settings.py`. The page clones it into `repos/code` when it starts. Before every code check it picks the branch and fetches the latest, so a developer can push and ask straight away: if an open pull request into `dev` has the question's user story id (e.g. US-005) in its title or branch name, its branch is checked, otherwise `dev`. The first step on the page says which branch and pull request it checks. If the same question was checked before on the same branch and the requirements are unchanged, only the files changed since that commit are read, and the earlier assessment is updated (at most 20 changed files, otherwise all the code is checked again). You need git installed. Set `CODE_REPO = ""` to read a folder on your computer instead (`CODE_FOLDER`).
3. Put an Azure DevOps Personal Access Token with read access to Code in `local_secrets.py` (ignored by git):
   ```python
   AZURE_DEVOPS_PAT = "your-token"
   ```
4. Start the page:
   ```bash
   python web.py
   ```
5. Open http://localhost:8000 and ask a question.

The page and the answers are in Danish. To show them in English (e.g. for a screenshot), set `LANGUAGE = "en"` in `settings.py`, or start the page with `AIPLATFORM_LANGUAGE=en python web.py`. The page texts are in `TEXTS` in `web.py`, the verdict words in `VERDICT_WORDS` in `agent.py`, and the AI gets `ENGLISH_NOTE` from `settings.py` at the end of every instruction. The test protocols and requirements stay Danish; the AI translates what it quotes.

## Questions to ask

The code is the demo project *Mit Aalborg Forsyning – Regninger* on the Dev branch of the Azure DevOps repo AI platform POC.

- Does our code solve US-005 Download faktura?
- Does our code solve US-004 Vis betalingsstatus?
- Does our code solve US-003 Regninger er ikke længere tilgængelige?
- Does our code solve US-001 Vis regningsoversigt?

The page is a chat in Danish. The question is a bubble, each step shows live in *Sådan finder jeg svaret* (folded away when the answer is ready), and the answer is a bubble with the verdict as a coloured badge, a folded *Kilder* box with the test documents, requirement files and code folder (and its git repo) the agent actually used, and a folded *Vurdering pr. krav* box with every requirement's status. The field at the bottom sends with Enter, and *Ny samtale* starts over. The agent assesses the code once per question, the same whoever asks: one line per requirement (met, not met, can't tell) plus risks. The verdict (**Løst**, **Delvist løst** or **Ikke løst**, "X af Y krav er opfyldt") is counted from that list by the code, not written by the AI. A dropdown above the question says who is asking, and the answer is written from the assessment for that role; switching role on the same question reuses the assessment. *Produkt / kommunikation* gets a short reply in plain Danish, in whole sentences like a colleague: it answers the question first, then says what the customer experiences and why, who changed what if a recent commit caused it, and whether the test can be passed. No ids or code; those are in the table. *IT* gets a technical answer with file:line, what can't be told from the code, architecture deviations and what to fix first.

A question can be followed up. Under each answer is a field for the next question, and the page sends the earlier questions and answers with it (at most 3, in a hidden field `c`, so the server remembers nothing). If the agent can't tell which user story is meant, it doesn't guess: it writes `QUESTION:` and a short question that lists the user stories that could fit (rule in `code-review`), the page shows it under *The agent asks*, and the answer, e.g. "Den om billing", comes back with the conversation.

The test protocols (`harness/data/test-protocols/`, one xlsx per area: Regninger, Profil and Overblik; each numbers its user stories from US-001, so every block is tagged with its *Område*) are examples written for the demo project.

Which teams a role sees is set in `ROLE_TEAMS` in `settings.py`, and the code gives each role an agent with only those teams' tools; the AI doesn't choose. Both *Produkt / kommunikation* and *IT* see the `web` team's code; only the audience skill used to write the final answer differs between them.

## Code layout

Everything that runs lives in a handful of files at the repo root; everything that isn't code (skills, sample data, docs, the presentation) lives under `harness/`.

| File | What it holds |
|---|---|
| `web.py` | The page: HTTP server, HTML, routes a question to chat, a docs lookup or a code check, and renders the answer. Entry point (`python web.py`). |
| `build.py` | The composition root: wires the brain, tools and skills into one agent per role (`ROLE_TEAMS`), plus the docs-only agent and the code checkout service. |
| `agent.py` | The agent loop (`AgentService`: think → act → see), the router that classifies a question (chat / docs / code check), `AnswerWriter` (writes the answer for a role from the assessment), the assessment model (`Finding`, `Assessment`, the verdict) and `MistralBrain`, the only place that talks to Ollama. |
| `tools.py` | The tool contracts (`ToolSpec`, `ToolCall`, `ToolResult`), `ToolService` (calls a tool by name) and `CheckoutService` (picks which branch a code check sees). |
| `tools_impl.py` | The tools themselves: `search_requirements`, `list_requirements`, `list_code_files`, `read_code_file`, `list_recent_changes`. |
| `repository.py` | `GitRepository` (clones/fetches the code to check) and `AzurePullRequestFinder` (finds an open PR matching a user story id). |
| `rag.py` | Loads and searches the documents: `XlsxLoader` reads the test protocols, `ParagraphChunker` splits them into chunks, `KeywordIndex` searches them. |
| `skills.py` | Reads skills from `harness/skills/*/SKILL.md` and exposes them as a catalog plus `load_skill`, the tool an agent uses to fetch one. |
| `settings.py` | All configuration in one place: the model, folders, teams, roles and prompts. |

| Folder | What's in it |
|---|---|
| `harness/skills/` | The skills: `evaluation`, `code-review`, `architecture-web`, `audience-product`, `audience-it`. |
| `harness/data/` | Sample data: `test-protocols/` (xlsx test cases). |
| `harness/diagrams/` | The architecture diagram shown during a demo. |
| `harness/Praesentation/` | The slide deck used to present the POC. |
| `harness/test-results/` | Saved example sessions. |

## Configuration

Everything is in `settings.py`:

| Setting | What it does |
|---|---|
| `MISTRAL_MODEL`, `MISTRAL_BASE_URL`, `MISTRAL_CONTEXT` | Which local model thinks (via Ollama), where Ollama listens, and how much text it can see per call. |
| `DATA_FOLDER` | The xlsx test cases. |
| `SEARCH_K` | How many results a search returns. |
| `CODE_REPO`, `CODE_BRANCH` | The git repo with the code to check, and the branch to check when no open pull request into it matches the question (`dev`, following IT's feature branch → `dev` → `main` rule). It is cloned at start and fetched again before every code check. Empty `CODE_REPO` reads `CODE_FOLDER` as it is. |
| `AZURE_DEVOPS_PAT` | The token git and the pull request search use to read `CODE_REPO`. Read from `local_secrets.py`, or from the `AZURE_DEVOPS_PAT` environment variable. It is sent as a header to git and never stored in the clone. |
| `CODE_FOLDER` | Where the code tools read the code: the clone of `CODE_REPO` (`repos/code`, ignored by git), or your own folder. The code tools can't see outside it. |
| `SKILLS_FOLDER` | The skill folders (`harness/skills`). |
| `TEAMS`, `TEAM` | The team whose code is checked (`web`), its description, and so which `architecture-<team>` skill it is checked against. |
| `ROLES`, `DEFAULT_ROLE` | The roles in the dropdown. A role needs an `audience-<key>` skill. |
| `ROLE_TEAMS` | Which teams each role sees, and so which tools its agent gets. |
| `MAX_STEPS`, `SYSTEM_PROMPT`, `DOCS_PROMPT` | The step limit, and the instructions for a code check and for a docs-only lookup. |

How the code is reviewed is in `harness/skills/code-review/SKILL.md`, and the answer formats are in `audience-product/SKILL.md` and `audience-it/SKILL.md`.

## Limitations

- **Keyword search.** It only matches whole words, and the requirements are in Danish, so the agent searches with ids and Danish words.
- **Every file name on every step.** `list_code_files` returns all files, which is slow on a large solution.
- **Local model.** Mistral 7B through Ollama is free and private, but slower and less reliable than a hosted frontier model, so the code double-checks its output (parsing the assessment format, dropping contradictions) rather than trusting it outright.
- **Saved assessments live in memory.** Restarting the server forgets them, so the next question is checked from scratch. A new file the agent didn't read last time doesn't change the fingerprint.
