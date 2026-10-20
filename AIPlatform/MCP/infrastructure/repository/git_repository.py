"""Kodens repo: henter udviklerens kode fra et git-repo, fx i Azure DevOps, til en lokal mappe.

Hvorfor en lokal kopi?
list_code_files og read_code_file læser filer i en mappe. Med en kopi af repoet
virker de uændret, og git ls-files ved stadig, hvad der er kode.
"""
import base64
import os
import subprocess
import threading
from pathlib import Path


class GitRepository:

    def __init__(self, url: str, folder: str | Path, branch: str = "", token: str = ""):
        # Adresse, gren og nøgle kommer fra settings.py. Mappen er kun en kopi, som POC'en selv styrer.
        self.url = url
        self.folder = Path(folder)
        self.branch = branch
        self.token = token
        # Siden kan tjekke to spørgsmål på én gang. Kun ét af dem må hente kode ad gangen.
        self.lock = threading.Lock()

    def sync(self) -> str:
        """Kloner repoet første gang, og henter derefter det nyeste. Returnerer den commit, koden står på."""
        with self.lock:
            return self._sync()

    def _sync(self) -> str:
        if not (self.folder / ".git").is_dir():
            self.folder.parent.mkdir(parents=True, exist_ok=True)
            self._git("clone", *(["--branch", self.branch] if self.branch else []), self.url, str(self.folder), cwd=None)
        else:
            # Hvorfor fetch og reset i stedet for pull?
            # Mappen er kun en kopi. Reset gør den altid lig med repoet, også hvis nogen har force-pushet.
            self._git("fetch", "origin", *([self.branch] if self.branch else []))
            self._git("reset", "--hard", "FETCH_HEAD")
        return self._git("rev-parse", "--short", "HEAD").strip()

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
