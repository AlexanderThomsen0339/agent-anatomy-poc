"""Kodens repo: henter udviklerens kode fra Azure DevOps, og finder åbne pull requests.

Hvorfor en lokal kopi?
list_code_files og read_code_file læser filer i en mappe. Med en kopi af repoet
virker de uændret, og git ls-files ved stadig, hvad der er kode.

Hvorfor REST og ikke git til PR'er?
Git kender branches, men ikke PR'er. Titlen og målbranchen findes kun i Azure DevOps' API.
"""
import base64
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from tools import PullRequest


class GitRepository:

    def __init__(self, url: str, folder: str | Path, token: str = ""):
        # Adresse og nøgle kommer fra settings.py. Mappen er kun en kopi, som POC'en selv styrer.
        self.url = url
        self.folder = Path(folder)
        self.token = token

    def sync(self, branch: str = "") -> str:
        """Gør kopien lig med branchen (tom betyder repoets standardbranch). Returnerer den commit, koden står på.

        Kaldes ved start, før siden tager imod spørgsmål, og derefter kun med CheckoutService' lås,
        så to spørgsmål ikke ændrer kopien på samme tid.
        """
        if not (self.folder / ".git").is_dir():
            self.folder.parent.mkdir(parents=True, exist_ok=True)
            self._git("clone", self.url, str(self.folder), cwd=None)
        # Kopien følger altid CODE_REPO, også når adressen er skiftet, efter kopien blev lavet.
        self._git("remote", "set-url", "origin", self.url)
        # Hvorfor fetch og reset i stedet for checkout og pull?
        # Mappen er kun en kopi. Reset gør den altid lig med branchen i repoet, også hvis nogen har force-pushet,
        # og der skal ikke holdes styr på lokale branches.
        self._git("fetch", "origin", self._remote_branch(branch) if branch else "HEAD")
        self._git("reset", "--hard", "FETCH_HEAD")
        # Reset fjerner ikke filer, git ikke kender. Uden clean bliver filer fra en anden branch eller et gammelt repo
        # liggende, og list_code_files viser dem stadig.
        self._git("clean", "-ffdx")
        return self._git("rev-parse", "--short", "HEAD").strip()

    def _remote_branch(self, branch: str) -> str:
        """Branchens navn, som det står i repoet.

        Hvorfor?
        Git skelner mellem store og små bogstaver, så "Dev" findes ikke, hvis branchen hedder "dev".
        Findes branchen slet ikke, siger fejlen, hvilke branches repoet har, så man kan rette CODE_BRANCH eller CODE_REPO.
        """
        heads = [line.split("refs/heads/", 1)[1] for line in self._git("ls-remote", "--heads", "origin").splitlines() if "refs/heads/" in line]
        if branch in heads:
            return branch
        same = [h for h in heads if h.lower() == branch.lower()]
        if same:
            return same[0]
        raise RuntimeError(
            f"branchen {branch} findes ikke i {self.url}. Repoet har: {', '.join(heads) or 'ingen branches'}. "
            "Ret CODE_BRANCH (eller CODE_REPO) i settings.py"
        )

    def changed_files(self, since: str) -> list[str]:
        # Fejler, hvis commit'en ikke findes længere, fx efter en force-push. Så tjekkes al koden igen.
        return self._git("diff", "--name-only", since, "HEAD").splitlines()

    def _git(self, *args: str, cwd: Path | None | str = "") -> str:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        if self.token:
            # Hvorfor en header og ikke nøglen i adressen?
            # En adresse med nøgle gemmes i .git/config og vises i fejlbeskeder og i Sources-boksen.
            # Headeren gives kun til git-processen via miljøet og gemmes ingen steder.
            # Azure DevOps tager en Personal Access Token som Basic-login med tomt brugernavn.
            auth = base64.b64encode(f":{self.token}".encode()).decode()
            env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="http.extraHeader", GIT_CONFIG_VALUE_0=f"Authorization: Basic {auth}")
        result = subprocess.run(
            ["git", *args], cwd=self.folder if cwd == "" else cwd,
            capture_output=True, text=True, encoding="utf-8", env=env,
        )
        if result.returncode != 0:
            error = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unknown error"
            # Den hyppigste fejl er en manglende eller udløbet nøgle. Git siger det kryptisk, så vi siger det tydeligt.
            if "Username" in error or "Authentication failed" in error or "403" in error:
                error += " (is AZURE_DEVOPS_PAT in local_secrets.py set and allowed to read Code?)"
            raise RuntimeError(f"git {args[0]} failed: {error}")
        return result.stdout


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
