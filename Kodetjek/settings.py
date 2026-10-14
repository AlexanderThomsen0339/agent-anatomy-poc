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
GEMINI_MODEL = "gemini-3.5-flash-lite"

# Hvor meget Gemini tænker, før den svarer: "minimal", "low", "medium" eller "high".
# Mere tænkning giver grundigere svar, men hvert skridt tager længere tid.
# Sæt den til "", hvis modellen ikke kender niveauerne (fx gemini-2.5).
GEMINI_THINKING = "low"

# Nøglen til Gemini. Skriv den i local_secrets.py ved siden af denne fil:
#     GEMINI_API_KEY = "your-key"
# Den fil ignoreres af git, så nøglen aldrig kommer med i et commit.
# Findes filen ikke, læses nøglen fra miljøvariablen GEMINI_API_KEY.
try:
    from local_secrets import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Grundinstruktionen, når LLM-laget bruges direkte.
LLM_SYSTEM_PROMPT = "Answer briefly in English."


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
    "You help developers check whether their code solves the task. Always answer in English.\n"
    "The tasks are user stories and test cases for Mit Aalborg Forsyning, found with search_requirements. "
    "They are written in Danish, so search with ids and Danish words.\n"
    "You see the developer's code with list_code_files and read_code_file. You can only read the code, never change it.\n"
    "Never guess: look up the requirements and read the code before you answer.\n"
    "If a task fits a skill, load it with load_skill before you start."
)
