"""Samler Skills-laget: vælger hvor skills hentes fra."""
from Skills.application.skill_service import SkillService
from Skills.config import settings
from Skills.infrastructure.file_skill_repository import FileSkillRepository


def build_service() -> SkillService:
    # Her vælger vi reolen. Det eneste sted, det sker.
    repository = FileSkillRepository(settings.SKILLS_FOLDER)
    return SkillService(repository)
