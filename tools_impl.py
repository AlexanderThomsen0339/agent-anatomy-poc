"""De værktøjer, agenten kan kalde: kode, krav og kravspec.

Kun læsning. Der er bevidst intet værktøj, der kan skrive eller slette.
"""
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from rag import Document, SearchIndex
from tools import ToolSpec

# Hvorfor en grænse?
# Hele svaret sendes med til LLM'en. En stor merge ville ellers drukne det vigtige.
MAX_CHARS = 15_000


class CodeChangesTool:
    """De seneste ændringer: de nyeste commits på branchen, med de linjer, der er ændret.

    Hvorfor et værktøj til det?
    Uden det ser agenten kun filerne, som de er nu, og læser dem, navnet peger på (fx BillingService).
    En fejl, der lige er committet i en fil længere nede (fx en manager, som servicen kalder), opdager den ikke.
    Med ændringerne foran sig kan den se, hvad der er rettet, og tjekke netop det mod testcasene.
    """

    spec = ToolSpec(
        name="list_recent_changes",
        description=(
            "Shows the newest commits on the branch being checked: message, author, date, changed files "
            "and the changed lines (diff). Use it to see what was changed lately."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Hvor mange commits, 1 til 10. Standard 3."},
            },
        },
    )

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def run(self, arguments: dict) -> str:
        count = max(1, min(int(arguments.get("count") or 3), 10))
        # --first-parent: en merge vises som én ændring (det, der kom ind i branchen), ikke som alle commits i feature-branchen.
        # -m sammen med --first-parent giver diff'en for en merge-commit mod branchen før merge.
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--first-parent", "-m", "--stat", "-p", "--format=commit %h  %ad  %an%n%s%n", "--date=short"],
                cwd=self.folder, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return "The code folder is not a git repo, so there is no history of changes."
        text = result.stdout.strip() or "No commits found."
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + f"\n... (cut after {MAX_CHARS} characters, ask for fewer commits)"
        return text


# Mapper, der aldrig er udviklerens egen kode. Bruges kun, hvis mappen ikke er et git-repo.
IGNORED_FOLDERS = {
    ".git", ".vs", ".idea", ".vscode", "__pycache__", "node_modules", ".venv", "venv",
    "bin", "obj", "dist", "build", "packages", "TestResults",
}


class CodeListTool:
    """Kodeoversigten: lister filerne i udviklerens kodemappe.

    LLM'en kan ikke se udviklerens maskine. Den får kun det, værktøjerne viser den,
    og dette værktøj viser kun filnavne inden for én mappe.
    """

    spec = ToolSpec(
        name="list_code_files",
        description="Lists the files in the developer's code. Use it first to see which files exist.",
    )

    def __init__(self, folder: str | Path):
        # Mappen kommer fra settings.py. Værktøjet kan ikke se uden for den.
        self.folder = Path(folder)

    def run(self, arguments: dict) -> str:
        # Alle filer i CODE_FOLDER, helst via git, så .gitignore respekteres.
        if not self.folder.is_dir():
            return f"Code folder not found: {self.folder}"

        files = self._git_files() or self._all_files()
        return "\n".join(files) if files else "The code folder is empty."

    def _git_files(self) -> list[str]:
        # Hvorfor spørge git?
        # Repoets .gitignore ved allerede, hvad der er kode, og hvad der er cache og build.
        # --others tager nye filer med, som udvikleren ikke har committet endnu.
        try:
            result = subprocess.run(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=self.folder, capture_output=True, text=True, encoding="utf-8", check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return []
        return sorted(line for line in result.stdout.splitlines() if (self.folder / line).is_file())

    def _all_files(self) -> list[str]:
        return [
            path.relative_to(self.folder).as_posix()
            for path in sorted(self.folder.rglob("*"))
            if path.is_file() and not IGNORED_FOLDERS & set(path.relative_to(self.folder).parts)
        ]


# Hvorfor en grænse?
# Hele filen sendes med til LLM'en. En kæmpe fil koster mange tokens og drukner det vigtige.
CODE_READ_MAX_CHARS = 20_000


class CodeReadTool:
    """Kodelæseren: viser indholdet af én fil i udviklerens kodemappe."""

    spec = ToolSpec(
        name="read_code_file",
        description=(
            "Reads one file from the developer's code, with line numbers. "
            "Use the path exactly as list_code_files shows it."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Filens sti, fx src/telefon.py"},
            },
            "required": ["path"],
        },
    )

    def __init__(self, folder: str | Path):
        self.folder = Path(folder).resolve()

    def run(self, arguments: dict) -> str:
        # Én fil fra CODE_FOLDER med linjenumre, så svaret kan henvise til fil:linje.
        file = (self.folder / arguments["path"]).resolve()

        # Hvorfor tjekke stien?
        # LLM'en kunne bede om "../../hemmelig.txt". Alt uden for kodemappen afvises.
        if not file.is_relative_to(self.folder):
            return "Refused: the file is outside the code folder."
        if not file.is_file():
            return f"File not found: {arguments['path']}"

        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "The file is not text and cannot be read."

        cut = len(text) > CODE_READ_MAX_CHARS
        lines = text[:CODE_READ_MAX_CHARS].splitlines()

        # Linjenumre, så svaret kan henvise til fil:linje.
        numbered = "\n".join(f"{i:4} | {line}" for i, line in enumerate(lines, start=1))
        if cut:
            numbered += f"\n... (cut after {CODE_READ_MAX_CHARS} characters)"
        return numbered


