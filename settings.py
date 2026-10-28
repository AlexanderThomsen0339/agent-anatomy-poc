"""Den samlede konfiguration for AI Platform POC'en.

Hvorfor én fil?
Alt, man kan skrue på, står her ét sted.
"""
import os
from pathlib import Path

# Roden af repoet. Alle stier herunder regnes ud fra den.
ROOT = Path(__file__).resolve().parent

# Mappen med skills, dokumenter, diagrammer og andet, der ikke er kode.
HARNESS = ROOT / "harness"


# 1. Model
# Hvilken hjerne tænker: "gemini" (Google, kræver en nøgle) eller "mistral" (lokal gennem Ollama).
BRAIN = "gemini"

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

# Den lokale Mistral-model, når BRAIN = "mistral", kørt gennem Ollama.
# Hentes med: ollama pull mistral:7b-instruct-v0.3-q4_K_M
MISTRAL_MODEL = "mistral:7b-instruct-v0.3-q4_K_M"

# Hvor Ollama lytter.
MISTRAL_BASE_URL = "http://localhost:11434"

# Hvor meget tekst (tokens) modellen må se på én gang. Sendes med hvert kald, så `ollama serve` er nok.
# Systemprompten fylder ca. 4.000, og commits, krav og kode kommer oveni. Mistral 7B kan højst 32.768.
MISTRAL_CONTEXT = 32768


# 2. RAG
# Mappen med user stories og testcases (.xlsx), som search_requirements søger i.
DATA_FOLDER = HARNESS / "data" / "test-protocols"

# Mappen med forretningens kravspec (.md), som search_specification søger i.
# Hvert krav har et id som KRAV-REG-03 og en linje "Dækker:" med de user stories og testcases, det hører til.
SPEC_FOLDER = HARNESS / "data" / "kravspec"


# 3. MCP
# Hvor mange afsnit kravsøgningen returnerer.
SEARCH_K = 3

# Repoet med udviklerens kode, som list_code_files og read_code_file læser i.
# POC'en kloner det ved start og henter det nyeste før hvert kodetjek, så en udvikler kan pushe og straks spørge.
# Sæt CODE_REPO til "" for i stedet at læse en mappe på computeren direkte (CODE_FOLDER herunder).

CODE_REPO = "https://dev.azure.com/AF-IT/AI%20platform%20POC/_git/AI%20platform%20POC"

# Branchen, der tjekkes, når ingen åben PR passer til spørgsmålet.
# IT's regel for git: feature-branch → PR ind i dev → dev ind i main. Har spørgsmålets user story (fx US-005)
# en åben PR ind i CODE_BRANCH, tjekkes PR'ens branch i stedet. PR'en passer, hvis id'et står i titlen eller branch-navnet.
CODE_BRANCH = "Dev"

# Repoet er privat, så git skal have en Personal Access Token fra Azure DevOps med læseadgang til Code.
# Skriv den i local_secrets.py:
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
SKILLS_FOLDER = HARNESS / "skills"

# IT's hold, og hvad det laver. Agenterne får beskrivelsen, så de ved, hvis kode de ser på.
TEAMS = {
    "web": "builds Mit Aalborg Forsyning in .NET (C#, ASP.NET Core). Its code is checked against the user stories, test cases and kravspec.",
}

# Holdet, der ejer koden i CODE_FOLDER. Agenten tjekker koden mod, hvordan holdet koder,
# beskrevet i skillen architecture-<TEAM>, fx architecture-web.
# Hvorfor pr. hold? Web og FDAP koder ikke efter de samme retningslinjer, så hvert hold har sin egen skill.
# Skillen er fast og uafhængig af projektet og af kravene i RAG.
TEAM = "web"

# Rollerne, man kan vælge på siden. Nøglen står i adressen, værdien er det, brugeren ser i dropdownen (på hvert sprog).
# Et kodetjek skrives om til rollen med skillen audience-<rolle>, så en rolle, der ser TEAM, skal have sådan en skill.
# Hvorfor? En udvikler vil have kode og file:line, mens en fra kommunikation vil vide, hvad kunden oplever.
ROLE_NAMES = {
    "da": {"product": "Produkt / kommunikation", "it": "IT"},
    "en": {"product": "Product / communication", "it": "IT"},
}
DEFAULT_ROLE = "product"

