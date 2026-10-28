"""Skills: genbrugelig know-how, fx hvordan vi vurderer, om kode løser en user story.

Hvorfor to modeller i stedet for én?
Det er hele idéen med skills. LLM'en ser ALTID kataloget (navn + beskrivelse),
men indholdet hentes KUN, når det skal bruges. Med mange skills ville det være
dyrt og forvirrende at sende al deres tekst med hvert eneste kald.

En skill ligger som en mappe med en SKILL.md:

    harness/skills/
        code-review/SKILL.md
        vocabulary/SKILL.md

En SKILL.md ser sådan ud:

    ---
    name: code-review
    description: Brug når nogen spørger, om koden løser en user story.
    ---
    Instruktionerne står her.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tools import ToolSpec


@dataclass(frozen=True)
class SkillSummary:
    """Titlen i indholdsfortegnelsen. Det, LLM'en altid ser."""

    name: str

    # Hvorfor er beskrivelsen så vigtig?
    # LLM'en vælger skill ud fra beskrivelsen alene, ligesom med værktøjer.
    # Den skal sige, HVORNÅR skillen skal bruges, ikke hvad der står i den.
    description: str


@dataclass(frozen=True)
class Skill:
    """Hele nodearket. Hentes først, når skillen skal bruges."""

    name: str
    description: str

    # Hvorfor bare tekst?
    # En skill er instruktioner til en LLM, og en LLM læser tekst.
    # Det gør også, at alle kan skrive en skill uden at kunne programmere.
    instructions: str


# Hvorfor en port til at hente skills?
# I dag ligger de som mapper med en SKILL.md. I morgen kan de ligge i en
# database, i SharePoint eller deles mellem flere teams.
class SkillRepository(Protocol):

    # Hvorfor en separat list() med kun titler?
    # Kataloget skal kunne laves billigt, uden at læse hver eneste skill i sin helhed.
    def list(self) -> list[SkillSummary]:
        """Alle skills med navn og beskrivelse."""
        ...

    # Hvorfor returnere None i stedet for at kaste en fejl?
    # At en skill ikke findes, er ikke en fejl i systemet. Det er et svar.
    def get(self, name: str) -> Skill | None:
        """Én skill med fuldt indhold, eller None hvis den ikke findes."""
        ...


class SkillService:

    def __init__(self, repository: SkillRepository):
        # Vi får reolen udefra. Servicen er ligeglad med, hvor den står.
        self.repository = repository

    def list_skills(self) -> list[SkillSummary]:
        """Alle skills med navn og beskrivelse."""
        return self.repository.list()

    def catalog(self, hide: str | tuple[str, ...] = "") -> str:
        """Indholdsfortegnelsen som tekst. Det er det, LLM'en altid får at se.

        hide skjuler skills, hvis navn starter med det (eller et af dem), fx de skills, agenten ikke selv skal hente.
        """
        lines = [f"- {s.name}: {s.description}" for s in self.list_skills() if not (hide and s.name.startswith(hide))]
        return "\n".join(lines) or "(no skills)"

    def load(self, name: str) -> Skill:
        """Henter hele skillen. Findes den ikke, får man at vide, hvilke der findes."""
        skill = self.repository.get(name)
        if skill is None:
            names = ", ".join(s.name for s in self.list_skills())
            raise ValueError(f"Unknown skill: {name}. Available: {names}")
        return skill


class FileSkillRepository:

    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def list(self) -> list[SkillSummary]:
        summaries = []
        for file in sorted(self.folder.glob("*/SKILL.md")):
            # En skill uden overskrift (name og description mellem "---") springes over, så siden stadig starter.
            try:
                skill = self._read(file)
            except ValueError:
                print(f"Skills: skipped {file}, it needs a header with name and description between --- lines")
                continue
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


class LoadSkillTool:
    """load_skill som værktøj, så en LLM selv kan hente en skill.

    Det er døren mellem skills og værktøjerne: værktøjet passer i tools-modulets stik (Tool),
    så agenten kan bruge det på præcis samme måde som search_requirements og read_code_file.
    """

    def __init__(self, service: SkillService):
        self.service = service

        # Mærkatet laves ud fra de skills, der findes lige nu,
        # så LLM'en kun kan vælge navne, der faktisk eksisterer.
        names = [s.name for s in service.list_skills()]
        self.spec = ToolSpec(
            name="load_skill",
            description=(
                "Loads the full instructions for a skill from the catalog. "
                "Use it before solving a task that a skill fits."
            ),
            input_schema={
                "type": "object",
                "properties": {"name": {"type": "string", "enum": names}},
                "required": ["name"],
            },
        )

    def run(self, arguments: dict) -> str:
        # Læser SKILL.md via SkillService.load() og FileSkillRepository.get().
        skill = self.service.load(arguments["name"])
        return skill.instructions
