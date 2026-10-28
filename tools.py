"""MCP: de værktøjer, agenten kan kalde, og valget af hvilken kode der tjekkes.

Hvorfor egne modeller?
Et værktøj skal kunne beskrives, kaldes og give et resultat på samme måde,
uanset om det er et ur, en lommeregner eller en søgning i dokumenter,
og uanset om kaldet kommer fra terminalen, en MCP-klient eller agenten.
"""
import threading
from dataclasses import dataclass, field
from typing import Protocol


# Hvorfor en ToolSpec?
# Det er mærkatet på apparatet: hvad det hedder, hvad det gør, og hvilke
# knapper det har. Det er netop det, en LLM skal læse for at vælge det rigtige
# værktøj, så beskrivelsen er lige så vigtig som koden bag.
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str

    # Hvorfor et JSON-skema?
    # Det er det fælles sprog for "hvilke argumenter tager værktøjet".
    input_schema: dict = field(default_factory=lambda: {"type": "object", "properties": {}})


# Hvorfor en ToolCall?
# Det er at trykke på knappen: hvilket værktøj og med hvilke argumenter.
# Det er præcis det, en LLM svarer med, når den vil bruge et værktøj.
@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    name: str

    # Hvorfor altid tekst?
    # Resultatet skal tilbage til en LLM, og den læser tekst.
    content: str

    # Hvorfor et fejl-flag i stedet for at kaste en fejl?
    # Går et værktøj galt, skal det ikke vælte hele systemet. LLM'en skal
    # i stedet kunne læse fejlen og prøve noget andet, ligesom en sikring,
    # der slår fra i ét rum uden at slukke strømmen i hele huset.
    is_error: bool = False


# Hvorfor en PullRequest?
# Kodetjekket skal kunne se den kode, en udvikler arbejder på, før den er merget ind i dev.
# Kun det, siden og branch-valget har brug for, kommer med: ikke Azure DevOps' eget format.
@dataclass(frozen=True)
class PullRequest:
    id: int
    title: str
    branch: str
    url: str


# Hvorfor en Checkout?
# Den fortæller siden, hvilken kode agenten ser: branch, commit og den PR, branchen kom fra.
# note er en advarsel, fx at PR'erne ikke kunne hentes, så dev blev brugt.
@dataclass(frozen=True)
class Checkout:
    branch: str
    commit: str
    pull_request: PullRequest | None = None
    note: str = ""
    # De nyeste commits på branchen med de ændrede linjer. Agenten får dem altid som udgangspunkt.
    changes: str = ""


# Hvorfor er Tool en port?
# Det er stikkets form. Alle apparater, der har dette stik, kan sættes i:
# et ur, en lommeregner, en søgning i dokumenter, senere en kalender eller
# et API. Resten af koden ser aldrig, hvad der er inde i apparatet.
class Tool(Protocol):

    # Hvorfor er spec en egenskab og ikke en metode?
    # Mærkatet ændrer sig ikke, mens apparatet kører. Det læses, før man trykker på knappen.
    spec: ToolSpec

    # Hvorfor tager run() en dict og ikke rigtige parametre?
    # Argumenterne kommer fra en LLM eller en MCP-klient som JSON.
    # Alle værktøjer får dem i samme form, så de kan kaldes ens.
    def run(self, arguments: dict) -> str:
        """Udfører værktøjet og returnerer resultatet som tekst."""
        ...


# Hvorfor er repoet en port?
# Branch-valget skal ikke vide, om koden kommer fra Azure DevOps, GitHub eller en mappe.
class CodeRepository(Protocol):

    def sync(self, branch: str) -> str:
        """Gør kopien lig med branchen og returnerer den commit, koden står på."""
        ...

    def changed_files(self, since: str) -> list[str]:
        """Filerne, der er ændret fra commit since til den commit, kopien står på nu."""
        ...


class PullRequestFinder(Protocol):

    def find(self, question: str) -> PullRequest | None:
        """Den nyeste åbne PR, der passer til spørgsmålet, eller None."""
        ...


class ToolService:

    def __init__(self, tools: list[Tool]):
        # Vi får værktøjerne udefra og slår dem op på navn.
        self.tools = {tool.spec.name: tool for tool in tools}

    def list_tools(self) -> list[ToolSpec]:
        """Mærkaterne på alle værktøjer. Det er det, en LLM får at se."""
        return [tool.spec for tool in self.tools.values()]

    def call(self, call: ToolCall) -> ToolResult:
        """Kalder ét værktøj. Går det galt, får man en fejl tilbage i stedet for et nedbrud."""
        tool = self.tools.get(call.name)
        if tool is None:
            return ToolResult(call.name, f"Unknown tool: {call.name}", is_error=True)

        try:
            content = tool.run(call.arguments)
            return ToolResult(call.name, content)
        except Exception as error:
            # Sikringen slår fra: fejlen bliver til et resultat, som en LLM kan læse.
            return ToolResult(call.name, str(error), is_error=True)


class CheckoutService:
    """Vælger, hvilken kode kodetjekket ser.

    IT's regel for git: en udvikler arbejder på en feature-branch, laver en PR ind i dev, og dev kommer senere ind i main.
    Har spørgsmålets user story en åben PR ind i dev, er det den kode, der skal tjekkes. Ellers tjekkes dev.
    """

    def __init__(self, repository: CodeRepository, finder: PullRequestFinder | None, default_branch: str, changes: Tool | None = None):
        # Repoet og PR-søgningen kommer udefra. Uden PR-søgning (fx et repo uden for Azure DevOps) bruges altid default_branch.
        self.repository = repository
        self.finder = finder
        self.default_branch = default_branch
        # Værktøjet, der viser de seneste commits. Branch-valget kalder det selv, så AI'en ikke kan springe det over.
        self.changes = changes
        # Hvorfor en lås?
        # Der er kun én kopi af repoet. Siden holder låsen, mens et kodetjek kører,
        # så et andet spørgsmål ikke skifter branch midt i det.
        self.lock = threading.Lock()

    def checkout(self, question: str) -> Checkout:
        # Hvorfor vælger koden og ikke AI'en?
        # Så giver samme spørgsmål altid samme branch, og siden kan vise, hvorfor, før agenten starter.
        pull_request, note = None, ""
        if self.finder:
            try:
                pull_request = self.finder.find(question)
            except RuntimeError as e:
                note = f"Could not look for pull requests, so {self.default_branch} is used: {e}"
        branch = pull_request.branch if pull_request else self.default_branch
        commit = self.repository.sync(branch)
        # Hvorfor hente ændringerne her og ikke lade AI'en gøre det?
        # Spørger man "er kravene overholdt?", gik AI'en direkte til de filer, hvis navn passede (Billing),
        # og så aldrig, at en anden fil lige var ændret. Hentes de her, starter den altid fra dem.
        changes = self.changes.run({"count": 3}) if self.changes else ""
        return Checkout(branch, commit, pull_request, note, changes)

    def changed_since(self, commit: str) -> list[str] | None:
        """Filerne, der er ændret siden commit, eller None, hvis git ikke kan svare (så tjekkes al koden)."""
        try:
            return self.repository.changed_files(commit)
        except RuntimeError:
            return None
