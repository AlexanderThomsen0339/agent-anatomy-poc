# Kodetjek

POC'en til forretningsdemoen: en udvikler spørger AI'en, om den kode, udvikleren har skrevet, løser opgaven, og AI'en ser i koden og svarer ud fra user stories og testcases.

Mappen er en **fuld kopi** af de fem lag i roden af repoet (LLM, RAG, MCP, Skills, Agent). Originalen røres ikke og står som reference. Alt, hvad Kodetjek skal kunne, bygges her.

## Forskelle fra originalen

| Hvad | Originalen | Kodetjek |
|---|---|---|
| Konfiguration | En `config/` pr. lag | Én samlet [`settings.py`](settings.py) |
| Data | Markdown-dokumenter om et bibliotek | RAG-laget søger i `RAG/data/` med user stories og testcases i xlsx |
| Pakker | `requirements.txt` i roden | Egen [`requirements.txt`](requirements.txt), som også har `openpyxl` |

Lagenes egne README-filer er kopieret fra originalen og beskriver stadig mest biblioteksdemoen. Hvor de nævner `config/`, gælder `settings.py` i stedet, og værktøjerne `get_time` og `calculate` er fjernet i Kodetjek.

## Kom i gang

Kræver Python 3.10 eller nyere. Alle kommandoer køres fra **Kodetjek-mappen**, så lagene her bruges og ikke originalen.

```bash
cd Kodetjek
pip install -r requirements.txt

python -m LLM.api.cli "Hvad er en LLM?" --fake
python -m RAG.api.cli "Hvad er acceptkriterierne for download af faktura?" --fake
python -m MCP.api.cli list
python -m Skills.api.cli catalog
python -m Agent.api.cli "Løser vores kode US-001 Vis regningsoversigt?" --fake
```

Uden `--fake` kræves `ANTHROPIC_API_KEY`, som beskrevet i [README i roden](../README.md).

## Data

`RAG/data/` indeholder user stories og testcases for Mit Aalborg Forsyning:

- `Mit Aalborg Forsyning_Mit Overblik_Testcases.xlsx`
- `Mit Aalborg Forsyning_Regninger_Testcases.xlsx`
- `Testcases_minprofil_mitaalborgforsyning.xlsx`

RAG-laget læser dem med `XlsxLoader` (`RAG/infrastructure/loaders/xlsx_loader.py`). Hvert ark bliver ét dokument, og hver user story og testcase bliver ét afsnit, som ordsøgningen kan finde. Testresultaterne pr. testdato kommer med i teksten.

MCP-laget har værktøjet `search_requirements`, som søger i de samme data, så agenten kan slå kravene op selv. Bibliotekets `search_docs` er der stadig, indtil agenten er lavet om til kodetjek.

## Udviklerens kode

`list_code_files` og `read_code_file` lader agenten se den kode, der skal tjekkes. De kan kun læse, og kun i mappen `CODE_FOLDER` i `settings.py` (som standard `Kodetjek/eksempel/`). Peg `CODE_FOLDER` på en anden mappe for at tjekke anden kode.

## Agenten

Agenten er en kodetjekker: systemprompten i `settings.py` beder den slå kravene op med `search_requirements`, læse koden og svare efter skillen `kodevurdering`.

Uden API-nøgle (`--fake`) bruges `RuleBrain` (`Agent/infrastructure/brains/rule_brain.py`). Den tager dit spørgsmål, finder den bedste user story, læser de filer, hvis navne ligner user storyens titel, og viser for hvert acceptkriterie, hvor kriteriets ord står i koden. Værktøjskaldene er ægte, men vurderingen er kun ord-matchning, ikke en AI-vurdering, og det står i svaret.
