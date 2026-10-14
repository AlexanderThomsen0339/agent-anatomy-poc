# Kodetjek

POC'en til forretningsdemoen: en udvikler spørger AI'en, om den kode, udvikleren har skrevet, løser opgaven, og AI'en ser i koden og svarer ud fra user stories og testcases.

Kodetjek bygger på de samme fem lag som originalen i roden af repoet (LLM, RAG, MCP, Skills, Agent), med samme ports & adapters-struktur. Originalen røres ikke og står som reference, også for forklaringen af lagene i dens README-filer.

## Flowet

```
Udvikler: "Does our code solve US-001?"
   ▼
Agent ── vælger selv værktøjer ──┬─ load_skill("code-review")   Skills
                                 ├─ search_requirements(...)      MCP → RAG (xlsx)
                                 ├─ list_code_files()             MCP → CODE_FOLDER
                                 └─ read_code_file(...)           MCP → CODE_FOLDER
   ▼
Svar: hvert acceptkriterie med henvisning til fil:linje
```

## Kom i gang

Kræver Python 3.10 eller nyere. Alle kommandoer køres fra **Kodetjek-mappen**, så lagene her bruges og ikke originalen.

```bash
cd Kodetjek
pip install -r requirements.txt
```

Sæt `CODE_FOLDER` i [`settings.py`](settings.py) til roden af den kode, der skal tjekkes, fx:

```python
CODE_FOLDER = Path(r"C:\Users\...\source\repos\MitProjekt")
```

Kør så agenten:

```bash
python -m Agent.api.cli "Does our code solve US-001?" --fake
```

Uden `--fake` tænker en rigtig model. Hvilken bestemmes af `BRAIN` i `settings.py`:

- `"gemini"`: Googles Gemini (`GEMINI_MODEL`). Kræver en nøgle fra Google AI Studio. Læg den i en fil `local_secrets.py` i Kodetjek-mappen med linjen `GEMINI_API_KEY = "din-nøgle"`. Filen ignoreres af git. Alternativt miljøvariablen `GEMINI_API_KEY`.
- `"claude"`: Claude (`MODEL`). Kræver `ANTHROPIC_API_KEY`, som beskrevet i [README i roden](../README.md).

```bash
python -m Agent.api.cli "Does our code solve US-001?"
```

Koden, agenten læser, sendes til den valgte model. Læg aldrig nøglen i koden.

Eller som demo-webside, hvor man ser skridtene live. Åbn derefter http://localhost:8000:

```bash
python -m Agent.api.web          # eller med --fake
```

Hvert lag kan også prøves for sig:

```bash
python -m RAG.api.cli "acceptkriterier download faktura" --fake
python -m MCP.api.cli list
python -m MCP.api.cli call search_requirements query="acceptkriterier telefonnummer"
python -m MCP.api.cli call list_code_files
python -m Skills.api.cli show code-review
```

## Hvad ligger hvor

| Lag | Hvad Kodetjek bruger |
|---|---|
| `LLM/` | `LLMService` med `AnthropicProvider` eller `FakeProvider`. Bruges af RAG-laget. |
| `RAG/` | `XlsxLoader` læser `RAG/data/*.xlsx`. Hvert ark bliver ét dokument, og hver user story og testcase bliver ét afsnit i ordsøgningen (`KeywordIndex`). |
| `MCP/` | Tre værktøjer: `search_requirements` (søger i RAG-indekset), `list_code_files` og `read_code_file` (læser kun i `CODE_FOLDER`, aldrig uden for). Kan også startes som MCP-server med `python -m MCP.api.mcp_server`. |
| `Skills/` | Én skill, `code-review`, der beskriver hvordan svaret skal se ud. |
| `Agent/` | `GeminiBrain` eller `ClaudeBrain` med API-nøgle (vælges med `BRAIN`), `RuleBrain` med `--fake`. |
| [`settings.py`](settings.py) | Al konfiguration: model, datamappe, kodemappe, systemprompt, antal skridt. |

## Data

`RAG/data/` indeholder user stories og testcases for Mit Aalborg Forsyning:

- `Mit Aalborg Forsyning_Mit Overblik_Testcases.xlsx`
- `Mit Aalborg Forsyning_Regninger_Testcases.xlsx`
- `Testcases_minprofil_mitaalborgforsyning.xlsx`

## Udviklerens kode

`list_code_files` og `read_code_file` kan kun læse, og kun i `CODE_FOLDER`. Er mappen et git-repo, følger `list_code_files` repoets `.gitignore`, så `bin`, `obj`, `.vs` og lignende ikke kommer med. Nye filer, der ikke er committet endnu, kommer med.

## Uden API-nøgle

Med `--fake` bruges `RuleBrain` (`Agent/infrastructure/brains/rule_brain.py`). Den tager spørgsmålet, finder den bedste user story, læser op til fire filer, hvis navne ligner user storyens titel, og viser for hvert acceptkriterie, hvor kriteriets ord står i koden. Værktøjskaldene er ægte, men vurderingen er kun ord-matchning, ikke en AI-vurdering, og det står i svaret.

## Kendte begrænsninger

- **Ordsøgningen finder kun hele, ens ord.** Spørg med ord fra arkene, fx "acceptkriterier telefonnummer".
- **Samme id findes i flere ark.** TC-011 findes både i Regninger og Min Profil, så søg med ord og ikke kun id.
- **`list_code_files` sender alle filnavne.** I en stor løsning er det mange tokens, når Claude bruges.
