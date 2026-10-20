"""Finder åbne pull requests i Azure DevOps, så kodetjekket kan se den branch, en udvikler arbejder på.

Hvorfor REST og ikke git?
Git kender branches, men ikke PR'er. Titlen og målbranchen findes kun i Azure DevOps' API.
"""
import base64
import json
import re
import urllib.error
import urllib.request
from urllib.parse import urlparse

from MCP.domain.models import PullRequest

# Et user story-id i et spørgsmål, en PR-titel eller et branch-navn: US-005, US_5, us005 eller feature/US-005-filnavn.
US_ID = re.compile(r"US[-_ ]?(\d+)", re.IGNORECASE)


def us_ids(text: str) -> set[int]:
    """Tallene i user story-id'erne, så US-5, US_005 og US-005 er det samme."""
    return {int(n) for n in US_ID.findall(text)}


class AzurePullRequestFinder:

    def __init__(self, repo_url: str, token: str, target_branch: str):
        # Repoets adresse er https://dev.azure.com/<org>/<projekt>/_git/<repo>.
        # Hedder projektet det samme som repoet, kan Azure udelade det: https://dev.azure.com/<org>/_git/<repo>.
        parts = urlparse(repo_url).path.strip("/").split("/")
        git = parts.index("_git")
        org, repo = parts[0], parts[git + 1]
        project = parts[1] if git == 2 else repo
        self.api = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests"
        self.repo_url = repo_url
        self.token = token
        self.target_branch = target_branch

    def find(self, question: str) -> PullRequest | None:
        # Kun spørgsmål med et user story-id kan passe til en PR. Uden id bruges dev.
        wanted = us_ids(question)
        if not wanted:
            return None
        # Nyeste først, så den nyeste PR vinder, hvis flere passer.
        for record in sorted(self._open_pull_requests(), key=lambda r: r.get("creationDate", ""), reverse=True):
            branch = record.get("sourceRefName", "").removeprefix("refs/heads/")
            if wanted & us_ids(f"{record.get('title', '')} {branch}"):
                pr_id = record["pullRequestId"]
                return PullRequest(pr_id, record.get("title", ""), branch, f"{self.repo_url}/pullrequest/{pr_id}")
        return None

    def _open_pull_requests(self) -> list[dict]:
        # Kun åbne PR'er ind i dev. PR'er fra dev ind i main er udgivelser, ikke en udviklers arbejde.
        query = f"searchCriteria.status=active&searchCriteria.targetRefName=refs/heads/{self.target_branch}&api-version=7.1"
        auth = base64.b64encode(f":{self.token}".encode()).decode()
        request = urllib.request.Request(f"{self.api}?{query}", headers={"Authorization": f"Basic {auth}", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8")
                # Azure svarer med en login-side (HTML) i stedet for en fejl, hvis nøglen ikke virker.
                if "json" not in response.headers.get("Content-Type", ""):
                    raise RuntimeError("Azure DevOps did not accept AZURE_DEVOPS_PAT (it needs Code: Read)")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Azure DevOps answered {e.code} (is AZURE_DEVOPS_PAT allowed to read Code?)") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Could not reach Azure DevOps: {e.reason}") from e
        return json.loads(body).get("value", [])