# Første linje i en blok, der er en user story eller en testcase, fx "US-ID: US-001" eller "TC-016: Ingen regninger".
BLOCK = re.compile(r"^(US-ID: |US-|TC-)", re.IGNORECASE)


def outline(documents: list[Document]) -> str:
    """Én linje pr. user story og testcase, under sit område og ark."""
    areas: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for document in documents:
        sheet = document.source.split(" › ")[-1]
        for block in document.text.split("\n\n"):
            lines = block.split("\n")
            area = lines[0].removeprefix("Område: ") if lines[0].startswith("Område: ") else "?"
            body = lines[1:] if lines[0].startswith("Område: ") else lines
            if not body or not BLOCK.match(body[0]):
                continue
            if body[0].startswith("US-ID: "):
                title = next((l.removeprefix("Titel: ") for l in body if l.startswith("Titel: ")), "")
                areas[area]["User stories"].append(f"{body[0].removeprefix('US-ID: ')} {title}")
            elif body[0].upper().startswith("TC-"):
                areas[area][sheet].append(body[0])
    out = []
    for area, sheets in areas.items():
        out.append(f"## {area}")
        for sheet, items in sheets.items():
            out.append(f"{sheet}: " + "; ".join(items))
    return "\n".join(out)


class RequirementsListTool:
    """Oversigten over alle testprotokoller: hver user story og hver testcase med titel, fordelt på område og ark.

    Hvorfor et værktøj ved siden af søgningen?
    Søgningen giver de få bedste træf. "Hvilke tests er der?" skal have dem alle, ellers mangler listen nogen.
    """

    spec = ToolSpec(
        name="list_requirements",
        description=(
            "Lists every user story and test case in the test protocols for Mit Aalborg Forsyning, "
            "with id and title, grouped by area (Regninger, Profil, Overblik) and sheet. "
            "Use it to answer which tests or user stories there are. Use search_requirements for the details of one."
        ),
        input_schema={"type": "object", "properties": {}},
    )

    def __init__(self, documents: list[Document]):
        # Oversigten laves én gang ved start ud fra de samme dokumenter, som søgningen indlæser.
        self.text = outline(documents) or "No test protocols found."

    def run(self, arguments: dict) -> str:
        return self.text


class RequirementsSearchTool:
    """Kravsøgningen: slår op i user stories og testcases.

    Det er RAG lavet om til et værktøj. Nu er det ikke koden, der altid søger først,
    men LLM'en, der selv vælger, om og hvad der skal søges efter (agentisk RAG).
    """

    spec = ToolSpec(
        name="search_requirements",
        description=(
            "Searches user stories, acceptance criteria and test cases for Mit Aalborg Forsyning's Regninger page. "
            "The data is in Danish: use ids like US-002 and TC-016, "
            "or short Danish keywords."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
            },
            "required": ["query"],
        },
    )

    def __init__(self, index: SearchIndex, k: int = 3):
        # Vi får indekset fra RAG udefra, allerede fyldt med user stories og testcases.
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        # Søger i indekset. Fortsæt i rag.py.
        results = self.index.search(arguments["query"], self.k)
        if not results:
            return "No results."
        return "\n\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)


class SpecificationSearchTool:
    """Kravspec-søgningen: slår op i forretningens krav (KRAV-ids).

    Hvorfor et værktøj ved siden af search_requirements?
    Testcases siger, hvad testholdet tjekker. Kravspec siger, hvad forretningen har bestilt.
    Det er to forskellige kilder, så agenten skal kunne se, hvilken et svar kommer fra,
    og opdage, når en user story slet ikke har et krav.
    """

    spec = ToolSpec(
        name="search_specification",
        description=(
            "Searches the business requirements specification (kravspec) for Mit Aalborg Forsyning. "
            "Each requirement has an id like KRAV-REG-03 and lists the user stories and test cases it covers. "
            "The data is in Danish: search with ids like KRAV-REG-03 or US-005, or short Danish keywords. "
            "If nothing is found, the user story has no documented business requirement."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
            },
            "required": ["query"],
        },
    )

    def __init__(self, index: SearchIndex, k: int = 3):
        # Et indeks kun med kravspec, så krav ikke drukner mellem testcases.
        self.index = index
        self.k = k

    def run(self, arguments: dict) -> str:
        query = arguments["query"]

        # Hvorfor et filter på user story-id?
        # Ordsøgning finder "US" i alle krav, så US-099 ville give krav, der intet har med den at gøre.
        # Spørges der på et id, returneres i stedet præcis de krav, hvis "Dækker"-linje nævner det.
        story_ids = {s.upper() for s in re.findall(r"\bUS-\d+\b", query, re.IGNORECASE)}
        if story_ids:
            results = [r for r in self.index.search(query, k=1000) if story_ids & covered_stories(r.chunk.text)]
        else:
            results = self.index.search(query, self.k)

        if not results:
            return "No requirement found in the specification. Report it as not documented; do not guess."
        return "\n\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)


def covered_stories(text: str) -> set[str]:
    """De user story-ids, som et krav dækker, læst fra linjen "Dækker:"."""
    for line in text.splitlines():
        if line.startswith("Dækker:"):
            return {s.upper() for s in re.findall(r"\bUS-\d+\b", line, re.IGNORECASE)}
    return set()
