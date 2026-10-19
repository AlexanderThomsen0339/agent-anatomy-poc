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

# Mappen med OT-holdets dokumenter (.xlsx og .pdf), som search_ot_documents søger i, fx signallisten for anlægget.
# Hvert ark læses som en tabel, og hver række bliver ét afsnit. Hver side i en PDF bliver ét afsnit.
# Filerne ignoreres af git, fordi de beskriver et rigtigt anlæg. Læg dem selv i mappen.
OT_FOLDER = ROOT / "RAG" / "data" / "ot"


# 3. MCP
# Hvor mange afsnit kravsøgningen returnerer.
SEARCH_K = 3

# Hvor mange signaler eller rækker OT-søgningen returnerer. Lidt flere end kravsøgningen,
# fordi et spørgsmål som "kølevandspumpe 2" ofte rammer flere signaler på samme pumpe.
OT_SEARCH_K = 5

# Mappen med udviklerens kode, som list_code_files og read_code_file må læse i.
# Peg den på den kode, der skal tjekkes. Værktøjerne kan ikke se uden for mappen.
CODE_FOLDER = ROOT / "C:\\Users\\n1majt\\source\\repos\\FremsynNordDK"


# 4. Skills
# Mappen med skills. Hver skill er en undermappe med en SKILL.md.
SKILLS_FOLDER = ROOT / "Skills" / "data" / "skills"

# IT's hold, og hvad hvert hold laver. Agenterne får beskrivelsen, så de ved, hvis kode eller dokumenter de ser på.
# Hvorfor her? IT har flere hold, og hver rolle ser ét eller flere af dem (ROLE_TEAMS herunder).
TEAMS = {
    "web": "builds Mit Aalborg Forsyning (Umbraco). Its code is checked against the user stories, test cases and kravspec.",
    "ot": "runs the plant's control systems (OT) and makes their documents, such as the signal list.",
}

# Holdet, der ejer koden i CODE_FOLDER. Agenten tjekker koden mod, hvordan holdet koder,
# beskrevet i skillen architecture-<TEAM>, fx architecture-web.
# Hvorfor pr. hold? Web og FDAP koder ikke efter de samme retningslinjer, så hvert hold har sin egen skill.
# Skillen er fast og uafhængig af projektet og af kravene i RAG.
TEAM = "web"

# Holdet, der laver dokumenterne i OT_FOLDER, som search_ot_documents søger i.
DOCUMENT_TEAM = "ot"

# Rollerne, man kan vælge på siden. Nøglen står i adressen, værdien er det, brugeren ser i dropdownen.
# Et kodetjek skrives om til rollen med skillen audience-<rolle>, så en rolle, der ser TEAM, skal have sådan en skill.
# Hvorfor? En udvikler vil have kode og file:line, mens en fra kommunikation vil vide, hvad kunden oplever.
ROLES = {
    "product": "Product / communication",
    "it": "IT",
    "maintenance": "Vedligehold",
}
DEFAULT_ROLE = "product"

# Hvilke hold hver rolle ser. Det er det, der bestemmer, hvilken agent en rolle får:
# TEAM giver krav og kode (kodetjek), DOCUMENT_TEAM giver OT's dokumenter (search_ot_documents).
# Hvorfor? IT dækker både web og OT, så IT ser begge. Vedligehold ser kun OT's dokumenter,
# og Product / communication kun web's kode. AI'en vælger ikke selv; den får kun værktøjerne til rollens hold.
ROLE_TEAMS = {
    "product": ["web"],
    "it": ["web", "ot"],
    "maintenance": ["ot"],
}


# 5. Agent
# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
# Et kodetjek skal både søge krav og kravspec, hente to skills, liste filer og læse flere filer, så den er sat højere end i originalen.
MAX_STEPS = 20

# Instruktionen til kodetjek, for roller der ser TEAM. Kataloget over skills sættes på i Agent/api/build.py.
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

# Instruktionen til opslag i OT's dokumenter, for roller der ser DOCUMENT_TEAM. Agenten svarer direkte, uden vurdering.
OT_PROMPT = (
    "You help people find information in the documents the OT team makes, "
    "such as the plant's signal list. Always answer in English, in plain language.\n"
    "Find everything with search_ot_documents. The documents are in Danish, so search with signal codes "
    "(like MKF20AP001A) or short Danish words (like kølevandspumpe). If the first search misses, try other words.\n"
    "Answer short: what was asked, then the signal or row it comes from with its name in both the old and the new system, "
    "its description, unit and range when they are there. End each point with the document and sheet in brackets.\n"
    "If several rows match, list at most 5 and say which detail would tell them apart.\n"
    "If the user asks which document contains certain words, or puts words in quotes, search with exact set to true "
    "and answer with every document and page that contains them, word for word.\n"
    "Never guess: if the documents don't say it, say it is not in OT's documents."
)