# Hvilke hold hver rolle ser. Det er det, der bestemmer, hvilken agent en rolle får.
ROLE_TEAMS = {
    "product": ["web"],
    "it": ["web"],
}


# 5. Sprog
# Sproget på siden og i svarene: "da" (dansk) eller "en" (engelsk).
# Hvorfor en indstilling? Brugerne er danske, men siden skal kunne vises på engelsk, fx til et skærmbillede.
# Den kan også sættes uden at rette filen: AIPLATFORM_LANGUAGE=en python web.py
LANGUAGE = os.environ.get("AIPLATFORM_LANGUAGE", "da")
if LANGUAGE not in ROLE_NAMES:
    LANGUAGE = "da"
ROLES = ROLE_NAMES[LANGUAGE]

# Det, der sættes sidst på hver instruktion, når sproget er engelsk.
# Hvorfor sidst? Skills og prompts siger "Danish" mange steder. Den sidste instruktion vinder,
# så de kan forblive som de er, og dansk virker præcis som før.
ENGLISH_NOTE = (
    "\n\nLANGUAGE: Write everything the user reads in English, even where the instructions above say Danish: "
    "answers, questions to the user, and the requirement and why parts of an assessment. "
    "The test protocols and requirements are in Danish: keep searching with Danish words, but translate titles and requirements "
    "into English when you write them. Ids, file names, code and the status words stay as they are. "
    "Use these headings instead of the Danish ones: Missing, Can't tell, Architecture, Fix first, and write Fix: instead of Ret:."
)
# Det samme for dansk. En lille lokal model falder tilbage til engelsk, især i opfølgende svar,
# fordi reglerne er på engelsk. Derfor siges det til sidst i hver instruktion.
DANISH_NOTE = (
    "\n\nLANGUAGE: Write everything the user reads in Danish, also in follow-up answers and even when the "
    "instructions, the commits or the code are in English. Ids, file names, code and the status words stay as they are."
)
LANGUAGE_NOTE = ENGLISH_NOTE if LANGUAGE == "en" else DANISH_NOTE


# 6. Agent
# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
# Et kodetjek skal både søge krav og kravspec, hente to skills, liste filer og læse flere filer, så den er sat højere end i originalen.
MAX_STEPS = 20

# Lader koden søge kravene og læse de ændrede filer, før modellen tænker første gang (first_steps i web.py).
# Hvorfor? En lille lokal model springer ellers værktøjerne over og gætter ud fra commits alene.
# Gemini slår selv op, så den får det kun med BRAIN = "mistral". Sæt den til True for at prøve det med Gemini.
FIRST_STEPS = BRAIN == "mistral"
# Højst så mange af de filer, de nyeste commits ændrede, læses på forhånd, og kun kodefiler.
FIRST_FILES = 3
FIRST_FILE_TYPES = (".cs", ".cshtml", ".razor", ".js", ".ts", ".py")

# Instruktionen til kodetjek, for roller der ser TEAM. Skillsne code-review og architecture-<TEAM> sættes på i build.py.
SYSTEM_PROMPT = (
    "You check whether the code solves a task, and write an assessment by the code-review rules. "
    "You never write the answer for the person asking: another step turns your assessment into that answer.\n"
    "The tasks are user stories and test cases for Mit Aalborg Forsyning, found with search_requirements. "
    "The business requirements (kravspec) are found with search_specification. Both are written in Danish.\n"
    "You see the developer's code with list_code_files and read_code_file, and the newest commits with list_recent_changes. "
    "You can only read the code, never change it."
)

# Det, agenten får at vide, hvis dens svar hverken er vurderingslinjer eller et spørgsmål (én gang pr. kodetjek).
# En lille lokal model skriver ofte fri tekst i stedet for formatet, og så kan siden ikke læse en dom ud af svaret.
FORMAT_REMINDER = (
    "\n\nYour last answer could not be read, because it did not follow the code-review format. Do it again:\n"
    "1. If you have not found the user story yet, call search_requirements (and search_specification) first.\n"
    "2. Then write ONLY the assessment lines, one per requirement, seven parts separated by |:\n"
    "STATUS | ids | requirement | why in plain words | what the code does | file:line | how to fix\n"
    "STATUS is MET, NOT_MET, CANT_TELL or RISK. No other text, no headings, no summary.\n"
    "If the question is too unclear to assess, write QUESTION: and your question instead."
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
