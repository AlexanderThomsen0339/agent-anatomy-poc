"""Den samlede konfiguration for Kodetjek.

Hvorfor én fil i stedet for en config/ pr. lag?
I originalen har hvert lag sin egen config/, så lagene kan stå alene.
Kodetjek er én POC, der skal vises samlet, så alt, man kan skrue på,
står her ét sted.
"""
from pathlib import Path

# Roden af Kodetjek-mappen. Alle stier herunder regnes ud fra den.
ROOT = Path(__file__).resolve().parent


# 1. LLM
# Modellen, der svarer i LLM- og RAG-laget, og som tænker i agenten.
MODEL = "claude-sonnet-5-5"

# Grundinstruktionen, når LLM-laget bruges direkte.
LLM_SYSTEM_PROMPT = "Svar kort på dansk."


# 2. RAG
# Mappen med user stories og testcases (.xlsx), som RAG-laget søger i.
DATA_FOLDER = ROOT / "data"

# Bibliotekets dokumenter fra originalen. Bruges stadig af MCP-lagets search_docs.
DOCS_FOLDER = ROOT / "RAG" / "data" / "docs"

# Hvor mange afsnit der sendes med til modellen.
TOP_K = 3


# 3. MCP
# Navnet, MCP-klienter (fx Claude Desktop) ser serveren under.
SERVER_NAME = "kodetjek-tools"

# Hvor mange afsnit dokumentsøgningen returnerer.
SEARCH_K = 3


# 4. Skills
# Mappen med skills. Hver skill er en undermappe med en SKILL.md.
SKILLS_FOLDER = ROOT / "Skills" / "data" / "skills"


# 5. Agent
# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
MAX_STEPS = 8

# Grundinstruktionen. Kataloget over skills sættes på i Agent/api/build.py.
SYSTEM_PROMPT = (
    "Du er en hjælpsom assistent for Biblioteket Anatomi. Svar på dansk.\n"
    "Brug værktøjerne, når du har brug for viden eller skal regne. Gæt aldrig.\n"
    "Passer en opgave til en skill, så hent den med load_skill, før du går i gang."
)
