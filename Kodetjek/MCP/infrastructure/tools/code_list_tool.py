"""Kodeoversigten: lister filerne i udviklerens kodemappe.

LLM'en kan ikke se udviklerens maskine. Den får kun det, værktøjerne viser den,
og dette værktøj viser kun filnavne inden for én mappe.
"""
from pathlib import Path

from MCP.domain.models import ToolSpec

# Mapper, der aldrig er udviklerens egen kode.
IGNORED_FOLDERS = {".git", "__pycache__", "node_modules", ".venv", "venv", "bin", "obj", "dist", "build"}


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

        files = [
            path.relative_to(self.folder).as_posix()
            for path in sorted(self.folder.rglob("*"))
            if path.is_file() and not IGNORED_FOLDERS & set(path.relative_to(self.folder).parts)
        ]
        return "\n".join(files) if files else "Kodemappen er tom."
