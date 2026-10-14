# Kodetjek

POC'en til forretningsdemoen: en udvikler spørger AI'en, om den kode, udvikleren har skrevet, løser opgaven, og AI'en ser i koden og svarer ud fra user stories og testcases.

Kodetjek bygger på fire af lagene fra originalen i roden af repoet (RAG, MCP, Skills, Agent), med samme ports & adapters-struktur. LLM-laget er ikke med, fordi agentens hjerne selv taler med modellen. Originalen røres ikke og står som reference, også for forklaringen af lagene i dens README-filer.

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

Agenten tænker med Googles Gemini (`GEMINI_MODEL`). Det kræver en nøgle fra Google AI Studio. Læg den i en fil `local_secrets.py` i Kodetjek-mappen med linjen `GEMINI_API_KEY = "din-nøgle"`. Filen ignoreres af git. Alternativt miljøvariablen `GEMINI_API_KEY`. Koden, agenten læser, sendes til Gemini. Læg aldrig nøglen i koden.

Start demo-websiden, og åbn http://localhost:8000. Her ser man skridtene live:

```bash
python -m Agent.api.web
```

Eller kør agenten i terminalen:

```bash
python -m Agent.api.cli "Does our code solve US-001?"
```

Begge kan køres med `--fake` uden nøgle.

## Hvad ligger hvor

| Lag | Hvad Kodetjek bruger |
|---|---|
| `RAG/` | `XlsxLoader` læser `RAG/data/*.xlsx`. Hvert ark bliver ét dokument, og hver user story og testcase bliver ét afsnit i ordsøgningen (`KeywordIndex`). |
| `MCP/` | Tre værktøjer: `search_requirements` (søger i RAG-indekset), `list_code_files` og `read_code_file` (læser kun i `CODE_FOLDER`, aldrig uden for). |
| `Skills/` | Én skill, `code-review`, der beskriver hvordan svaret skal se ud. |
| `Agent/` | `GeminiBrain` med API-nøgle, `RuleBrain` med `--fake`. Demo-siden (`web.py`) og terminalen (`cli.py`). |
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
- **`list_code_files` sender alle filnavne.** I en stor løsning er det mange tokens i hvert skridt.
