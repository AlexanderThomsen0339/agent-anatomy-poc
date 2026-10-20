"""Læser skills fra mapper. Hver skill er en mappe med en SKILL.md.

    data/skills/
        mail/SKILL.md
        referat/SKILL.md

En SKILL.md ser sådan ud:

    ---
    name: mail
    description: Brug når brugeren vil have skrevet en mail.
    ---
    Instruktionerne står her.
"""
from pathlib import Path

from Skills.domain.models import Skill, SkillSummary


class FileSkillRepository:

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def list(self) -> list[SkillSummary]:
        summaries = []
        for file in sorted(self.folder.glob("*/SKILL.md")):
            skill = self._read(file)
            summaries.append(SkillSummary(skill.name, skill.description))
        return summaries

    def get(self, name: str) -> Skill | None:
        file = self.folder / name / "SKILL.md"
        if not file.exists():
            return None
        return self._read(file)

    @staticmethod
    def _read(file: Path) -> Skill:
        # Filen er delt i tre af "---": (tom) | navn og beskrivelse | instruktioner.
        _, header, body = file.read_text(encoding="utf-8").split("---", 2)

        fields = {}
        for line in header.strip().splitlines():
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()

        return Skill(
            name=fields["name"],
            description=fields["description"],
            instructions=body.strip(),
        )
