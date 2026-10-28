"""De seneste ændringer: de nyeste commits på branchen, med de linjer, der er ændret.

Hvorfor et værktøj til det?
Uden det ser agenten kun filerne, som de er nu, og læser dem, navnet peger på (fx BillingService).
En fejl, der lige er committet i en fil længere nede (fx en manager, som servicen kalder), opdager den ikke.
Med ændringerne foran sig kan den se, hvad der er rettet, og tjekke netop det mod testcasene.
"""
import subprocess
from pathlib import Path

from MCP.domain.models import ToolSpec

# Hvorfor en grænse?
# Hele svaret sendes med til LLM'en. En stor merge ville ellers drukne det vigtige.
MAX_CHARS = 15_000


class CodeChangesTool:

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

    def __init__(self, folder: str | Path, max_chars: int = MAX_CHARS):
        self.folder = Path(folder)
        self.max_chars = max_chars

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
        if len(text) > self.max_chars:
            text = text[:self.max_chars] + f"\n... (cut after {self.max_chars} characters, ask for fewer commits)"
        return text
