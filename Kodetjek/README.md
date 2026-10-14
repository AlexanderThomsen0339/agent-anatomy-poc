# Kodetjek

POC'en til forretningsdemoen: en udvikler spørger AI'en, om den kode, udvikleren har skrevet, løser opgaven, og AI'en ser i koden og svarer ud fra user stories og testcases.

Mappen er en **fuld kopi** af de fem lag i roden af repoet (LLM, RAG, MCP, Skills, Agent). Originalen røres ikke og står som reference. Alt, hvad Kodetjek skal kunne, bygges her.

## Forskelle fra originalen

| Hvad | Originalen | Kodetjek |
|---|---|---|
| Konfiguration | En `config/` pr. lag | Én samlet [`settings.py`](settings.py) |
| Data | Markdown-dokumenter om et bibliotek | RAG-laget søger i `data/` med user stories og testcases i xlsx |
| Pakker | `requirements.txt` i roden | Egen [`requirements.txt`](requirements.txt), som også har `openpyxl` |

Lagenes egne README-filer er kopieret uændret, så hvor de nævner `config/`, gælder `settings.py` i stedet.

## Kom i gang

Kræver Python 3.10 eller nyere. Alle kommandoer køres fra **Kodetjek-mappen**, så lagene her bruges og ikke originalen.

```bash
cd Kodetjek
pip install -r requirements.txt

python -m LLM.api.cli "Hvad er en LLM?" --fake
python -m RAG.api.cli "Hvad er acceptkriterierne for download af faktura?" --fake
python -m MCP.api.cli list
python -m Skills.api.cli catalog
python -m Agent.api.cli --fake
```

Uden `--fake` kræves `ANTHROPIC_API_KEY`, som beskrevet i [README i roden](../README.md).

## Data

`data/` indeholder user stories og testcases for Mit Aalborg Forsyning:

- `Mit Aalborg Forsyning_Mit Overblik_Testcases.xlsx`
- `Mit Aalborg Forsyning_Regninger_Testcases.xlsx`
- `Testcases_minprofil_mitaalborgforsyning.xlsx`

RAG-laget læser dem med `XlsxLoader` (`RAG/infrastructure/loaders/xlsx_loader.py`). Hvert ark bliver ét dokument, og hver user story og testcase bliver ét afsnit, som ordsøgningen kan finde. Testresultaterne pr. testdato kommer med i teksten.

MCP- og Agent-laget søger stadig i bibliotekets dokumenter. Det er næste skridt.
