"""Uret: fortæller dato og klokkeslæt.

Et godt første værktøj, fordi en LLM aldrig selv ved, hvad klokken er.
"""
from datetime import datetime

from MCP.domain.models import ToolSpec


class TimeTool:

    spec = ToolSpec(
        name="get_time",
        description="Giver dato og klokkeslæt lige nu. Brug det, når svaret afhænger af tiden.",
    )

    def run(self, arguments: dict) -> str:
        return datetime.now().strftime("%A %d-%m-%Y kl. %H:%M")
