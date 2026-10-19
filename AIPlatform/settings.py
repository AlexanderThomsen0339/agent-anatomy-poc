"""Den samlede konfiguration for AI Platform POC'en.

Hvorfor én fil i stedet for en config/ pr. lag?
I originalen har hvert lag sin egen config/, så lagene kan stå alene.
AI Platform POC'en er én POC, der skal vises samlet, så alt, man kan skrue på,
står her ét sted.
"""
import os
from pathlib import Path

# Roden af AIPlatform-mappen. Alle stier herunder regnes ud fra den.
ROOT = Path(__file__).resolve().parent


# 1. Model
# Gemini-modellen, der tænker i agenten.
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


# 2. RAG
# Mappen med user stories og testcases (.xlsx), som search_requirements søger i.
DATA_FOLDER = ROOT / "RAG" / "data"

# Mappen med forretningens kravspec (.md), som search_specification søger i.
# Hvert krav har et id som KRAV-REG-03 og en linje "Dækker:" med de user stories og testcases, det hører til.
SPEC_FOLDER = ROOT / "RAG" / "data" / "kravspec"


# 3. MCP
# Hvor mange afsnit kravsøgningen returnerer.
SEARCH_K = 3

# Mappen med udviklerens kode, som list_code_files og read_code_file må læse i.
# Peg den på den kode, der skal tjekkes. Værktøjerne kan ikke se uden for mappen.
CODE_FOLDER = ROOT / "C:\\Users\\n1majt\\source\\repos\\FremsynNordDK"


# 4. Skills
# Mappen med skills. Hver skill er en undermappe med en SKILL.md.
SKILLS_FOLDER = ROOT / "Skills" / "data" / "skills"

# Holdet, der ejer koden i CODE_FOLDER. Agenten tjekker koden mod, hvordan holdet koder,
# beskrevet i skillen architecture-<TEAM>, fx architecture-web.
# Hvorfor pr. hold? Web og FDAP koder ikke efter de samme retningslinjer, så hvert hold har sin egen skill.
# Skillen er fast og uafhængig af projektet og af kravene i RAG.
TEAM = "web"

# Rollerne, man kan vælge på siden. Rollen bestemmer, hvordan svaret skrives, beskrevet i skillen audience-<rolle>.
# Hvorfor? En udvikler vil have kode og file:line, mens en fra kommunikation vil vide, hvad kunden oplever.
# Nøglen er skillens navn, værdien er det, brugeren ser i dropdownen.
ROLES = {
    "product": "Product / communication",
    "developer": "Developer",
}
DEFAULT_ROLE = "product"


# 5. Agent
# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
# Et kodetjek skal både søge krav og kravspec, hente to skills, liste filer og læse flere filer, så den er sat højere end i originalen.
MAX_STEPS = 20

# Grundinstruktionen. Kataloget over skills sættes på i Agent/api/build.py.
SYSTEM_PROMPT = (
    "You help people check whether the code solves the task. The reader may not be a developer, "
    "so answer in plain English and keep technical details in references. Always answer in English.\n"
    "The tasks are user stories and test cases for Mit Aalborg Forsyning, found with search_requirements. "
    "They are written in Danish, so search with ids and Danish words.\n"
    "The business requirements (kravspec) are found with search_specification. They say what the business ordered, "
    "and the test cases say what the test team checks. Check the code against both.\n"
    "You see the developer's code with list_code_files and read_code_file. You can only read the code, never change it.\n"
    "Never guess: look up the requirements and read the code before you answer. "
    "If a requirement is not written down anywhere, say it is not documented instead of inventing one.\n"
    "If a task fits a skill, load it with load_skill before you start."
)
