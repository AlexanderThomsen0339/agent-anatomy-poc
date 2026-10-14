"""load_skill som værktøj, så en LLM selv kan hente en skill.

Det er døren mellem lag 4 og lag 3: værktøjet passer i MCP-lagets stik (Tool),
så agenten kan bruge det på præcis samme måde som search_requirements og read_code_file.
"""
from MCP.domain.models import ToolSpec
from Skills.application.skill_service import SkillService


class LoadSkillTool:

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
        skill = self.service.load(arguments["name"])
        return skill.instructions
