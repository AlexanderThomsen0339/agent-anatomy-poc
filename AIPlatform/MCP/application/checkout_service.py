"""CheckoutService: vælger, hvilken kode kodetjekket ser.

IT's regel for git: en udvikler arbejder på en feature-branch, laver en PR ind i dev, og dev kommer senere ind i main.
Har spørgsmålets user story en åben PR ind i dev, er det den kode, der skal tjekkes. Ellers tjekkes dev.
"""
import threading

from MCP.domain.models import Checkout
from MCP.domain.ports import CodeRepository, PullRequestFinder, Tool


class CheckoutService:

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
