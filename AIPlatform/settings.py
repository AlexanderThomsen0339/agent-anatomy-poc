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
DATA_FOLDER = ROOT / "RAG" / "data" / "test-protocols"

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

# Repoet med udviklerens kode, som list_code_files og read_code_file læser i.
# POC'en kloner det ved start og henter det nyeste før hvert kodetjek, så en udvikler kan pushe og straks spørge.
# Sæt CODE_REPO til "" for i stedet at læse en mappe på computeren direkte (CODE_FOLDER herunder).

CODE_REPO = "https://dev.azure.com/AF-IT/AI%20platform%20POC/_git/AI%20platform%20POC"

# Branchen, der tjekkes, når ingen åben PR passer til spørgsmålet.
# IT's regel for git: feature-branch → PR ind i dev → dev ind i main. Har spørgsmålets user story (fx US-005)
# en åben PR ind i CODE_BRANCH, tjekkes PR'ens branch i stedet. PR'en passer, hvis id'et står i titlen eller branch-navnet.
CODE_BRANCH = "Dev"

# Repoet er privat, så git skal have en Personal Access Token fra Azure DevOps med læseadgang til Code.
# Skriv den i local_secrets.py ligesom Gemini-nøglen:
#     AZURE_DEVOPS_PAT = "your-token"
# Findes den ikke dér, læses den fra miljøvariablen AZURE_DEVOPS_PAT.
try:
    from local_secrets import AZURE_DEVOPS_PAT
except ImportError:
    AZURE_DEVOPS_PAT = os.environ.get("AZURE_DEVOPS_PAT", "")

# Mappen, værktøjerne læser koden fra. De kan ikke se uden for den.
# Med CODE_REPO er det POC'ens egen kopi af repoet (ignoreres af git). Uden er det din egen mappe med koden.
CODE_FOLDER = ROOT / "repos" / "code"


# 4. Skills
# Mappen med skills. Hver skill er en undermappe med en SKILL.md.
SKILLS_FOLDER = ROOT / "Skills" / "data" / "skills"

# IT's hold, og hvad hvert hold laver. Agenterne får beskrivelsen, så de ved, hvis kode eller dokumenter de ser på.
# Hvorfor her? IT har flere hold, og hver rolle ser ét eller flere af dem (ROLE_TEAMS herunder).
TEAMS = {
    "web": "builds Mit Aalborg Forsyning in .NET (C#, ASP.NET Core). Its code is checked against the user stories, test cases and kravspec.",
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
    "product": "Produkt / kommunikation",
    "it": "IT",
    "maintenance": "Vedligehold",
}
DEFAULT_ROLE = "product"

# Hvilke hold hver rolle ser. Det er det, der bestemmer, hvilken agent en rolle får:
# TEAM giver krav og kode (kodetjek), DOCUMENT_TEAM giver OT's dokumenter (search_ot_documents).
# Hvorfor? IT dækker både web og OT, så IT ser begge. Vedligehold ser kun OT's dokumenter,
# og Produkt / kommunikation kun web's kode. AI'en vælger ikke selv; den får kun værktøjerne til rollens hold.
ROLE_TEAMS = {
    "product": ["web"],
    "it": ["web", "ot"],
    "maintenance": ["ot"],
}


# 5. Agent
# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
# Et kodetjek skal både søge krav og kravspec, hente to skills, liste filer og læse flere filer, så den er sat højere end i originalen.
MAX_STEPS = 20

# Instruktionen til kodetjek, for roller der ser TEAM. Skillsne code-review og architecture-<TEAM> sættes på i Agent/api/build.py.
SYSTEM_PROMPT = (
    "You check whether the code solves a task, and write an assessment by the code-review rules. "
    "You never write the answer for the person asking: another step turns your assessment into that answer.\n"
    "The tasks are user stories and test cases for Mit Aalborg Forsyning, found with search_requirements. "
    "The business requirements (kravspec) are found with search_specification. Both are written in Danish.\n"
    "You see the developer's code with list_code_files and read_code_file, and the newest commits with list_recent_changes. "
    "You can only read the code, never change it."
)

# Instruktionen til opslag i testprotokollerne og kravene, når et spørgsmål ikke kræver koden (Router: DOCS).
DOCS_PROMPT = (
    "You answer questions about the test protocols for Mit Aalborg Forsyning (user stories, acceptance criteria and test cases: "
    "list_requirements lists them all, search_requirements finds the details of one) and the business requirements (kravspec, found with search_specification). Both are in Danish.\n"
    "Each area (Regninger, Profil, Overblik) numbers its user stories from US-001, so always name the area with the id.\n"
    "You never see the code, so never say whether the code meets a test. If the user wants that, tell them they can ask, "
    "e.g. \"Virker Vis regningsoversigt?\".\n"
    "Answer in Danish, short and friendly, like a colleague.\n"
    "When asked which tests or user stories there are, call list_requirements and include every one of them: never leave one out. "
    "Group them by area (Regninger, Profil, Overblik), then one line per sheet with the number of tests and their titles. "
    "Otherwise answer in at most 15 lines. Never invent a test, user story or requirement."
)

# Grænsen for antal skridt for et opslag uden kode.
DOCS_MAX_STEPS = 6

# Instruktionen til opslag i OT's dokumenter, for roller der ser DOCUMENT_TEAM. Agenten svarer direkte, uden vurdering.
OT_PROMPT = (
    "You help people find information in the documents the OT team makes, "
    "such as the plant's signal list. Always answer in English, in plain language.\n"
    "Find everything with search_ot_documents. The documents are in Danish, so search with signal codes "
    "(like MKF20AP001A) or short Danish words (like kølevandspumpe). If the first search misses, try other words.\n"
    "Answer short: what was asked, then the signal or row it comes from with its name in both the old and the new system, "
    "its description, unit and range when they are there. End each point with the document and sheet in brackets.\n"
    "If several rows match, list at most 5 and say which detail would tell them apart.\n"
    "Results come as PDF documents first, then the signal list. For what something means, how it is done or why, "
    "answer from the PDF documents and name the file and page. Use the signal list for signal names, units and ranges.\n"
    "If the user asks which document contains certain words, or puts words in quotes, search with exact set to true "
    "and answer with every document and page that contains them, word for word.\n"
    "Never guess: if the documents don't say it, say it is not in OT's documents."
)
