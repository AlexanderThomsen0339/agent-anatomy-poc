"""Samler Skills-laget: vælger hvor skills hentes fra."""
import settings
from Skills.application.skill_service import SkillService
from Skills.infrastructure.file_skill_repository import FileSkillRepository


def build_service() -> SkillService:
    # 3: SKILLS: Skills ligger som mapper med en SKILL.md i Skills/data/skills/.
    # FileSkillRepository læser dem, når der bliver spurgt. Tilbage til build_agent() (trin 4).
    repository = FileSkillRepository(settings.SKILLS_FOLDER)
    return SkillService(repository)
