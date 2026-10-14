"""Den samlede konfiguration for Kodetjek.

Hvorfor én fil i stedet for en config/ pr. lag?
I originalen har hvert lag sin egen config/, så lagene kan stå alene.
Kodetjek er én POC, der skal vises samlet, så alt, man kan skrue på,
står her ét sted.
"""
import os
from pathlib import Path

# Roden af Kodetjek-mappen. Alle stier herunder regnes ud fra den.
ROOT = Path(__file__).resolve().parent


# 1. LLM
# Modellen, der svarer i LLM- og RAG-laget, og som tænker i agenten, når BRAIN er "claude".
MODEL = "claude-sonnet-5-5"

# Hvilken model der tænker i agenten uden --fake: "claude" (kræver ANTHROPIC_API_KEY)
# eller "gemini" (kræver GEMINI_API_KEY).
BRAIN = "gemini"

# Gemini-modellen, når BRAIN er "gemini".
GEMINI_MODEL = "gemini-2.5-flash"

# Nøglen til Gemini. Læses fra miljøvariablen GEMINI_API_KEY, hvis den er sat.
# Midlertidigt kan nøglen skrives direkte her lokalt, men commit den aldrig.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Grundinstruktionen, når LLM-laget bruges direkte.
LLM_SYSTEM_PROMPT = "Svar kort på dansk."


# 2. RAG
# Mappen med user stories og testcases (.xlsx), som RAG-laget og MCP-lagets search_requirements søger i.
DATA_FOLDER = ROOT / "RAG" / "data"

# Hvor mange afsnit der sendes med til modellen.
TOP_K = 3


# 3. MCP
# Navnet, MCP-klienter (fx Claude Desktop) ser serveren under.
SERVER_NAME = "kodetjek-tools"

# Hvor mange afsnit kravsøgningen returnerer.
SEARCH_K = 3

# Mappen med udviklerens kode, som list_code_files og read_code_file må læse i.
# Peg den på den kode, der skal tjekkes. Værktøjerne kan ikke se uden for mappen.
CODE_FOLDER = ROOT / "C:\\Users\\n1majt\\source\\repos\\FremsynNordDK"


# 4. Skills
# Mappen med skills. Hver skill er en undermappe med en SKILL.md.
SKILLS_FOLDER = ROOT / "Skills" / "data" / "skills"


# 5. Agent
# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
# Et kodetjek skal både søge krav, liste filer og læse flere filer, så den er sat højere end i originalen.
MAX_STEPS = 15

# Grundinstruktionen. Kataloget over skills sættes på i Agent/api/build.py.
SYSTEM_PROMPT = (
    "Du hjælper udviklere med at tjekke, om deres kode løser opgaven. Svar på dansk.\n"
    "Opgaverne er user stories og testcases for Mit Aalborg Forsyning, som du finder med search_requirements.\n"
    "Udviklerens kode ser du med list_code_files og read_code_file. Du kan kun læse koden, aldrig ændre den.\n"
    "Gæt aldrig: slå kravene op, og læs koden, før du svarer.\n"
    "Passer en opgave til en skill, så hent den med load_skill, før du går i gang."
)
