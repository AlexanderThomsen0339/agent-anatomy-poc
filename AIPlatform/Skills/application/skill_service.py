"""SkillService: laver kataloget og henter den rigtige skill."""
from Skills.domain.models import Skill, SkillSummary
from Skills.domain.ports import SkillRepository


class SkillService:

    def __init__(self, repository: SkillRepository):
        # Vi får reolen udefra. Servicen er ligeglad med, hvor den står.
        self.repository = repository

    def list_skills(self) -> list[SkillSummary]:
        """Alle skills med navn og beskrivelse."""
        return self.repository.list()

    def catalog(self, hide: str = "") -> str:
        """Indholdsfortegnelsen som tekst. Det er det, LLM'en altid får at se.

        hide skjuler skills, hvis navn starter med det, fx de skills, agenten ikke selv skal hente.
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
