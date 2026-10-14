"""Kodelæseren: viser indholdet af én fil i udviklerens kodemappe.

Kun læsning. Der er bevidst intet værktøj, der kan skrive eller slette.
"""
from pathlib import Path

from MCP.domain.models import ToolSpec

# Hvorfor en grænse?
# Hele filen sendes med til LLM'en. En kæmpe fil koster mange tokens og drukner det vigtige.
MAX_CHARS = 20_000


class CodeReadTool:

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
        file = (self.folder / arguments["path"]).resolve()

        # Hvorfor tjekke stien?
        # LLM'en kunne bede om "../../hemmelig.txt". Alt uden for kodemappen afvises.
        if not file.is_relative_to(self.folder):
            return "Afvist: filen ligger uden for kodemappen."
        if not file.is_file():
            return f"File not found: {arguments['path']}"

        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "The file is not text and cannot be read."

        cut = len(text) > MAX_CHARS
        lines = text[:MAX_CHARS].splitlines()

        # Linjenumre, så svaret kan henvise til fil:linje.
        numbered = "\n".join(f"{i:4} | {line}" for i, line in enumerate(lines, start=1))
        if cut:
            numbered += f"\n... (afkortet efter {MAX_CHARS} tegn)"
        return numbered
