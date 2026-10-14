"""Kodeoversigten: lister filerne i udviklerens kodemappe.

LLM'en kan ikke se udviklerens maskine. Den får kun det, værktøjerne viser den,
og dette værktøj viser kun filnavne inden for én mappe.
"""
import subprocess
from pathlib import Path

from MCP.domain.models import ToolSpec

# Mapper, der aldrig er udviklerens egen kode. Bruges kun, hvis mappen ikke er et git-repo.
IGNORED_FOLDERS = {
    ".git", ".vs", ".idea", ".vscode", "__pycache__", "node_modules", ".venv", "venv",
    "bin", "obj", "dist", "build", "packages", "TestResults",
}


class CodeListTool:

    spec = ToolSpec(
        name="list_code_files",
        description="Lister filerne i udviklerens kode. Brug det først for at se, hvilke filer der findes.",
    )

    def __init__(self, folder: str | Path):
        # Mappen kommer fra settings.py. Værktøjet kan ikke se uden for den.
        self.folder = Path(folder)

    def run(self, arguments: dict) -> str:
        if not self.folder.is_dir():
            return f"Kodemappen findes ikke: {self.folder}"

        files = self._git_files() or self._all_files()
        return "\n".join(files) if files else "Kodemappen er tom."

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
