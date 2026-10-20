"""CheckoutService: vælger, hvilken kode kodetjekket ser.

IT's regel for git: en udvikler arbejder på en feature-branch, laver en PR ind i dev, og dev kommer senere ind i main.
Har spørgsmålets user story en åben PR ind i dev, er det den kode, der skal tjekkes. Ellers tjekkes dev.
"""
import threading

from MCP.domain.models import Checkout
from MCP.domain.ports import CodeRepository, PullRequestFinder


class CheckoutService:

    def __init__(self, repository: CodeRepository, finder: PullRequestFinder | None, default_branch: str):
        # Repoet og PR-søgningen kommer udefra. Uden PR-søgning (fx et repo uden for Azure DevOps) bruges altid default_branch.
        self.repository = repository
        self.finder = finder
        self.default_branch = default_branch
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
        return Checkout(branch, self.repository.sync(branch), pull_request, note)
