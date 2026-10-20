"""Samler Agent-laget: hjernen, alle værktøjer og skills."""
import settings
from Agent.application.agent_service import AgentService
from Agent.application.answer_writer import AnswerWriter
from Agent.infrastructure.brains.gemini_brain import GeminiBrain
from MCP.api.build import build_service as build_tools
from MCP.application.tool_service import ToolService
from Skills.api.build import build_service as build_skills
from Skills.api.skill_tool import LoadSkillTool


def build_agent() -> AgentService:
    # 2: BYG AGENTEN: Her samles alle lag. Det sker én gang, når serveren starter.

    # 3: SKILLS: Fortsæt i Skills/api/build.py.
    skills = build_skills()

    # 4: VÆRKTØJER: Fortsæt i MCP/api/build.py. Her indlæses også xlsx-filerne (trin 5-8).
    mcp_tools = build_tools()

    # 9: SAML: Værktøjerne fra MCP plus load_skill fra Skills lægges i én ToolService.
    tools = ToolService(list(mcp_tools.tools.values()) + [LoadSkillTool(skills)])

    # Systemprompten: grundinstruktionen fra settings.py, holdet og kataloget over skills.
    # Holdet fortæller agenten, hvilken skill der beskriver, hvordan koden skal være bygget.
    system = (
        settings.SYSTEM_PROMPT
        + f"\nThe code belongs to the {settings.TEAM} team. Check it against how that team codes, in the skill architecture-{settings.TEAM}."
        # audience-skills skjules: rollen bruges først, når svaret skrives (AnswerWriter), aldrig i vurderingen.
        + "\n\nSkills:\n" + skills.catalog(hide="audience-")
    )

    # Hjernen, der taler med Gemini.
    brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)

    # Agenten er klar. Tilbage til main() i Agent/api/web.py (trin 10).
    return AgentService(brain, tools, system, max_steps=settings.MAX_STEPS)


def build_writer() -> AnswerWriter:
    # Skribenten, der laver vurderingen om til et svar til den valgte rolle (trin 20b).
    # Den får rollens skill (audience-<rolle>) fra Skills-laget, men ingen værktøjer.
    skills = build_skills()
    brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)
    return AnswerWriter(brain, lambda role: skills.load(f"audience-{role}").instructions)
